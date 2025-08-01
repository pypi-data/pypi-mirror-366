import importlib
import inspect
from typing import Dict
from typing import Type, List

from fastapi import APIRouter, Request, Depends
from fastpluggy_plugin.crud_tools.config import CrudConfig
from loguru import logger

from fastpluggy.core.database import Base
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.models_tools.sqlalchemy import ModelToolsSQLAlchemy
from fastpluggy.core.tools.inspect_tools import get_module
from fastpluggy.core.view_builer.components.model import ModelView
from fastpluggy.core.widgets import AutoLinkWidget
from fastpluggy.core.widgets import TableWidget

crud_admin_view_router = APIRouter(prefix='/models', tags=["front_action"])


def import_base(path: str) -> Type:
    """Dynamically import a Base class given its full import path."""
    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_models_from_base(base: Type) -> List[Type]:
    """
    Pull all mapped classes out of a SQLAlchemy declarative Base
    (using the _decl_class_registry).
    """
    base_cls = import_base(base)
    mappers = getattr(base_cls, "registry", []).mappers
    result = []
    module_name = '__autodetected__'
    for mapper in mappers:  # type: ignore[attr-defined]
        cls = mapper.class_  # type: ignore[attr-defined]
        from ..router.crud import get_admin_instance
        admin = get_admin_instance(cls.__name__, default_crud_class=False)
        result.append({
            "module_name": module_name,
            "model_name": cls.__name__,
            "registered": admin is not None,
            "admin_class": admin.__class__.__name__ if admin else None
        })
    return result


def get_sqlalchemy_models(module_name: str) -> list[type]:
    module = get_module(f"{module_name}.models", reload=False)
    return [
        obj for name, obj in inspect.getmembers(module)
        if inspect.isclass(obj) and ModelToolsSQLAlchemy.is_sqlalchemy(obj) and obj is not Base
    ]


def get_admin_model_status(module_name: str) -> List[Dict[str, str]]:
    result = []
    models = get_sqlalchemy_models(module_name)
    for model in models:
        from ..router.crud import get_admin_instance
        admin = get_admin_instance(model.__name__, default_crud_class=False)
        result.append({
            "module_name": module_name,
            "model_name": model.__name__,
            "registered": admin is not None,
            "admin_class": admin.__class__.__name__ if admin else None
        })

    return result


@menu_entry(label="Models", type='admin')
@crud_admin_view_router.api_route("", methods=["GET", "POST"], name="list_models")
async def list_models(request: Request, view_builder=Depends(get_view_builder),
                      fast_pluggy=Depends(get_fastpluggy)):
    items_admin = []
    for module_name in fast_pluggy.module_manager.modules.values():
        try:
            admin = get_admin_model_status(module_name.package_name, )
            items_admin.extend(admin)
        except Exception as e:
            logger.exception(e)

    custom_base = CrudConfig().base_sqlalchemy_model
    if custom_base is not None:
        admin = get_models_from_base(custom_base)
        items_admin.extend(admin)

    from ..crud_link_helper import CrudLinkHelper
    from ..schema import CrudAction
    items = [
        TableWidget(
            data=items_admin,
            title="Crud Models",
            links=[
                CrudLinkHelper.get_crud_link(model='<model_name>', action=CrudAction.LIST),
                CrudLinkHelper.get_crud_link(model='<model_name>', action=CrudAction.CREATE),
                AutoLinkWidget(route_name='inspect_admin', param_inputs={'model_name': '<model_name>'}),
            ]
        )
    ]

    return view_builder.generate(
        request,
        title="List of models",
        widgets=items,
    )


