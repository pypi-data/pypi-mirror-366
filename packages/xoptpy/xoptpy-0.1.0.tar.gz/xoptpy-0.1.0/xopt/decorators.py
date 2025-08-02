from typing import Callable


def step(func: Callable) -> Callable:
    """Decorator to mark a function as a step"""
    func._is_step = True
    return func


def module(func: Callable) -> Callable:
    """Decorator to mark a function as a module factory"""
    func._is_module = True
    return func