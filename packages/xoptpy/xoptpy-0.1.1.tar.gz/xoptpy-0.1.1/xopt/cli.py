#!/usr/bin/env python3
"""
Command-line interface for xopt module management
"""

import argparse
import sys
import json
import toml
from pathlib import Path
from xopt.client import client


def cmd_package(args):
    """Package a module directory"""
    try:
        output_path = client().package(args.module_dir, args.output)
        print(f"Package created: {output_path}")
    except Exception as e:
        print(f"Error packaging module: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_install(args):
    """Install a module package"""
    try:
        module_name = client().install(args.package)
        print(f"Module {module_name} installed successfully")
    except Exception as e:
        print(f"Error installing module: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_uninstall(args):
    """Uninstall a module"""
    try:
        success = client().uninstall(args.module)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error uninstalling module: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """List installed modules"""
    try:
        installed = client().list_installed()
        if not installed:
            print("No modules installed")
            return
        
        print("Installed modules:")
        for name, info in installed.items():
            print(f"  {name}@{info['version']} - {info['installed_at']}")
    except Exception as e:
        print(f"Error listing modules: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_run(args):
    """Run an installed module"""
    try:
        import subprocess
        import os
        
        # Find installed module
        installed = client().list_installed()
        if args.module not in installed:
            print(f"Module {args.module} is not installed", file=sys.stderr)
            sys.exit(1)
        
        module_info = installed[args.module]
        
        # For reference modules, use the base module's environment
        if module_info.get("type") == "reference":
            base_module = module_info["base_module"] 
            base_name = base_module.split("@")[0]
            if base_name not in installed:
                print(f"Base module {base_name} not installed", file=sys.stderr)
                sys.exit(1)
            base_info = installed[base_name]
            module_dir = Path(base_info["installed_at"])
        else:
            module_dir = Path(module_info["installed_at"])
            
        venv_python = module_dir / "venv" / ("Scripts" if os.name == "nt" else "bin") / "python"
        
        # Prepare config overrides
        config_json = None
        if args.config:
            config_json = args.config
        
        # Build command
        cmd = [str(venv_python), "-m", "xopt.runner", "--module", args.module, "--input", args.input]
        if config_json:
            cmd.extend(["--config", config_json])
        
        # For reference modules, run from base module directory
        if module_info.get("type") == "reference":
            run_dir = module_dir  # Base module directory
        else:
            run_dir = module_dir
            
        # Run in module's virtual environment
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(run_dir))
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"Error running module: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running module: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_dev_run(args):
    """Run a module from a development directory"""
    try:
        import subprocess
        import sys
        
        module_dir = Path(args.module_dir)
        if not module_dir.exists():
            print(f"Module directory {module_dir} does not exist", file=sys.stderr)
            sys.exit(1)
        
        # Use current Python environment for development
        cmd = [sys.executable, "-m", "xopt.runner", "--module-dir", str(module_dir), "--module", args.module, "--input", args.input]
        
        if args.config:
            cmd.extend(["--config", args.config])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"Error running module: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running module: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_sync(args):
    """Sync project dependencies from .xopt/deps.toml"""
    try:
        xopt_dir = Path(".xopt")
        deps_file = xopt_dir / "deps.toml"
        
        if not deps_file.exists():
            print("No .xopt/deps.toml found. Run 'xopt init' to create a project.", file=sys.stderr)
            sys.exit(1)
        
        # Load dependencies
        deps = toml.load(deps_file)
        modules = deps.get("modules", {})
        sources = deps.get("sources", {})
        
        installed = client().list_installed()
        
        for module_name, version in modules.items():
            if module_name in installed:
                print(f"✅ {module_name}@{version} already installed")
                continue
            
            # Check if we have a local source
            if module_name in sources:
                source_info = sources[module_name]
                if "path" in source_info:
                    source_path = Path(source_info["path"])
                    if source_path.exists():
                        print(f"📦 Packaging {module_name} from {source_path}")
                        package_path = client().package(str(source_path))
                        print(f"📥 Installing {module_name}")
                        client().install(package_path)
                        continue
            
            print(f"❌ Module {module_name}@{version} not found locally")
            print(f"   Add to sources in deps.toml or provide .xopt package")
        
        print("\n🎉 Sync complete!")
        
    except Exception as e:
        print(f"Error syncing dependencies: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_install_config(args):
    """Install a module configuration file"""
    try:
        module_name = client().install_config(args.config_file)
        print(f"Reference module {module_name} installed successfully")
    except Exception as e:
        print(f"Error installing config: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_project_run(args):
    """Run a module using project configuration"""
    try:
        xopt_dir = Path(".xopt")
        if not xopt_dir.exists():
            print("No .xopt directory found. Run 'xopt init' to create a project.", file=sys.stderr)
            sys.exit(1)
        
        # Load module config
        module_name = args.module
        safe_name = module_name.replace("/", "-")
        config_file = xopt_dir / f"{safe_name}.toml"
        
        config_overrides = {}
        if config_file.exists():
            module_config = toml.load(config_file)
            config_overrides = {
                "tunables": module_config.get("tunables", {}),
                "configurables": module_config.get("configurables", {})
            }
        
        # Merge with any CLI overrides
        if args.config:
            cli_config = json.loads(args.config)
            if "tunables" in cli_config:
                config_overrides.setdefault("tunables", {}).update(cli_config["tunables"])
            if "configurables" in cli_config:
                config_overrides.setdefault("configurables", {}).update(cli_config["configurables"])
        
        # Run the module
        import subprocess
        import os
        
        installed = client().list_installed()
        if module_name not in installed:
            print(f"Module {module_name} not installed. Run 'xopt sync' first.", file=sys.stderr)
            sys.exit(1)
        
        module_info = installed[module_name]
        module_dir = Path(module_info["installed_at"])
        
        # Check if this is a reference module
        module_toml = module_dir / "module.toml"
        if module_toml.exists():
            # This is a reference module - use the base module's venv
            import toml
            ref_config = toml.load(module_toml)
            base_module = ref_config["module"]["base_module"]
            base_name = base_module.split("@")[0]  # Remove version
            
            if base_name not in installed:
                print(f"Base module {base_name} not installed", file=sys.stderr)
                sys.exit(1)
            
            base_info = installed[base_name]
            base_dir = Path(base_info["installed_at"])
            venv_python = base_dir / "venv" / ("Scripts" if os.name == "nt" else "bin") / "python"
            
            cmd = [str(venv_python), "-m", "xopt.runner", "--reference", module_name, "--input", args.input]
            if config_overrides:
                cmd.extend(["--config", json.dumps(config_overrides)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(base_dir))
        else:
            # Regular module
            venv_python = module_dir / "venv" / ("Scripts" if os.name == "nt" else "bin") / "python"
            
            cmd = [str(venv_python), "-m", "xopt.runner", "--module", module_name, "--input", args.input]
            if config_overrides:
                cmd.extend(["--config", json.dumps(config_overrides)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(module_dir))
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"Error running module: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running project module: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_init(args):
    """Initialize a new xopt project"""
    try:
        xopt_dir = Path(".xopt")
        xopt_dir.mkdir(exist_ok=True)
        
        # Create deps.toml
        deps_file = xopt_dir / "deps.toml"
        if not deps_file.exists():
            deps_content = """# xopt module dependencies
[modules]
# "xopt/react" = "0.1.0"
# "xopt/calculator" = "0.1.0"

# Optional: sources for modules (for development)
[sources]
# "xopt/react" = { path = "examples/modules/react" }
# "xopt/calculator" = { path = "examples/modules/calculator" }

# Optional: registries for finding modules
[registries]  
# default = "https://registry.xopt.ai"
# local = "file://./packages"
"""
            deps_file.write_text(deps_content)
            print(f"✅ Created {deps_file}")
        else:
            print(f"📁 {deps_file} already exists")
        
        print(f"\n🎉 Initialized xopt project in {xopt_dir}")
        print("\n📝 Next steps:")
        print(f"   1. Edit {deps_file} to add your module dependencies")
        print(f"   2. Run 'xopt sync' to install dependencies")
        print(f"   3. Create module config files like .xopt/xopt-react.toml")
        
    except Exception as e:
        print(f"Error initializing project: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="xopt module management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Package command
    package_parser = subparsers.add_parser("package", help="Package a module directory")
    package_parser.add_argument("module_dir", help="Directory containing the module")
    package_parser.add_argument("-o", "--output", help="Output package path")
    package_parser.set_defaults(func=cmd_package)
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a module package")
    install_parser.add_argument("package", help="Path to .xopt package file")
    install_parser.set_defaults(func=cmd_install)
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a module")
    uninstall_parser.add_argument("module", help="Module name to uninstall")
    uninstall_parser.set_defaults(func=cmd_uninstall)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed modules")
    list_parser.set_defaults(func=cmd_list)
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an installed module")
    run_parser.add_argument("module", help="Module name to run")
    run_parser.add_argument("input", help="Input data for the module")
    run_parser.add_argument("-c", "--config", help="JSON config overrides")
    run_parser.set_defaults(func=cmd_run)
    
    # Dev command
    dev_parser = subparsers.add_parser("dev", help="Run a module from development directory")
    dev_parser.add_argument("module_dir", help="Module directory path")
    dev_parser.add_argument("module", help="Module name")
    dev_parser.add_argument("input", help="Input data for the module")
    dev_parser.add_argument("-c", "--config", help="JSON config overrides")
    dev_parser.set_defaults(func=cmd_dev_run)
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new xopt project")
    init_parser.set_defaults(func=cmd_init)
    
    # Sync command  
    sync_parser = subparsers.add_parser("sync", help="Sync project dependencies")
    sync_parser.set_defaults(func=cmd_sync)
    
    # Install config command
    install_config_parser = subparsers.add_parser("install-config", help="Install a module configuration")
    install_config_parser.add_argument("config_file", help="Path to module config file (.toml)")
    install_config_parser.set_defaults(func=cmd_install_config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()