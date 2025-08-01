from typing import Any, Dict, Optional

from sqlalchemy.orm import DeclarativeMeta as ModelBase
from wtforms import StringField
from wtforms.validators import Optional as OptionalValidator

from . import HeaderFilter


class TextHeaderFilter(HeaderFilter):
    """
    Header filter for text fields.

    This filter provides a text input for filtering text fields with options for
    exact match, contains, starts with, and ends with.
    """

    def __init__(self, field_name: str, model: ModelBase, label: Optional[str] = None, 
                 filter_type: str = 'partial'):
        """
        Initialize a text header filter.

        Args:
            field_name: The name of the field to filter on
            model: The SQLAlchemy model class
            label: The display label for the filter
            filter_type: The type of filter to apply ('partial', 'exact', 'startswith', 'endswith')
        """
        super().__init__(field_name, model, label, filter_type)

    def render(self) -> Dict[str, Any]:
        """
        Render the filter as HTML.

        Returns:
            A dictionary with the HTML and any other data needed for rendering
        """
        # Use the base class implementation but override the type
        render_data = super().render()
        render_data['type'] = 'text'
        return render_data

    def _apply_filter_implementation(self, field: Any, value: Any) -> Any:
        """
        Implementation of the filter application logic for text fields.

        Args:
            field: The model field to filter on
            value: The filter value

        Returns:
            The filter condition
        """
        if self.filter_type == 'partial':
            return field.like(f"%{value}%")
        elif self.filter_type == 'exact':
            return field == value
        elif self.filter_type == 'startswith':
            return field.like(f"{value}%")
        elif self.filter_type == 'endswith':
            return field.like(f"%{value}")

        # Default to partial match
        return field.like(f"%{value}%")

    def get_form_field(self) -> StringField:
        """
        Get the WTForms field for this filter.

        Returns:
            A StringField instance
        """
        # Use the base class implementation which already returns a StringField
        return super().get_form_field()
