from typing import Dict, Any, Callable, Optional
import yaml
import os
import subprocess
import sys
import tempfile
import tarfile
import json
from pathlib import Path


class XOptClient:
    """Client for managing xopt configuration and modules"""
    
    def __init__(self, config_path: str = "xopt.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._modules = {}
        self._instances = {}
        self.modules_dir = Path.home() / ".xopt" / "modules"
        self.modules_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from xopt.yaml"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def tunable(self, name: str, description: str = "") -> Callable:
        """Create a tunable parameter that reads from config"""
        def get_tunable_value():
            # Find the tunable value in config
            for module_config in self.config.values():
                if 'tunables' in module_config and name in module_config['tunables']:
                    return module_config['tunables'][name]
            return f"Default {name}"
        
        return get_tunable_value
    
    def configurable(self, name: str, description: str = "") -> Any:
        """Create a configurable parameter that reads from config"""
        # Find the configurable value in config
        for module_config in self.config.values():
            if 'configurables' in module_config and name in module_config['configurables']:
                return module_config['configurables'][name]
        return []
    
    def package(self, module_dir: str, output_path: Optional[str] = None) -> str:
        """Package a module directory into a .xopt archive"""
        module_path = Path(module_dir)
        if not module_path.exists():
            raise ValueError(f"Module directory {module_dir} does not exist")
        
        # Load module metadata
        if (module_path / "xopt.yaml").exists():
            with open(module_path / "xopt.yaml") as f:
                config = yaml.safe_load(f)
                module_name = list(config.keys())[0].split("@")[0]
                version = list(config.keys())[0].split("@")[1]
        else:
            raise ValueError("Module must have xopt.yaml file")
        
        # Create output path if not specified
        if not output_path:
            safe_name = module_name.replace("/", "_")
            output_path = f"{safe_name}-{version}.xopt"
        
        # Create package archive
        with tarfile.open(output_path, "w:gz") as tar:
            # Add all module files
            tar.add(module_path, arcname=".")
        
        print(f"📦 Packaged {module_name}@{version} to {output_path}")
        return output_path
    
    def install_config(self, config_path: str) -> str:
        """Install a module configuration (reference-based module)"""
        config_path = Path(config_path)
        if not config_path.exists():
            raise ValueError(f"Config file {config_path} does not exist")
        
        # Load config
        import toml
        config = toml.load(config_path)
        
        if "module" not in config:
            raise ValueError("Config file must have [module] section")
        
        module_info = config["module"]
        module_name = module_info["name"]
        base_module = module_info.get("base_module")
        
        if not base_module:
            raise ValueError("Reference-based modules must specify base_module")
        
        # Check if base module is installed
        installed = self.list_installed()
        base_name = base_module.split("@")[0]
        if base_name not in installed:
            raise ValueError(f"Base module {base_name} not installed. Install it first.")
        
        # Create module directory
        safe_name = module_name.replace("/", "_")
        module_dir = self.modules_dir / safe_name
        if module_dir.exists():
            print(f"⚠️  Module {module_name} already installed, removing old version")
            import shutil
            shutil.rmtree(module_dir)
        
        module_dir.mkdir(parents=True)
        
        # Copy config file
        import shutil
        shutil.copy2(config_path, module_dir / "module.toml")
        
        # Save installation metadata
        install_info = {
            "name": module_name,
            "version": module_info["version"],
            "installed_at": str(module_dir),
            "type": "reference",
            "base_module": base_module,
            "config": config
        }
        
        with open(module_dir / "install_info.json", "w") as f:
            json.dump(install_info, f, indent=2)
        
        print(f"✅ Installed reference module {module_name}@{module_info['version']}")
        return module_name

    def install(self, package_path: str) -> str:
        """Install a .xopt package with virtual environment"""
        package_path = Path(package_path)
        if not package_path.exists():
            raise ValueError(f"Package {package_path} does not exist")
        
        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract package
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(temp_path)
            
            # Load module metadata
            config_path = temp_path / "xopt.yaml"
            if not config_path.exists():
                raise ValueError("Package missing xopt.yaml")
            
            with open(config_path) as f:
                config = yaml.safe_load(f)
                module_spec = list(config.keys())[0]
                module_name = module_spec.split("@")[0]
                version = module_spec.split("@")[1]
            
            # Create module directory
            module_dir = self.modules_dir / module_name.replace("/", "_")
            if module_dir.exists():
                print(f"⚠️  Module {module_name} already installed, removing old version")
                import shutil
                shutil.rmtree(module_dir)
            
            module_dir.mkdir(parents=True)
            
            # Copy module files
            import shutil
            for item in temp_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, module_dir / item.name)
                else:
                    shutil.copy2(item, module_dir / item.name)
            
            # Create virtual environment
            venv_path = module_dir / "venv"
            print(f"🐍 Creating virtual environment at {venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            
            # Install dependencies
            if (module_dir / "pyproject.toml").exists() or (module_dir / "requirements.txt").exists():
                venv_python = venv_path / ("Scripts" if os.name == "nt" else "bin") / "python"
                
                # Install xopt in the venv first
                print("📦 Installing xopt in module environment")
                subprocess.run([str(venv_python), "-m", "pip", "install", "-e", str(Path(__file__).parent.parent)], check=True)
                
                # Install module dependencies
                if (module_dir / "pyproject.toml").exists():
                    print("📦 Installing module dependencies from pyproject.toml")
                    subprocess.run([str(venv_python), "-m", "pip", "install", "-e", str(module_dir)], check=True)
                else:
                    print("📦 Installing module dependencies from requirements.txt")
                    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(module_dir / "requirements.txt")], check=True)
            
            # Save installation metadata
            install_info = {
                "name": module_name,
                "version": version,
                "installed_at": str(module_dir),
                "config": config[module_spec]
            }
            
            with open(module_dir / "install_info.json", "w") as f:
                json.dump(install_info, f, indent=2)
            
            print(f"✅ Installed {module_name}@{version} to {module_dir}")
            return module_name
    
    def list_installed(self) -> Dict[str, Dict[str, Any]]:
        """List all installed modules"""
        installed = {}
        
        for module_path in self.modules_dir.iterdir():
            if module_path.is_dir():
                install_info_path = module_path / "install_info.json"
                if install_info_path.exists():
                    with open(install_info_path) as f:
                        info = json.load(f)
                        installed[info["name"]] = info
        
        return installed
    
    def uninstall(self, module_name: str) -> bool:
        """Uninstall a module"""
        module_dir = self.modules_dir / module_name.replace("/", "_")
        if module_dir.exists():
            import shutil
            shutil.rmtree(module_dir)
            print(f"🗑️  Uninstalled {module_name}")
            return True
        else:
            print(f"❌ Module {module_name} not found")
            return False


# Global client instance
_client = None

def client() -> XOptClient:
    """Get the global xopt client"""
    global _client
    if _client is None:
        _client = XOptClient()
    return _client