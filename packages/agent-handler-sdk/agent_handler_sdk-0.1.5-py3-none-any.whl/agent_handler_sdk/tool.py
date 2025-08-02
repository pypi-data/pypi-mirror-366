import inspect
from typing import (
    Callable,
    Optional,
    List,
    Any,
    Dict,
    get_type_hints,
    get_origin,
    get_args,
    TypeVar,
    cast,
)
from pydantic import BaseModel, create_model
from .registry import ConnectorRegistry
from .utils import convert_type_hint_to_json_schema


F = TypeVar("F", bound=Callable[..., Any])


def tool(
    name: Optional[str] = None,
    desc: str = "",
    tags: Optional[List[str]] = None,
) -> Callable[[F], F]:
    """
    Decorator to register a function as a tool.

    Args:
        name: Optional name for the tool. Defaults to the function name.
        desc: Description of the tool.
        tags: Optional list of tags for the tool.

    Returns:
        The decorated function.
    """
    tags_list: List[str] = tags or []

    def decorator(fn: F) -> F:
        sig = inspect.signature(fn)
        type_hints = get_type_hints(fn)

        # Create a clean schema structure
        schema: Dict[str, Any] = {"type": "object", "properties": {}}
        required: List[str] = []

        # Process each parameter
        for param_name, param in sig.parameters.items():
            # Get the type hint
            type_hint = type_hints.get(param_name, Any)

            # Determine if the parameter is required
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

            # Convert type hint to JSON schema
            schema["properties"][param_name] = convert_type_hint_to_json_schema(type_hint)

        # If there are required fields, add them to the schema
        if required:
            schema["required"] = required

        # Check if the function is async
        is_async = inspect.iscoroutinefunction(fn)

        # Create a wrapper function that converts dictionaries to Pydantic models
        if is_async:
            # Type ignore for the conditional function variants issue
            async def wrapped_fn(**kwargs: Any) -> Any:  # type: ignore
                converted_kwargs = convert_kwargs(kwargs, type_hints)
                return await fn(**converted_kwargs)

        else:

            def wrapped_fn(**kwargs: Any) -> Any:  # type: ignore
                converted_kwargs = convert_kwargs(kwargs, type_hints)
                return fn(**converted_kwargs)

        # Preserve the original function's signature and docstring
        wrapped_fn.__name__ = fn.__name__
        wrapped_fn.__doc__ = fn.__doc__
        wrapped_fn.__annotations__ = fn.__annotations__

        tool_name = name or fn.__name__
        ConnectorRegistry.register_tool(
            name=tool_name,
            description=desc,
            fn=wrapped_fn,
            param_schema=schema,
            tags=tags_list,
        )
        return fn

    return decorator


def convert_kwargs(kwargs: Dict[str, Any], type_hints: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to convert dictionaries to Pydantic models based on type hints."""
    converted_kwargs: Dict[str, Any] = {}
    for param_name, param_value in kwargs.items():
        if param_name in type_hints:
            param_type = type_hints[param_name]
            # Check if it's a Pydantic model
            if (
                isinstance(param_value, dict)
                and hasattr(param_type, "model_validate")
                and issubclass(param_type, BaseModel)
            ):
                # Convert dict to Pydantic model
                converted_kwargs[param_name] = param_type.model_validate(param_value)
            # Handle List[PydanticModel]
            elif (
                isinstance(param_value, list)
                and get_origin(param_type) is list
                and len(get_args(param_type)) > 0
                and hasattr(get_args(param_type)[0], "model_validate")
                and issubclass(get_args(param_type)[0], BaseModel)
            ):
                model_class = get_args(param_type)[0]
                converted_kwargs[param_name] = [
                    model_class.model_validate(item) if isinstance(item, dict) else item for item in param_value
                ]
            else:
                converted_kwargs[param_name] = param_value
        else:
            converted_kwargs[param_name] = param_value

    return converted_kwargs
