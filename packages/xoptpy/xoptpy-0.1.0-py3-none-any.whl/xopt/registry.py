from typing import Callable
from .client import client


def register(module_func: Callable) -> None:
    """Register a module with the global registry"""
    if hasattr(module_func, '_is_module'):
        mod = module_func()
        # Register with both versioned and unversioned names
        client()._modules[mod.versioned_name] = mod  # e.g. "xopt/calculator:0.1.0"
        client()._modules[mod.name] = mod            # e.g. "xopt/calculator"