@crud_admin_view_router.api_route("/inspect/{model_name}", methods=["GET", "POST"], name="inspect_admin")
async def inspect_admin(model_name: str, request: Request, view_builder=Depends(get_view_builder),
                        fast_pluggy=Depends(get_fastpluggy)):
    """
    Inspect the admin configuration for a model.

    This route shows detailed information about how field types, filters, and other
    configurations are detected and configured for each CRUD action.
    """
    from ..router.crud import get_admin_instance
    from ..schema import CrudAction
    from fastpluggy_plugin.ui_tools.extra_widget.display.card import CardWidget
    from fastpluggy_plugin.ui_tools.extra_widget.display.code import CodeWidget

    from fastpluggy.core.widgets import TableWidget

    # Get the admin instance for this model
    admin = get_admin_instance(model_name)
    if not admin:
        return view_builder.generate(
            request,
            title=f"Admin inspection for {model_name}",
            widgets=[CardWidget(
                title="Error",
                content=f"No admin found for model {model_name}"
            )]
        )

    # Get model metadata
    model_class = admin.model
    model_metadata = {}
    try:
        from fastpluggy.core.models_tools.shared import ModelToolsShared
        model_metadata = ModelToolsShared.get_model_metadata(model=model_class)
    except Exception as e:
        logger.exception(e)

    # Create widgets to display the information
    items = []

    # Model information
    model_info = {
        "Model Name": model_class.__name__,
        "Admin Class": admin.__class__.__name__,
        "Primary Key": admin.primary_key_field,
        "Table Name": getattr(model_class, "__tablename__", "Unknown"),
    }

    items.append(ModelView(
        title="Model Information",
        model=model_info,
    ))

    # Field types for each CRUD action
    for action in [CrudAction.CREATE, CrudAction.EDIT, CrudAction.LIST, CrudAction.VIEW]:
        field_types = admin.configure_fields(context=action)
        field_info = []

        for name, field_type in field_types.items():
            field_class = field_type.__class__.__name__
            field_meta = model_metadata.get(name, {})

            # Determine how the field type was detected
            detection_logic = "Unknown"
            if name == "id" or field_meta.get("primary_key", False):
                detection_logic = "Primary key or field named 'id'"
            elif field_meta.get("enum_class"):
                detection_logic = f"Enum class: {field_meta.get('enum_class')}"
            elif field_meta.get("type") == "datetime":
                detection_logic = "Field type: datetime"
            elif field_meta.get("type") == "string":
                detection_logic = "Field type: string"
            elif field_meta.get("type") == "text":
                detection_logic = "Field type: text"
            elif field_meta.get("type") == "int":
                detection_logic = "Field type: int"
            elif field_meta.get("type") in ["bool", "boolean"]:
                detection_logic = "Field type: boolean"
            elif field_meta.get("type") == "enum":
                detection_logic = "Field type: enum"
            elif field_meta.get("type") == "timedelta":
                detection_logic = "Field type: timedelta"
            else:
                detection_logic = f"Default fallback for type: {field_meta.get('type', 'unknown')}"

            field_info.append({
                "Field Name": name,
                "Field Type": field_class,
                "Detection Logic": detection_logic,
                "Required": field_meta.get("required", False),
                "Default": field_meta.get("default", None),
                "Help Text": field_meta.get("description", None),
                "Primary Key": field_meta.get("primary_key", False),
                "Readonly": field_meta.get("readonly", False),
            })

        items.append(TableWidget(
            title=f"Field Types for {action.title()}",
            data=field_info,
        ))

    # Filters for LIST action
    filters = admin.get_list_filters(context=CrudAction.LIST)
    field_types = admin.configure_fields(context=CrudAction.LIST)
    filter_info = []

    for name, filter_instance in filters.items():
        filter_class = filter_instance.__class__.__name__
        filter_type = getattr(filter_instance, "filter_type", "Unknown")
        field_type = field_types.get(name, None)
        field_type_name = field_type.__class__.__name__ if field_type else "Unknown"

        filter_info.append({
            "Field Name": name,
            "Filter Type": filter_class,
            "Filter Mode": filter_type,
            "Field Type": field_type_name,
        })

    items.append(TableWidget(
        title="Filters for LIST",
        data=filter_info,
    ))

    # Excluded fields for each action
    excluded_fields = {}
    for action in [CrudAction.CREATE, CrudAction.EDIT, CrudAction.LIST, CrudAction.VIEW]:
        excluded_fields[action.name] = admin.get_excluded_fields(context=action)

    items.append(TableWidget(
        title="Excluded Fields by Action",
        data=[excluded_fields],
    ))

    # Field callbacks
    callbacks = admin.get_fields_callbacks(context=CrudAction.LIST)
    callback_info = []

    for name, callback in callbacks.items():
        callback_info.append({
            "Field Name": name,
            "Callback": callback.__name__ if callable(callback) else str(callback),
        })

    if callback_info:
        items.append(TableWidget(
            title="Field Rendering Callbacks",
            data=callback_info,
        ))

    # JavaScript dependencies
    js_scripts = admin.get_js_scripts(request=request, context=CrudAction.LIST)
    if js_scripts:
        items.append(CodeWidget(
            title="JavaScript Dependencies",
            code="\n".join(js_scripts),
            language="javascript"
        ))

    return view_builder.generate(
        request,
        title=f"Admin inspection for {model_name}",
        widgets=items,
    )
