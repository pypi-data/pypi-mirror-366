from typing import Optional, Union, Dict, Any, List

from sqlalchemy.orm import DeclarativeMeta as ModelBase, Session

from ..filters import HeaderFilter, apply_filters
from ..filters.filter_factory import FilterFactory
from fastpluggy.core.models_tools.shared import ModelToolsShared
from fastpluggy.core.view_builer.components.table_model import TableModelView
from fastpluggy.core.widgets import RequestParamsMixin, BaseButtonWidget


class FilteredTableModelWidget(TableModelView, RequestParamsMixin):
    """
    Extension of TableModelView that supports header filters based on field types.
    """

    widget_type = "filtered_table"
    template_name = "crud_tools/widgets/data/filtered_table.html.j2"
    macro_name = "render_filtered_table"
    render_method = "macro"

    # Widget registration attributes
    category = "data"
    description = "Table with header filters based on field types"
    icon = "table-filter"

    def __init__(self, model: ModelBase,
                 filters: Optional[Union[Dict[str, Any], Dict[str, Dict]]] = None,
                 default_sort: Optional[Dict[str, str]] = None,
                 limits: int = 100,
                 db: Session = None,
                 pagination_options: Optional[Dict[str, Any]] = None,
                 links: Optional[List[Union[BaseButtonWidget, Dict[str, Any]]]] = None,
                 enable_header_filters: bool = True,
                 **kwargs):
        """
        Initialize a filtered table model view.

        Args:
            model: The SQLAlchemy model class
            filters: Filters to apply to the query. If these are HeaderFilter instances,
                    they will be used for header filtering. Otherwise, they will be used
                    for base filtering only.
            default_sort: Default sort order
            limits: Maximum number of items per page
            db: SQLAlchemy session
            pagination_options: Pagination options
            links: Links to display for each row
            enable_header_filters: Whether to enable header filters
            **kwargs: Additional arguments to pass to TableModelView
        """
        # Check if filters are HeaderFilter instances
        self.header_filters = {}
        base_filters = None

        if filters:
            if all(isinstance(f, HeaderFilter) for f in filters.values()):
                # If all filters are HeaderFilter instances, store them for header filtering
                # but don't pass them to the base class
                self.header_filters = filters
            else:
                # Otherwise, pass the filters to the base class for regular filtering
                base_filters = filters

        super().__init__(
            model=model,
            filters=base_filters,  # Only pass non-HeaderFilter filters to the base class
            default_sort=default_sort,
            limits=limits,
            db=db,
            pagination_options=pagination_options,
            links=links,
            **kwargs
        )
        self.enable_header_filters = enable_header_filters

        # Initialize header filters if enabled and not already set
        if self.enable_header_filters and not self.header_filters:
            self._init_header_filters()

    def _init_header_filters(self):
        """
        Initialize header filters based on field types.
        """
        # Get metadata for all fields in the model
        fields_metadata = ModelToolsShared.get_model_metadata(
            model=self.model,
            exclude_fields=self.exclude_fields
        )

        # Create filters for each field
        self.header_filters = FilterFactory.create_filters_from_metadata(
            model=self.model,
            fields_metadata=fields_metadata,
            exclude_fields=self.exclude_fields
        )

    def apply_filters_from_query(self, query, model, query_params, search_params):
        """
        Apply filters from query parameters to a SQLAlchemy query.

        This method extends the base implementation to support header filters.

        Args:
            query: The SQLAlchemy query to modify
            model: The SQLAlchemy model class
            query_params: Query parameters from the request
            search_params: A dictionary defining the fields and their types for filtering

        Returns:
            The modified query with filters applied
        """
        # First apply the base filters
        query = super().apply_filters_from_query(query, model, query_params, search_params)

        # Then apply header filters if enabled
        if self.enable_header_filters and self.header_filters:
            query = apply_filters(query, model, self.header_filters, query_params)

        return query

    def get_context_data(self):
        """
        Get context data for rendering the table.

        This method extends the base implementation to include header filters.

        Returns:
            A dictionary with context data for rendering the table
        """
        context = super().get_context_data()

        # Add header filters to context if enabled
        if self.enable_header_filters and self.header_filters:
            header_filters_data = {}
            for field_name, filter_instance in self.header_filters.items():
                header_filters_data[field_name] = filter_instance.render()

            context['header_filters'] = header_filters_data
            context['header_filters_enabled'] = True

            # Add table attributes if needed
            context['table_attrs'] = context.get('table_attrs', {})

        return context
