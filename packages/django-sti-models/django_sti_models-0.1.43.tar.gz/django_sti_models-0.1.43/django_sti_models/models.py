"""
Simple and robust Single Table Inheritance for Django.

This implementation provides clean STI with:
- Automatic table sharing for subclasses
- Type-aware querying and management
- Support for both concrete and abstract base classes
- Custom type field names
"""

from typing import Any, Dict, Optional, Type, TypeVar

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.manager import Manager

from .fields import TypeField

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
            type_field_name = self._get_type_field_name()
            if type_field_name:
                type_name = self.model_class.__name__
                queryset = queryset.filter(**{type_field_name: type_name})

        return queryset

    def _get_type_field_name(self) -> Optional[str]:
        """Get the type field name for this model."""
        if not self.model_class:
            return None

        # Check meta first
        if hasattr(self.model_class._meta, "type_field_name"):
            return self.model_class._meta.type_field_name

        # Look for TypeField in model or its bases
        try:
            for field in self.model_class._meta.get_fields():
                if isinstance(field, TypeField):
                    return field.name
        except Exception:
            # Fallback to default
            return "model_type"

        return None

    def create(self, **kwargs: Any) -> T:
        """Create a new instance with the correct type."""
        type_field_name = self._get_type_field_name()

        if type_field_name and type_field_name not in kwargs and self.model_class:
            kwargs[type_field_name] = self.model_class.__name__

        return super().create(**kwargs)


