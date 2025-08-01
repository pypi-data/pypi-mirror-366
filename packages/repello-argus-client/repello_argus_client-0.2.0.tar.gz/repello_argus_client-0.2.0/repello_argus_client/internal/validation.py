from functools import wraps
from typing import Any, Callable, Optional

from pydantic import ValidationError, validate_call

from ..errors import ArgusTypeError


def format_policy_error(exc: ValidationError, base_key: str, policy_name: str) -> str:
    error_details = []
    for error in exc.errors():
        # e.g., "[1].0" -> the first element of the second item in the list
        location_suffix = ".".join(map(str, error["loc"]))
        full_location = f"{base_key}.{location_suffix}" if location_suffix else base_key
        message = error["msg"]
        error_details.append(f"  - In key '{full_location}': {message}")
    return f"Invalid structure in policy '{policy_name}':\n" + "\n".join(error_details)


def _format_error(exc: ValidationError) -> str:
    """Formats a Pydantic ValidationError into a user-friendly string."""
    error_details = []
    for error in exc.errors():
        location = ".".join(map(str, error["loc"]))
        message = error["msg"]
        error_details.append(f"  - Argument '{location}': {message}")

    error_summary = "\n".join(error_details)
    return f"Invalid argument type(s) provided:\n{error_summary}"


def arg_validator(func: Callable) -> Callable:
    """
    A decorator that wraps a function with Pydantic's validation and translates
    its ValidationError into a custom ArgusTypeError.

    This decorator relies on Pydantic being a required dependency of the SDK.
    """
    _validated_func: Optional[Callable] = None

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal _validated_func

        if _validated_func is None:
            _validated_func = validate_call(config=dict(arbitrary_types_allowed=True))(
                func
            )

        try:
            return _validated_func(*args, **kwargs)
        except ValidationError as e:
            raise ArgusTypeError(_format_error(e)) from e

    return wrapper
