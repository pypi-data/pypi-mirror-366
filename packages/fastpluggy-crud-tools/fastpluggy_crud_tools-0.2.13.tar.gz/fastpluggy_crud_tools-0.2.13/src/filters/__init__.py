from typing import Any, Dict, List, Optional, Type, Union

import logging
from sqlalchemy import and_
from sqlalchemy.orm import DeclarativeMeta as ModelBase
from wtforms import Field, StringField
from wtforms.validators import Optional as OptionalValidator


logger = logging.getLogger(__name__)


class HeaderFilter:
    """
    Base class for header filters in table views.

    This class defines the interface that all filter types will implement.
    Each filter type will have its own rendering and filtering logic based on the field type.

    Attributes:
        field_name (str): The name of the field to filter on
        model (ModelBase): The SQLAlchemy model class
        label (str): The display label for the filter
        filter_type (str): The type of filter to apply (e.g., 'partial', 'exact', etc.)
    """

    def __init__(self, field_name: str, model: ModelBase, label: Optional[str] = None, 
                 filter_type: str = 'exact'):
        """
        Initialize a header filter.

        Args:
            field_name: The name of the field to filter on
            model: The SQLAlchemy model class
            label: The display label for the filter (defaults to capitalized field_name if not provided)
            filter_type: The type of filter to apply (defaults to 'exact')
        """
        self.field_name = field_name
        self.model = model
        self.label = label or field_name.replace('_', ' ').capitalize()
        self.filter_type = filter_type

    def render(self) -> Dict[str, Any]:
        """
        Render the filter as HTML.

        Returns:
            A dictionary with the HTML and any other data needed for rendering
        """
        return {
            'type': 'text',  # Default type, should be overridden by subclasses
            'field_name': self.field_name,
            'label': self.label,
            'filter_type': self.filter_type,
            'placeholder': f"Filter by {self.label}"
        }

    def apply_filter(self, query: Any, value: Any) -> Any:
        """
        Apply the filter to a SQLAlchemy query.

        Args:
            query: The SQLAlchemy query to filter
            value: The filter value from the request

        Returns:
            The filter condition or None if no filter should be applied
        """
        if not value:
            return None

        try:
            field = getattr(self.model, self.field_name)
            return self._apply_filter_implementation(field, value)
        except Exception as e:
            logger.error(f"Error applying filter for {self.field_name}: {str(e)}")
            return None

    def _apply_filter_implementation(self, field: Any, value: Any) -> Any:
        """
        Implementation of the filter application logic.

        This method should be overridden by subclasses to provide specific filtering logic.

        Args:
            field: The model field to filter on
            value: The filter value

        Returns:
            The filter condition
        """
        # Default implementation for exact match
        return field == value

    def get_filter_type(self) -> str:
        """
        Get the filter type for this field.

        Returns:
            The filter type (e.g., 'partial', 'exact', etc.)
        """
        return self.filter_type

    def get_form_field(self) -> Field:
        """
        Get the WTForms field for this filter.

        Returns:
            A WTForms field instance
        """
        return StringField(
            label=self.label,
            validators=[OptionalValidator()],
            render_kw={
                'placeholder': f"Filter by {self.label}",
                'class': 'form-control'
            }
        )


def apply_filters(query: Any, model: ModelBase, filters: Dict[str, Any], query_params: Dict[str, Any]) -> Any:
    """
    Apply filters to a SQLAlchemy query.

    Args:
        query: The SQLAlchemy query to filter
        model: The SQLAlchemy model class
        filters: A dictionary of HeaderFilter instances
        query_params: The query parameters from the request

    Returns:
        The filtered query
    """
    if not query or not filters or not query_params:
        return query

    try:
        filter_conditions = []

        for field_name, filter_instance in filters.items():
            if not isinstance(filter_instance, HeaderFilter):
                logger.warning(f"Filter for {field_name} is not a HeaderFilter instance")
                continue

            filter_value = query_params.get(field_name)
            if filter_value:
                try:
                    filter_condition = filter_instance.apply_filter(query, filter_value)
                    if filter_condition is not None:
                        filter_conditions.append(filter_condition)
                except Exception as e:
                    logger.error(f"Error applying filter for {field_name}: {str(e)}")

        # Apply filters to the query
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        return query
    except Exception as e:
        logger.error(f"Error applying filters: {str(e)}")
        return query
