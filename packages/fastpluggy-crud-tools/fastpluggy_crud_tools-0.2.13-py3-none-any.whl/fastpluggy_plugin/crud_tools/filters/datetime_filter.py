from typing import Any, Dict, Optional

from sqlalchemy.orm import DeclarativeMeta as ModelBase
from wtforms import DateTimeField
from wtforms.validators import Optional as OptionalValidator

from . import HeaderFilter, logger


class DateTimeHeaderFilter(HeaderFilter):
    """
    Header filter for datetime fields.

    This filter provides a datetime input for filtering datetime fields with options for
    equal, greater than, less than, and between.
    """

    def __init__(self, field_name: str, model: ModelBase, label: Optional[str] = None, 
                 filter_type: str = 'exact'):
        """
        Initialize a datetime header filter.

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
        render_data['type'] = 'datetime'
        return render_data

    def _apply_filter_implementation(self, field: Any, value: Any) -> Any:
        """
        Implementation of the filter application logic for datetime fields.

        Args:
            field: The model field to filter on
            value: The filter value

        Returns:
            The filter condition
        """
        try:
            from datetime import datetime

            # For 'between', we expect a range like "2023-01-01 00:00:00-2023-01-31 23:59:59"
            if self.filter_type == 'between' and '-' in value:
                start_str, end_str = value.split('-', 1)
                try:
                    start_date = datetime.fromisoformat(start_str.strip()) if start_str.strip() else None
                    end_date = datetime.fromisoformat(end_str.strip()) if end_str.strip() else None

                    if start_date is not None and end_date is not None:
                        return field.between(start_date, end_date)
                    elif start_date is not None:
                        return field >= start_date
                    elif end_date is not None:
                        return field <= end_date
                except ValueError:
                    logger.warning(f"Invalid datetime format for {self.field_name}: {value}")
                    return None

            # For single datetime value
            date_value = datetime.fromisoformat(value)

            if self.filter_type == 'exact':
                return field == date_value
            elif self.filter_type == 'gt':
                return field > date_value
            elif self.filter_type == 'lt':
                return field < date_value
            else:
                # Default to exact match
                return field == date_value
        except ValueError:
            logger.warning(f"Invalid datetime format for {self.field_name}: {value}")
            return None
        except Exception as e:
            logger.error(f"Error applying datetime filter for {self.field_name}: {str(e)}")
            return None

    def get_form_field(self) -> DateTimeField:
        """
        Get the WTForms field for this filter.

        Returns:
            A DateTimeField instance
        """
        return DateTimeField(
            label=self.label,
            validators=[OptionalValidator()],
            render_kw={
                'placeholder': f"Filter by {self.label}",
                'class': 'form-control'
            }
        )