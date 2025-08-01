from typing import Dict, Optional, Type, Any, List, Union
import logging

from sqlalchemy.orm import DeclarativeMeta as ModelBase

from . import HeaderFilter, logger
from .boolean_filter import BooleanHeaderFilter
from .datetime_filter import DateTimeHeaderFilter
from .enum_filter import EnumHeaderFilter
from .number_filter import NumberHeaderFilter
from .text_filter import TextHeaderFilter

# Import for type hints
try:
    from ..field_types import FieldType
except ImportError:
    pass


class FilterFactory:
    """
    Factory class for creating header filters based on field type.

    This class provides methods for creating filter instances based on field types
    and for creating filters for all fields in a model based on metadata.
    """

    # Type mappings for different field types
    TEXT_TYPES = ['string', 'text', 'varchar', 'char', 'nvarchar', 'nchar']
    NUMBER_TYPES = ['int', 'integer', 'float', 'decimal', 'numeric', 'bigint', 'smallint']
    BOOLEAN_TYPES = ['bool', 'boolean']
    DATETIME_TYPES = ['datetime', 'date', 'time', 'timestamp']
    ENUM_TYPES = ['enum', 'enumeration']

    # Custom filter registry for extensibility
    _custom_filters = {}

    @classmethod
    def register_custom_filter(cls, field_type: str, filter_class: Type[HeaderFilter]) -> None:
        """
        Register a custom filter class for a specific field type.

        Args:
            field_type: The type of the field
            filter_class: The filter class to use for this field type
        """
        cls._custom_filters[field_type.lower()] = filter_class
        logger.info(f"Registered custom filter for field type: {field_type}")

    @classmethod
    def create_filter(cls, field_name: str, model: ModelBase, field_type: str, 
                      label: Optional[str] = None, **kwargs) -> HeaderFilter:
        """
        Create a header filter based on field type.

        Args:
            field_name: The name of the field to filter on
            model: The SQLAlchemy model class
            field_type: The type of the field ('string', 'int', 'bool', etc.)
            label: The display label for the filter
            **kwargs: Additional arguments to pass to the filter constructor

        Returns:
            A HeaderFilter instance
        """
        if not field_name or not model:
            logger.error("Field name and model are required to create a filter")
            raise ValueError("Field name and model are required")

        try:
            field_type = field_type.lower() if field_type else 'string'

            # Check for custom filter first
            if field_type in cls._custom_filters:
                return cls._custom_filters[field_type](field_name, model, label, **kwargs)

            # Then check standard types
            if field_type in cls.TEXT_TYPES:
                return TextHeaderFilter(field_name, model, label, **kwargs)
            elif field_type in cls.NUMBER_TYPES:
                return NumberHeaderFilter(field_name, model, label, **kwargs)
            elif field_type in cls.BOOLEAN_TYPES:
                return BooleanHeaderFilter(field_name, model, label, **kwargs)
            elif field_type in cls.DATETIME_TYPES:
                return DateTimeHeaderFilter(field_name, model, label, **kwargs)
            elif field_type in cls.ENUM_TYPES:
                return EnumHeaderFilter(field_name, model, label, **kwargs)
            else:
                # Default to text filter for unknown types
                logger.warning(f"Unknown field type: {field_type}, defaulting to text filter")
                return TextHeaderFilter(field_name, model, label, **kwargs)
        except Exception as e:
            logger.error(f"Error creating filter for {field_name}: {str(e)}")
            # Return a basic text filter as fallback
            return TextHeaderFilter(field_name, model, label)

    @classmethod
    def create_filters_from_metadata(cls, model: ModelBase, 
                                    fields_metadata: Dict[str, Dict], 
                                    exclude_fields: Optional[List[str]] = None) -> Dict[str, HeaderFilter]:
        """
        Create header filters for all fields in a model based on metadata.

        Args:
            model: The SQLAlchemy model class
            fields_metadata: Metadata for the model fields
            exclude_fields: Fields to exclude from filtering

        Returns:
            A dictionary of field names to HeaderFilter instances
        """
        if not model or not fields_metadata:
            logger.error("Model and fields_metadata are required to create filters")
            return {}

        filters = {}
        exclude_fields = exclude_fields or []

        for field_name, metadata in fields_metadata.items():
            if field_name in exclude_fields:
                continue

            try:
                field_type = metadata.get('type', 'string')
                label = metadata.get('label', field_name.replace('_', ' ').capitalize())

                # Get additional filter options from metadata
                filter_options = metadata.get('filter_options', {})

                # Create filter based on field type
                filters[field_name] = cls.create_filter(
                    field_name=field_name,
                    model=model,
                    field_type=field_type,
                    label=label,
                    **filter_options
                )
            except Exception as e:
                logger.error(f"Error creating filter for {field_name}: {str(e)}")

        return filters

    @classmethod
    def create_filters_from_field_types(cls, model: ModelBase, 
                                      field_types: Dict[str, 'FieldType'],
                                      exclude_fields: Optional[List[str]] = None) -> Dict[str, HeaderFilter]:
        """
        Create header filters based on already detected field types.

        Args:
            model: The SQLAlchemy model class
            field_types: Dictionary of field names to FieldType instances
            exclude_fields: Fields to exclude from filtering

        Returns:
            A dictionary of field names to HeaderFilter instances
        """
        if not model or not field_types:
            logger.error("Model and field_types are required to create filters")
            return {}

        filters = {}
        exclude_fields = exclude_fields or []

        for field_name, field_type in field_types.items():
            if field_name in exclude_fields:
                continue

            try:
                # Get filter class from field type
                filter_class = field_type.get_filter_class()

                # Create filter instance
                filters[field_name] = filter_class(
                    field_name=field_name,
                    model=model,
                    label=getattr(field_type, 'label', field_name.replace('_', ' ').capitalize()),
                )
            except Exception as e:
                logger.error(f"Error creating filter for {field_name}: {str(e)}")

        return filters
