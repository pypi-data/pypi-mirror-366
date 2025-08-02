from typing import Dict, Any, Optional
from .client import client
from .instance import ModuleInstance


def start(module: str, configurables: Dict[str, Any] = None, 
          tunables: Dict[str, Any] = None) -> ModuleInstance:
    """Start a module instance with given configuration"""
    module_name = module.split('@')[0]  # Remove version if present
    
    if module_name in client()._modules:
        mod = client()._modules[module_name]
        config = {
            'configurables': configurables or {},
            'tunables': tunables or {}
        }
        return ModuleInstance(mod, config)
    else:
        raise ValueError(f"Module {module_name} not found")


def details(module_name: str) -> Optional[Dict[str, Any]]:
    """Get details about a registered module"""
    if module_name in client()._modules:
        mod = client()._modules[module_name]
        return {
            'name': mod.name,
            'steps': list(mod.steps.keys()),
            'start_step': mod.start_step,
            'long_description': mod.long_description
        }
    return None