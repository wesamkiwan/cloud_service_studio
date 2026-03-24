import sys
import os
from PyQt6.QtWidgets import QApplication

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core.plugin_manager import PluginManager

def main():
    app = QApplication(sys.argv)
    
    # Initialize plugin manager and load tools
    plugin_manager = PluginManager()
    plugin_manager.discover_plugins("tools")
    
    # Initialize and show main window
    window = MainWindow(plugin_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
