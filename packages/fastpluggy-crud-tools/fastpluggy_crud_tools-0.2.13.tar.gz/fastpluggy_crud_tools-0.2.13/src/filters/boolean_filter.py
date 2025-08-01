from typing import Any, Dict, Optional

from sqlalchemy.orm import DeclarativeMeta as ModelBase
from wtforms import SelectField
from wtforms.validators import Optional as OptionalValidator

from . import HeaderFilter


class BooleanHeaderFilter(HeaderFilter):
    """
    Header filter for boolean fields.

    This filter provides a dropdown with true/false/any options for filtering boolean fields.
    """

    def __init__(self, field_name: str, model: ModelBase, label: Optional[str] = None):
        """
        Initialize a boolean header filter.

        Args:
            field_name: The name of the field to filter on
            model: The SQLAlchemy model class
            label: The display label for the filter
        """
        super().__init__(field_name, model, label, filter_type='exact')

    def render(self) -> Dict[str, Any]:
        """
        Render the filter as HTML.

        Returns:
            A dictionary with the HTML and any other data needed for rendering
        """
        render_data = super().render()
        render_data.update({
            'type': 'boolean',
            'choices': [
                ('', 'Any'),
                ('true', 'Yes'),
                ('false', 'No')
            ]
        })
        return render_data

    def _apply_filter_implementation(self, field: Any, value: Any) -> Any:
        """
        Implementation of the filter application logic for boolean fields.

        Args:
            field: The model field to filter on
            value: The filter value

        Returns:
            The filter condition
        """
        if not value or value.lower() not in ['true', 'false']:
            return None

        is_true = value.lower() == 'true'
        return field == is_true

    def get_form_field(self) -> SelectField:
        """
        Get the WTForms field for this filter.

        Returns:
            A SelectField instance
        """
        return SelectField(
            label=self.label,
            choices=[
                ('', 'Any'),
                ('true', 'Yes'),
                ('false', 'No')
            ],
            validators=[OptionalValidator()],
            render_kw={
                'class': 'form-control'
            }
        )