class TypedModelMeta(ModelBase):
    """Metaclass for STI models using Django's proxy model approach."""

    def __new__(
        mcs, name: str, bases: tuple, namespace: Dict[str, Any], **kwargs: Any
    ) -> Type[T]:
        """Create a new typed model class."""

        # Debug output
        print(f"🔍 TypedModelMeta.__new__ called for: {name}")
        print(
            f"   Bases: {[b.__name__ if hasattr(b, '__name__') else str(b) for b in bases]}"
        )

        # Handle Django app loading issues during setup
        try:
            from django.apps import apps

            if not apps.ready:
                # During Django setup, just create the class normally
                print(f"   ⚠️ Django apps not ready, creating normally")
                cls = super().__new__(mcs, name, bases, namespace, **kwargs)
                # Mark for post-initialization setup
                cls._needs_sti_setup = True
                return cls
        except Exception:
            # If apps aren't available, create normally
            print(f"   ⚠️ Django apps exception, creating normally")
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            cls._needs_sti_setup = True
            return cls

        # Check what fields are in the namespace
        from django_sti_models.fields import TypeField

        typefield_in_namespace = any(
            isinstance(v, TypeField) for v in namespace.values()
        )

        # Also check if TypeField is inherited from base classes
        typefield_in_inheritance = mcs._has_typefield_in_bases(bases)

        # Skip TypedModel itself
        if name == "TypedModel":
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            cls._meta.fields_from_subclasses = {}
            return cls

        # Skip abstract models
        Meta = namespace.get("Meta")
        if Meta and getattr(Meta, "abstract", False):
            return super().__new__(mcs, name, bases, namespace, **kwargs)

        # Check if this inherits from a TypedModel
        typed_base = mcs._find_typed_base(bases)
        print(
            f"   🔍 Found typed_base: {typed_base.__name__ if typed_base else 'None'}"
        )

        if typed_base:
            # This is an STI subclass - force proxy=True BEFORE class creation
            Meta = namespace.get("Meta", type("Meta", (), {}))
            if hasattr(Meta, "proxy") and getattr(Meta, "proxy", False):
                # User explicitly set proxy=True, treat as regular proxy
                return super().__new__(mcs, name, bases, namespace, **kwargs)

            # Extract declared fields from subclass
            from django.core.exceptions import FieldError
            from django.db.models.fields import Field

            declared_fields = dict(
                (field_name, field_obj)
                for field_name, field_obj in list(namespace.items())
                if isinstance(field_obj, Field)
            )

            # Validate and move fields to base class
            for field_name, field in list(declared_fields.items()):
                # Fields on STI subclasses must be nullable or have defaults
                if not (field.many_to_many or field.null or field.has_default()):
                    raise FieldError(
                        f"All fields defined on STI subclasses must be nullable "
                        f"or have a default value. For {name}.{field_name}, either:\n"
                        f"  - Add null=True (allows NULL in database)\n"
                        f"  - Add default='...' (provides default value)\n"
                        f"This prevents Multi-Table Inheritance (MTI) and ensures "
                        f"true Single Table Inheritance (STI)."
                    )

                # Check if field already exists on base class
                try:
                    existing_field = typed_base._meta.get_field(field_name)
                    # Check if it's exactly the same field
                    if existing_field.deconstruct()[1:] != field.deconstruct()[1:]:
                        raise ValueError(
                            f"Field '{field_name}' from '{name}' conflicts with "
                            f"existing field on '{typed_base.__name__}'"
                        )
                except Exception:
                    # Field doesn't exist, add it to base class
                    field.contribute_to_class(typed_base, field_name)

                # Remove field from subclass namespace
                namespace.pop(field_name)

            # Track fields added from subclasses
            if hasattr(typed_base._meta, "fields_from_subclasses"):
                typed_base._meta.fields_from_subclasses.update(declared_fields)

            # Force proxy=True for STI behavior
            Meta.proxy = True
            namespace["Meta"] = Meta

            # Create the class
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            cls._meta.fields_from_subclasses = {}
            mcs._setup_sti_subclass(cls, typed_base)
        else:
            # Create the class normally
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            cls._meta.fields_from_subclasses = {}

            # Check if this class has a TypeField (either declared or inherited)
            if typefield_in_namespace or typefield_in_inheritance:
                # This has a TypeField, making it a typed base
                mcs._setup_sti_base(cls)

        return cls

    @classmethod
    def _find_typed_base(mcs, bases: tuple) -> Optional[Type[T]]:
        """Find a concrete STI base class (not the abstract TypedModel)."""
        for base in bases:
            if hasattr(base, "__name__") and hasattr(base, "_meta"):
                # Skip the abstract TypedModel itself
                if base.__name__ == "TypedModel":
                    continue

                is_sti_base = getattr(base._meta, "is_sti_base", False)
                has_type_field = mcs._has_type_field(base)
                is_abstract = getattr(base._meta, "abstract", False)

                # If this base has a TypeField and is not abstract, it's our typed base
                if has_type_field and not is_abstract:
                    return base

                # If this base is already marked as an STI base, use it
                if is_sti_base:
                    return base

                # If this base is abstract but has a TypeField, look for concrete subclasses
                # that should inherit the type field
                if has_type_field and is_abstract:
                    # This is an abstract base with TypeField - the concrete class should
                    # inherit the type field and become the STI base
                    return None  # Let the concrete class become the base

                # Check if this base inherits from a TypedModel (for cases like AugendModel -> Business)
                if hasattr(base, "__bases__"):
                    for parent_base in base.__bases__:
                        if (
                            hasattr(parent_base, "__name__")
                            and parent_base.__name__ == "TypedModel"
                        ):
                            # This base inherits from TypedModel, so it should be our STI base
                            if not is_abstract:
                                return base
        return None

    @classmethod
    def _has_type_field(mcs, cls: Type) -> bool:
        """Check if a class has a TypeField."""
        if not hasattr(cls, "_meta"):
            return False

        try:
            fields = cls._meta.get_fields()
            for field in fields:
                if isinstance(field, TypeField):
                    return True
        except Exception:
            # Fallback to check declared fields
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name, None)
                if isinstance(attr, TypeField):
                    return True

        return False

    @classmethod
    def _has_typefield_in_bases(mcs, bases: tuple) -> bool:
        """Check if any base class has a TypeField (for inheritance detection)."""
        from django_sti_models.fields import TypeField

        for base in bases:
            if hasattr(base, "__name__") and hasattr(base, "_meta"):
                # Skip the abstract TypedModel itself
                if base.__name__ == "TypedModel":
                    continue

                # Check for TypeField in this base class using _meta.get_fields()
                # This handles both direct fields and inherited fields properly
                try:
                    fields = base._meta.get_fields()
                    for field in fields:
                        if isinstance(field, TypeField):
                            return True
                except Exception:
                    # Fallback: check for TypeField in this base class using dir()
                    for attr_name in dir(base):
                        if not attr_name.startswith("_"):  # Skip private attributes
                            attr = getattr(base, attr_name, None)
                            if isinstance(attr, TypeField):
                                return True

                # Recursively check base's bases for inherited TypeField
                if hasattr(base, "__bases__"):
                    if mcs._has_typefield_in_bases(base.__bases__):
                        return True

        return False

    @classmethod
    def _setup_sti_base(mcs, cls: Type[T]) -> None:
        """Set up a base STI model."""
        cls._meta.is_sti_base = True

        # Find type field name
        type_field_name = None
        try:
            for field in cls._meta.get_fields():
                if isinstance(field, TypeField):
                    type_field_name = field.name
                    break
        except Exception:
            # Fallback if get_fields() fails
            type_field_name = "model_type"

        if type_field_name:
            cls._meta.type_field_name = type_field_name
            cls._meta.typed_models = {cls.__name__: cls}

        # Set up manager and properly initialize it
        manager = TypedModelManager()
        manager.contribute_to_class(cls, "objects")
        cls.objects = manager

    @classmethod
    def _setup_sti_subclass(mcs, cls: Type[T], base: Type[T]) -> None:
        """Set up an STI subclass using Django's proxy model approach."""
        cls._meta.is_sti_subclass = True
        cls._meta.sti_base_model = base

        # Note: proxy=True is already set in __new__ before class creation
        # This ensures Django creates no separate table for the subclass

        # Register with base model
        if hasattr(base._meta, "typed_models"):
            base._meta.typed_models[cls.__name__] = cls

        # Share type field name
        if hasattr(base._meta, "type_field_name"):
            cls._meta.type_field_name = base._meta.type_field_name

        # Set up manager and properly initialize it
        manager = TypedModelManager()
        manager.contribute_to_class(cls, "objects")
        cls.objects = manager


