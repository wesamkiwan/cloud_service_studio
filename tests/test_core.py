import os
import pytest
from core.plugin_manager import PluginManager

def test_plugin_discovery(qapp):
    """Test that the plugin manager can discover our two built-in tools."""
    manager = PluginManager()
    manager.discover_plugins("tools")
    
    plugins = manager.get_plugins()
    # We expect SQL IDE and MongoDB IDE
    assert len(plugins) >= 2, "Should discover at least 2 plugins"
    
    plugin_names = [p.name for p in plugins]
    assert "SQL IDE" in plugin_names
    assert "MongoDB IDE" in plugin_names
    
    # Test getting specific plugin
    sql_plugin = manager.get_plugin("SQL IDE")
    assert sql_plugin is not None
    assert sql_plugin.icon_name == "database"
