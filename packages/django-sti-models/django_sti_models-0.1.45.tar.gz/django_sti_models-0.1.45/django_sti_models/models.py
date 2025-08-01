"""
Simple and robust Single Table Inheritance for Django.

This implementation provides clean STI with:
- Automatic table sharing for subclasses
- Type-aware querying and management
- Support for both concrete and abstract base classes
- Uses Django's ContentType system for reliable type tracking
"""

from typing import Any, Dict, Optional, Type, TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.manager import Manager

T = TypeVar("T", bound="TypedModel")


class TypedModelManager(Manager[T]):
    """Simple manager for TypedModel with type-aware querying."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.model_class: Optional[Type[T]] = None

    def contribute_to_class(self, model: Type[T], name: str) -> None:
        """Called when manager is added to a model class."""
        super().contribute_to_class(model, name)
        self.model_class = model
        # Ensure the model property is also set for Django's manager
        self.model = model

    def get_queryset(self) -> models.QuerySet[T]:
        """Get a queryset, filtered by type for subclasses."""
        queryset = super().get_queryset()

        # If this is a subclass of a TypedModel, filter by type
        if (
            self.model_class
            and hasattr(self.model_class, "_meta")
            and getattr(self.model_class._meta, "is_sti_subclass", False)
        ):
            # Use ContentType to filter by the actual model class
            content_type = ContentType.objects.get_for_model(self.model_class)
            queryset = queryset.filter(polymorphic_ctype=content_type)

        return queryset

    def create(self, **kwargs: Any) -> T:
        """Create a new instance with the correct type."""
        # Set the ContentType automatically
        if "polymorphic_ctype" not in kwargs and self.model_class:
            content_type = ContentType.objects.get_for_model(self.model_class)
            kwargs["polymorphic_ctype"] = content_type

        return super().create(**kwargs)


class TypedModelMeta(ModelBase):
    """Metaclass for STI models using Django's ContentType system."""

    def __new__(
        mcs, name: str, bases: tuple, namespace: Dict[str, Any], **kwargs: Any
    ) -> Type[T]:
        """Create a new typed model class."""

        # Create the class normally - let Django handle inheritance
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Connect to class_prepared signal to set up STI after Django is done
        models.signals.class_prepared.connect(mcs._setup_sti_after_prepared, sender=cls)

        return cls

    @classmethod
    def _setup_sti_after_prepared(mcs, sender: Type[T], **kwargs: Any) -> None:
        """Set up STI after Django has prepared the model class."""

        # Skip abstract models - they don't create tables
        if getattr(sender._meta, "abstract", False):
            return

        # Skip TypedModel itself
        if sender.__name__ == "TypedModel":
            return

        # Check if this model inherits from TypedModel
        if mcs._inherits_from_typed_model(sender):
            # This is an STI model
            mcs._setup_sti_model(sender)

    @classmethod
    def _inherits_from_typed_model(mcs, cls: Type[T]) -> bool:
        """Check if a class inherits from TypedModel."""
        for base in cls.__bases__:
            if base.__name__ == "TypedModel":
                return True
            if hasattr(base, "__bases__") and mcs._inherits_from_typed_model(base):
                return True
        return False

    @classmethod
    def _setup_sti_model(mcs, cls: Type[T]) -> None:
        """Set up an STI model."""
        cls._meta.is_sti_model = True

        # Set up manager and properly initialize it
        manager = TypedModelManager()
        manager.contribute_to_class(cls, "objects")
        cls.objects = manager


class TypedModel(models.Model, metaclass=TypedModelMeta):
    """Base class for Single Table Inheritance (STI) models using ContentType."""

    # Use ContentType instead of a simple string field
    polymorphic_ctype = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=False,
        verbose_name="polymorphic type",
        related_name="polymorphic_%(app_label)s.%(class)s_set+",
    )

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the model, ensuring the ContentType is set."""
        # Set the ContentType to the current class if not already set
        if not self.polymorphic_ctype_id:
            self.polymorphic_ctype = ContentType.objects.get_for_model(self.__class__)

        super().save(*args, **kwargs)

    def get_real_instance_class(self) -> Optional[Type[T]]:
        """Get the real class of this instance."""
        if not self.polymorphic_ctype_id:
            return None

        try:
            return self.polymorphic_ctype.model_class()
        except Exception:
            return None

    @classmethod
    def get_type_class(cls, type_name: str) -> Optional[Type[T]]:
        """Get the model class for a given type name."""
        try:
            content_type = ContentType.objects.get(model=type_name.lower())
            return content_type.model_class()
        except ContentType.DoesNotExist:
            return None
