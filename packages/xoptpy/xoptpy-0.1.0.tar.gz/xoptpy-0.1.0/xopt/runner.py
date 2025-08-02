#!/usr/bin/env python3
"""
Module runner for executing xopt modules in isolated virtual environments
"""

import sys
import json
import importlib.util
import os
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
import yaml


def load_module_from_path(module_path: Path, module_name: str):
    """Load a Python module from a file path"""
    # Look for the main module file - try common patterns
    candidates = [
        module_path / f"{module_name.split('/')[-1]}.py",
        module_path / "main.py",
        module_path / "__init__.py"
    ]
    
    # Also check any .py files in the directory
    for py_file in module_path.glob("*.py"):
        if py_file.name not in ["__init__.py", "main.py"]:
            candidates.insert(0, py_file)
    
    for candidate in candidates:
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("xopt_module", candidate)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["xopt_module"] = module
                spec.loader.exec_module(module)
                return module
    
    raise ImportError(f"Could not find module file in {module_path}")


def run_installed_module(module_name: str, input_data: str, config_overrides: Optional[Dict[str, Any]] = None) -> str:
    """Run an installed module with given input"""
    from xopt.client import client
    
    # Find installed module
    installed_modules = client().list_installed()
    if module_name not in installed_modules:
        raise ValueError(f"Module {module_name} is not installed")
    
    module_info = installed_modules[module_name]
    
    # Check if this is a reference module
    if module_info.get("type") == "reference":
        return run_reference_module(module_name, input_data, config_overrides)
    
    module_dir = Path(module_info["installed_at"])


def run_reference_module(module_name: str, input_data: str, config_overrides: Optional[Dict[str, Any]] = None) -> str:
    """Run a reference-based module"""
    from xopt.client import client
    import toml
    
    # Find installed module
    installed_modules = client().list_installed()
    module_info = installed_modules[module_name]
    
    # Load the reference config
    module_dir = Path(module_info["installed_at"])
    config_file = module_dir / "module.toml"
    ref_config = toml.load(config_file)
    
    # Get base module info
    base_module = module_info["base_module"]
    base_name = base_module.split("@")[0]
    
    if base_name not in installed_modules:
        raise ValueError(f"Base module {base_name} not installed")
    
    # Merge configurations: reference config + overrides
    final_config = {}
    
    # Start with reference module config
    if "tunables" in ref_config:
        final_config["tunables"] = ref_config["tunables"].copy()
    if "configurables" in ref_config:
        final_config["configurables"] = ref_config["configurables"].copy()
    
    # Apply any CLI overrides
    if config_overrides:
        if "tunables" in config_overrides:
            final_config.setdefault("tunables", {}).update(config_overrides["tunables"])
        if "configurables" in config_overrides:
            final_config.setdefault("configurables", {}).update(config_overrides["configurables"])
    
    # Run the base module with merged config - but don't recurse
    base_info = installed_modules[base_name]
    module_dir = Path(base_info["installed_at"])
    
    # Load base module configuration
    import yaml
    config_path = module_dir / "xopt.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            module_spec = list(config.keys())[0]
            base_module_config = config[module_spec]
    else:
        base_module_config = base_info.get("config", {})
    
    # Override base config with reference config
    if "tunables" in final_config:
        base_module_config.setdefault("tunables", {}).update(final_config["tunables"])
    if "configurables" in final_config:
        base_module_config.setdefault("configurables", {}).update(final_config["configurables"])
    
    # Set up environment for module execution
    import os
    original_cwd = os.getcwd()
    os.chdir(module_dir)
    
    try:
        # Load and register the base module
        module_py = load_module_from_path(module_dir, base_name)
        
        # Update client configuration with merged config
        from xopt.client import client
        client().config = {module_spec: base_module_config}
        
        # Find and start the base module
        import xopt
        if base_name in client()._modules:
            module_instance = xopt.start(
                module=base_name,
                configurables=base_module_config.get("configurables", {}),
                tunables=base_module_config.get("tunables", {})
            )
            
            # Execute the module
            result = module_instance.call(input_data)
            
            # Return result content
            if hasattr(result, 'content'):
                return str(result.content)
            else:
                return str(result)
        else:
            raise ValueError(f"Base module {base_name} not found in registry after loading")
    
    finally:
        os.chdir(original_cwd)
    
    # Load module configuration
    config_path = module_dir / "xopt.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            module_spec = list(config.keys())[0]
            module_config = config[module_spec]
    else:
        module_config = module_info.get("config", {})
    
    # Apply config overrides
    if config_overrides:
        if "tunables" in config_overrides:
            module_config.setdefault("tunables", {}).update(config_overrides["tunables"])
        if "configurables" in config_overrides:
            module_config.setdefault("configurables", {}).update(config_overrides["configurables"])
    
    # Set up environment for module execution
    original_cwd = os.getcwd()
    os.chdir(module_dir)
    
    try:
        # Load and register the module
        module_py = load_module_from_path(module_dir, module_name)
        
        # Update client configuration with module config
        client().config = {module_spec: module_config}
        
        # Find and start the module
        import xopt
        if module_name in client()._modules:
            module_instance = xopt.start(
                module=module_name,
                configurables=module_config.get("configurables", {}),
                tunables=module_config.get("tunables", {})
            )
            
            # Execute the module
            result = module_instance.call(input_data)
            
            # Return result content
            if hasattr(result, 'content'):
                return str(result.content)
            else:
                return str(result)
        else:
            raise ValueError(f"Module {module_name} not found in registry after loading")
    
    finally:
        os.chdir(original_cwd)


