from typing import Any, Dict, Optional

from sqlalchemy.orm import DeclarativeMeta as ModelBase
from wtforms import IntegerField
from wtforms.validators import Optional as OptionalValidator

from . import HeaderFilter, logger


class NumberHeaderFilter(HeaderFilter):
    """
    Header filter for numeric fields.

    This filter provides a numeric input for filtering numeric fields with options for
    equal, greater than, less than, and between.
    """

    def __init__(self, field_name: str, model: ModelBase, label: Optional[str] = None, 
                 filter_type: str = 'exact'):
        """
        Initialize a number header filter.

        Args:
            field_name: The name of the field to filter on
            model: The SQLAlchemy model class
            label: The display label for the filter
            filter_type: The type of filter to apply ('exact', 'gt', 'lt', 'between')
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
        render_data['type'] = 'number'
        return render_data

    def _apply_filter_implementation(self, field: Any, value: Any) -> Any:
        """
        Implementation of the filter application logic for numeric fields.

        Args:
            field: The model field to filter on
            value: The filter value

        Returns:
            The filter condition
        """
        try:
            # Convert value to int for numeric comparison
            int_value = int(value)

            if self.filter_type == 'exact':
                return field == int_value
            elif self.filter_type == 'gt':
                return field > int_value
            elif self.filter_type == 'lt':
                return field < int_value
            elif self.filter_type == 'between':
                # For 'between', we expect a range like "10-20"
                if '-' in value:
                    min_val, max_val = value.split('-', 1)
                    try:
                        min_val = int(min_val) if min_val else None
                        max_val = int(max_val) if max_val else None

                        if min_val is not None and max_val is not None:
                            return field.between(min_val, max_val)
                        elif min_val is not None:
                            return field >= min_val
                        elif max_val is not None:
                            return field <= max_val
                    except ValueError:
                        logger.warning(f"Invalid range format for {self.field_name}: {value}")

                # Default to exact match if range format is invalid
                return field == int_value

            # Default to exact match
            return field == int_value
        except ValueError:
            # If value can't be converted to int, return None (no filter)
            logger.warning(f"Cannot convert value to int for {self.field_name}: {value}")
            return None

    def get_form_field(self) -> IntegerField:
        """
        Get the WTForms field for this filter.

        Returns:
            An IntegerField instance
        """
        return IntegerField(
            label=self.label,
            validators=[OptionalValidator()],
            render_kw={
                'placeholder': f"Filter by {self.label}",
                'class': 'form-control'
            }
        )
