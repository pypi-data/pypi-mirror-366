import importlib.util
import json
import sys
from functools import wraps
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from instructor import OpenAISchema

from ..const import FUNCTIONS_DIR


def wrap_gemini_function(func: Callable) -> Callable:
    """Wrap a function to add a name and docstring"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\033[94m@Function call: {wrapper.__name__}({json.dumps(kwargs) if kwargs else args})\033[0m")
        return func(*args, **kwargs)

    return wrapper


class Function:
    """Function description class"""

    def __init__(self, function: type["OpenAISchema"]):
        self.name = function.openai_schema["name"]
        self.description = function.openai_schema.get("description", "")
        self.parameters = function.openai_schema.get("parameters", {})
        self.execute = function.execute  # type: ignore
        self.func_cls = function


_func_name_map: Optional[dict[str, Function]] = None


def get_func_name_map() -> dict[str, Function]:
    """Get function name map"""
    global _func_name_map
    if _func_name_map:
        return _func_name_map
    if not FUNCTIONS_DIR.exists():
        FUNCTIONS_DIR.mkdir(parents=True, exist_ok=True)
        return {}
    functions = []
    for file in FUNCTIONS_DIR.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = str(file).replace("/", ".").rstrip(".py")
        spec = importlib.util.spec_from_file_location(module_name, str(file))
        module = importlib.util.module_from_spec(spec)  # type: ignore
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore

        if not hasattr(module.Function, "openai_schema") or not hasattr(module.Function, "anthropic_schema"):
            raise TypeError(f"Function {module_name} must be a subclass of instructor.OpenAISchema")
        if not hasattr(module.Function, "execute"):
            raise TypeError(f"Function {module_name} must have an 'execute' classmethod")

        # Add to function list
        functions.append(Function(function=module.Function))

    # Cache the function list
    _func_name_map = {func.name: func for func in functions}
    return _func_name_map


def list_functions() -> list[Function]:
    """List all available buildin functions"""
    global _func_name_map
    if not _func_name_map:
        _func_name_map = get_func_name_map()

    return list(_func_name_map.values())


def get_function(name: str) -> Function:
    """Get a function by name

    Args:
        name: Function name

    Returns:
        Function execute method

    Raises:
        ValueError: If function not found
    """
    func_map = get_func_name_map()
    if name in func_map:
        return func_map[name]
    raise ValueError(f"Function {name!r} not found")


def get_functions_gemini_format() -> List[Callable]:
    """Get functions in gemini format"""
    gemini_functions = []
    for func_name, func in get_func_name_map().items():
        wrapped_func = wrap_gemini_function(func.execute)
        wrapped_func.__name__ = func_name
        wrapped_func.__doc__ = func.description
        gemini_functions.append(wrapped_func)
    return gemini_functions
