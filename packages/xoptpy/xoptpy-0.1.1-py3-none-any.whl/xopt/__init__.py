from .models import Module, StepResult, Context
from .client import XOptClient, client
from .instance import ModuleInstance
from .decorators import step, module
from .registry import register
from .utils import start, details

# Import call_llm only when needed to avoid dependency issues
def call_llm(*args, **kwargs):
    from .llm import call_llm as _call_llm
    return _call_llm(*args, **kwargs)

__all__ = [
    'Module',
    'StepResult', 
    'Context',
    'XOptClient',
    'client',
    'ModuleInstance',
    'step',
    'module',
    'register',
    'start',
    'details',
    'call_llm'
]