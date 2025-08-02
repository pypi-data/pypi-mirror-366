from typing import Any, Dict, List, Optional, Union, get_type_hints, get_origin, get_args, Type
from enum import Enum
from pydantic import BaseModel


def convert_type_hint_to_json_schema(type_hint: Any) -> Dict[str, Any]:
    """
    Convert a Python type hint to a JSON schema representation.
    Handles primitive types, lists, tuples, unions, optional types, and Pydantic models.
    """
    # Handle None type
    if type_hint is type(None):
        return {"type": "null"}

    # Handle primitive types
    if type_hint in (int, float, str, bool):
        return _convert_primitive_type(type_hint)

    # Handle Pydantic models
    if hasattr(type_hint, "model_json_schema") and issubclass(type_hint, BaseModel):
        return _convert_pydantic_type(type_hint)

    # Handle container types (list, tuple, dict)
    origin = get_origin(type_hint)
    if origin is list:
        return _convert_list_type(type_hint)
    elif origin is tuple:
        return _convert_tuple_type(type_hint)
    elif origin is dict:
        return _convert_dict_type(type_hint)

    # Handle Union and Optional types
    if origin is Union:
        return _convert_union_type(type_hint)
    if origin is Optional:
        return _convert_optional_type(type_hint)

    # Handle Enum types
    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        return _convert_enum_type(type_hint)

    # Default to string for unknown types
    return {"type": "string"}


def _convert_primitive_type(type_hint: Type) -> Dict[str, Any]:
    """Convert primitive Python types to JSON schema types."""
    type_mapping = {
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        bool: {"type": "boolean"},
    }
    return type_mapping.get(type_hint, {"type": "string"})


def _convert_list_type(type_hint: Any) -> Dict[str, Any]:
    """Convert Python list type to JSON schema array."""
    item_type = get_args(type_hint)[0] if get_args(type_hint) else Any
    return {"type": "array", "items": convert_type_hint_to_json_schema(item_type)}


def _convert_tuple_type(type_hint: Any) -> Dict[str, Any]:
    """Convert Python tuple type to JSON schema array with constraints."""
    args = get_args(type_hint)
    if not args:
        return {"type": "array"}

    # Handle tuple with variable args (Tuple[int, ...])
    if len(args) == 2 and args[1] is Ellipsis:
        return {"type": "array", "items": convert_type_hint_to_json_schema(args[0])}

    # Handle fixed-length tuples
    return {
        "type": "array",
        "minItems": len(args),
        "maxItems": len(args),
        "items": [convert_type_hint_to_json_schema(arg) for arg in args],
    }


def _convert_dict_type(type_hint: Any) -> Dict[str, Any]:
    """Convert Python dict type to JSON schema object."""
    args = get_args(type_hint)
    key_type = args[0] if len(args) > 0 else Any
    value_type = args[1] if len(args) > 1 else Any

    # Only str keys are supported in JSON
    if key_type is not str and key_type is not Any:
        key_type = str

    return {"type": "object", "additionalProperties": convert_type_hint_to_json_schema(value_type)}


def _convert_union_type(type_hint: Any) -> Dict[str, Any]:
    """Convert Python Union type to JSON schema anyOf."""
    union_args = get_args(type_hint)

    # Handle Optional (Union[Type, None])
    if len(union_args) == 2 and type(None) in union_args:
        return _convert_optional_union(union_args)

    # Handle regular Union types
    return {"anyOf": [convert_type_hint_to_json_schema(arg) for arg in union_args]}


def _convert_optional_union(union_args: tuple) -> Dict[str, Any]:
    """Handle Optional as Union[Type, None]."""
    # Get the non-None type
    actual_type = union_args[0] if union_args[1] is type(None) else union_args[1]
    return convert_type_hint_to_json_schema(actual_type)


def _convert_optional_type(type_hint: Any) -> Dict[str, Any]:
    """Convert Python Optional type to JSON schema."""
    actual_type = get_args(type_hint)[0]
    return convert_type_hint_to_json_schema(actual_type)


def _convert_enum_type(type_hint: Type[Enum]) -> Dict[str, Any]:
    """Convert Python Enum type to JSON schema enum."""
    enum_values = [item.value for item in type_hint]
    return {"enum": enum_values}


def _convert_pydantic_type(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a flattened JSON schema without references.
    """
    # Get the model schema
    schema = model.model_json_schema()

    # Create a flattened version without references
    flattened_schema = {"type": "object", "properties": {}}

    # Get the definitions section
    defs = schema.get("$defs", {})

    # Copy properties and resolve any references
    if "properties" in schema:
        flattened_schema["properties"] = _resolve_references(schema["properties"], defs)

    # Copy required fields if present
    if "required" in schema:
        flattened_schema["required"] = schema["required"]

    # Copy title if present
    if "title" in schema:
        flattened_schema["title"] = schema["title"]

    return flattened_schema


def _resolve_references(obj: Any, schema_defs: Dict[str, Any]) -> Any:
    """
    Recursively resolve JSON schema references.

    Args:
        obj: The object to resolve references in
        schema_defs: The definitions dictionary containing referenced schemas

    Returns:
        The object with all references resolved
    """
    if isinstance(obj, dict):
        # If this is a reference, resolve it
        if "$ref" in obj and len(obj) == 1:
            return _resolve_single_reference(obj, schema_defs)

        # Process each property in the object
        result = {}
        for key, value in obj.items():
            if key == "items" and "$ref" in value:
                # Special handling for array items with references
                ref_path = value["$ref"].split("/")[-1]
                if ref_path in schema_defs:
                    # Replace with the referenced schema
                    result[key] = _resolve_references(schema_defs[ref_path], schema_defs)
            else:
                # Recursively process the value
                result[key] = _resolve_references(value, schema_defs)
        return result
    elif isinstance(obj, list):
        # Process each item in the list
        return [_resolve_references(item, schema_defs) for item in obj]
    else:
        # Return primitive values as is
        return obj


def _resolve_single_reference(ref_obj: Dict[str, Any], schema_defs: Dict[str, Any]) -> Any:
    """
    Resolve a single reference object.

    Args:
        ref_obj: The reference object containing a $ref key
        schema_defs: The definitions dictionary containing referenced schemas

    Returns:
        The resolved reference
    """
    ref_path = ref_obj["$ref"].split("/")[-1]
    if ref_path in schema_defs:
        # Replace with a copy of the referenced schema
        resolved = schema_defs[ref_path].copy()
        # Recursively resolve any references in the referenced schema
        return _resolve_references(resolved, schema_defs)
    return ref_obj  # Reference not found, return as is
