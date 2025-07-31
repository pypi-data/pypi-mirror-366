from functools import lru_cache
import importlib
from typing import Callable

from openbench.config import get_all_benchmarks


# Dynamically generate registry from config
def _generate_task_registry():
    """Generate task registry from config."""
    registry = {}
    for name, metadata in get_all_benchmarks().items():
        registry[name] = f"{metadata.module_path}.{metadata.function_name}"
    return registry


TASK_REGISTRY = _generate_task_registry()


@lru_cache()
def load_task(benchmark_name: str) -> Callable:
    """
    Loads a task by benchmark name using the registry.

    Args:
        benchmark_name (str): The name of the benchmark.

    Returns:
        Callable: The imported function object.

    Raises:
        ValueError: If the benchmark is not in the registry.
        ImportError: If the module cannot be imported.
        AttributeError: If the function does not exist in the module.
    """
    import_path = TASK_REGISTRY.get(benchmark_name)
    if not import_path:
        raise ValueError(
            f"Unknown benchmark: '{benchmark_name}'. "
            f"Available benchmarks: {', '.join(TASK_REGISTRY.keys())}"
        )
    module_path, func_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
