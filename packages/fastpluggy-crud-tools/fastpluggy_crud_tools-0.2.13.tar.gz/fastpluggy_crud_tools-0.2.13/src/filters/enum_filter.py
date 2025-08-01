from typing import Any, Dict, Optional, List, Tuple

from sqlalchemy.orm import DeclarativeMeta as ModelBase
from wtforms import SelectField
from wtforms.validators import Optional as OptionalValidator

from . import HeaderFilter, logger


class EnumHeaderFilter(HeaderFilter):
    """
    Header filter for enum fields.

    This filter provides a dropdown with enum values for filtering enum fields.
    """

    def __init__(self, field_name: str, model: ModelBase, label: Optional[str] = None,
                 choices: Optional[List[Tuple[str, str]]] = None):
        """
        Initialize an enum header filter.

        Args:
            field_name: The name of the field to filter on
            model: The SQLAlchemy model class
            label: The display label for the filter
            choices: List of (value, label) tuples for the dropdown options
        """
        super().__init__(field_name, model, label, filter_type='exact')
        self.choices = choices or []
        
        # If choices not provided, try to get them from the model field
        if not self.choices:
            try:
                field = getattr(model, field_name)
                if hasattr(field.property, 'columns') and len(field.property.columns) > 0:
                    column = field.property.columns[0]
                    if hasattr(column.type, 'enum_class') and column.type.enum_class:
                        enum_class = column.type.enum_class
                        self.choices = [(e.name, e.name) for e in enum_class]
                        logger.info(f"Detected enum choices for {field_name}: {self.choices}")
            except Exception as e:
                logger.warning(f"Could not detect enum choices for {field_name}: {str(e)}")

    def render(self) -> Dict[str, Any]:
        """
        Render the filter as HTML.

        Returns:
            A dictionary with the HTML and any other data needed for rendering
        """
        render_data = super().render()
        render_data.update({
            'type': 'enum',
            'choices': [('', 'Any')] + self.choices
        })
        return render_data

    def _apply_filter_implementation(self, field: Any, value: Any) -> Any:
        """
        Implementation of the filter application logic for enum fields.

        Args:
            field: The model field to filter on
            value: The filter value

        Returns:
            The filter condition
        """
        if not value:
            return None

        # Simple exact match for enum values
        return field == value

    def get_form_field(self) -> SelectField:
        """
        Get the WTForms field for this filter.

        Returns:
            A SelectField instance
        """
        return SelectField(
            label=self.label,
            choices=[('', 'Any')] + self.choices,
            validators=[OptionalValidator()],
            render_kw={
                'class': 'form-control'
            }
        )