class TypedModel(models.Model, metaclass=TypedModelMeta):
    """Simple base class for Single Table Inheritance (STI) models."""

    # Default type field - subclasses can override the field name
    model_type = TypeField()

    class Meta:
        abstract = True

    @classmethod
    def _setup_sti_post_init(cls):
        """Post-initialization setup for STI models after Django is ready."""
        if hasattr(cls, "_needs_sti_setup") and cls._needs_sti_setup:
            print(f"🔧 Setting up STI for {cls.__name__}")

            # Check if this inherits from a TypedModel
            from django_sti_models.models import TypedModelMeta

            typed_base = TypedModelMeta._find_typed_base(cls.__bases__)

            if typed_base:
                print(f"   📋 {cls.__name__} is STI subclass of {typed_base.__name__}")
                # Set up as STI subclass
                TypedModelMeta._setup_sti_subclass(cls, typed_base)
            else:
                # Check if this should be an STI base
                from django_sti_models.fields import TypeField

                has_type_field = any(
                    isinstance(field, TypeField) for field in cls._meta.get_fields()
                )
                if has_type_field:
                    print(f"   📋 {cls.__name__} is STI base")
                    TypedModelMeta._setup_sti_base(cls)

            # Clear the flag
            cls._needs_sti_setup = False

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the model, ensuring the type field is set."""
        # Set the type field to the current class name
        type_field_name = self.get_type_field_name()
        if type_field_name:
            setattr(self, type_field_name, self.__class__.__name__)

        super().save(*args, **kwargs)

    @classmethod
    def get_type_field_name(cls) -> str:
        """Get the name of the type field for this model."""
        if hasattr(cls._meta, "type_field_name"):
            return cls._meta.type_field_name
        return "model_type"

    @classmethod
    def get_all_types(cls) -> Dict[str, Type[T]]:
        """Get all registered types for this STI hierarchy."""
        if hasattr(cls._meta, "typed_models"):
            return cls._meta.typed_models.copy()
        return {}

    @classmethod
    def get_type_class(cls, type_name: str) -> Optional[Type[T]]:
        """Get the model class for a given type name."""
        if hasattr(cls._meta, "typed_models"):
            return cls._meta.typed_models.get(type_name)
        return None
