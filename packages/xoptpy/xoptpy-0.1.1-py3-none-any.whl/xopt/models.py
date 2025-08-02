
from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod
import json


class Context(ABC):
    """Interface for step context implementations"""
    
    @abstractmethod
    def get_context(self, text: Optional[str] = None) -> str:
        """Get context as string, optionally incorporating new text"""
        pass


class StepResult(BaseModel):
    """Result of executing a step - can be a module call or final response"""
    action: str  # "module_call" or "response" 
    content: Any
    module_name: Optional[str] = None
    module_input: Optional[Dict[str, Any]] = None

class Module:
    """Xopt module that contains steps and can be executed"""
    
    def __init__(self, name: str, version: str, description: str, 
                 long_description: str = "", tunables: List = None, 
                 configurables: List = None):
        self.name = name
        self.version = version
        self.description = description
        self.long_description = long_description
        self.tunables = tunables or []
        self.configurables = configurables or []
        self.steps = {}
        self.start_step = None
    
    @property
    def versioned_name(self) -> str:
        """Get the full name with version (name:version)"""
        return f"{self.name}:{self.version}"
        
    def register(self, name: str, step: Callable, input_type: type, output_type: type = None):
        """Register a step function with the module"""
        self.steps[name] = {
            'function': step,
            'input_type': input_type,
            'output_type': output_type
        }
    
    def set_start_step(self, step_name: str):
        """Set the starting step for this module"""
        self.start_step = step_name
    
    def step(self, func):
        """Decorator to register a step function"""
        self.register(func.__name__, func, str, type(None))
        return func

