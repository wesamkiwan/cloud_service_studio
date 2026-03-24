import os
import importlib
import inspect
import sys
from typing import List, Dict
from .base_tool import BaseTool

class PluginManager:
    """Discovers and manages tools (plugins) in the application."""
    
    def __init__(self):
        self._plugins: Dict[str, BaseTool] = {}
        
    def discover_plugins(self, tools_dir: str):
        """Scan the tools directory and load subtools."""
        # Make sure tools directory exists within the project directory
        # The tools directory is expected to be adjacent to main.py
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_path = os.path.join(project_root, tools_dir)
        
        if not os.path.isdir(base_path):
            os.makedirs(base_path, exist_ok=True)
            # Create an __init__.py so it can be treated as a package
            with open(os.path.join(base_path, "__init__.py"), "w") as f:
                f.write("")
            return

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and not item.startswith("__"):
                self._load_plugin(item)
                
    def _load_plugin(self, plugin_module_name: str):
        """Load a specific plugin by module name."""
        try:
            # Assuming tools is a package
            module_path = f"tools.{plugin_module_name}.plugin"
            module = importlib.import_module(module_path)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj is not BaseTool:
                    # Instantiate the plugin
                    plugin_instance = obj()
                    self._plugins[plugin_instance.name] = plugin_instance
                    plugin_instance.on_loaded()
                    print(f"Successfully loaded plugin: {plugin_instance.name}")
                    
        except ImportError as e:
            print(f"Failed to load plugin from {plugin_module_name}: {e}")
            
    def get_plugins(self) -> List[BaseTool]:
        """Return a list of all loaded plugins."""
        return list(self._plugins.values())
        
    def get_plugin(self, name: str) -> BaseTool:
        """Return a specific plugin by name."""
        return self._plugins.get(name)