def main():
    """Main entry point for module runner"""
    parser = argparse.ArgumentParser(description="Run xopt modules in isolated environments")
    parser.add_argument("--module", help="Module name to run")
    parser.add_argument("--reference", help="Reference module name to run")
    parser.add_argument("--input", required=True, help="Input data for the module")
    parser.add_argument("--config", help="JSON string with config overrides")
    parser.add_argument("--module-dir", help="Path to module directory (for development)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.module and not args.reference:
        parser.error("Either --module or --reference must be specified")
    if args.module and args.reference:
        parser.error("Cannot specify both --module and --reference")
    
    try:
        # Parse config overrides if provided
        config_overrides = None
        if args.config:
            config_overrides = json.loads(args.config)
        
        if args.module_dir:
            # Development mode - run from module directory
            module_dir = Path(args.module_dir)
            original_cwd = os.getcwd()
            os.chdir(module_dir)
            
            try:
                # Load module
                module_py = load_module_from_path(module_dir, args.module)
                
                # Load config
                config_path = module_dir / "xopt.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        module_spec = list(config.keys())[0]
                        module_config = config[module_spec]
                else:
                    module_config = {}
                
                # Apply overrides
                if config_overrides:
                    if "tunables" in config_overrides:
                        module_config.setdefault("tunables", {}).update(config_overrides["tunables"])
                    if "configurables" in config_overrides:
                        module_config.setdefault("configurables", {}).update(config_overrides["configurables"])
                
                # Set up client config
                from xopt.client import client
                client().config = {module_spec: module_config}
                
                # Start and run module
                import xopt
                module_name = module_spec.split("@")[0]
                module_instance = xopt.start(
                    module=module_name,
                    configurables=module_config.get("configurables", {}),
                    tunables=module_config.get("tunables", {})
                )
                
                result = module_instance.call(args.input)
                output = result.content if hasattr(result, 'content') else str(result)
                print(output)
            
            finally:
                os.chdir(original_cwd)
        else:
            # Production mode - run installed module
            if args.reference:
                result = run_reference_module(args.reference, args.input, config_overrides)
            else:
                result = run_installed_module(args.module, args.input, config_overrides)
            print(result)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()