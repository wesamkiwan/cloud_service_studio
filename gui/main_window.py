from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QStackedWidget, QLabel, QListWidgetItem
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize
import qtawesome as qta
from core.plugin_manager import PluginManager
from gui.connection_dialog import ConnectionDialog
from core.plugin_manager import PluginManager

class MainWindow(QMainWindow):
    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        self.plugin_manager = plugin_manager
        
        self.setWindowTitle("Cloud Service Studio")
        self.setMinimumSize(1000, 700)
        
        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setIconSize(QSize(24, 24))
        self.sidebar.currentRowChanged.connect(self.display_tool)
        
        # Main content area
        self.content_area = QStackedWidget()
        
        # Add to layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        self.setup_menu()
        self.setup_ui_styling()
        self.populate_tools()

    def setup_menu(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        
        file_menu = menubar.addMenu("File")
        
        manage_conns_action = QAction("Manage Connections", self)
        manage_conns_action.triggered.connect(self.open_connection_manager)
        file_menu.addAction(manage_conns_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_connection_manager(self):
        dlg = ConnectionDialog(self)
        dlg.exec()

    def setup_ui_styling(self):
        """Apply dark mode professional stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QListWidget {
                background-color: #252526;
                color: #cccccc;
                border: none;
                border-right: 1px solid #333333;
                font-size: 14px;
                padding-top: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #37373d;
                color: #ffffff;
                border-left: 3px solid #007acc;
            }
            QListWidget::item:hover:!selected {
                background-color: #2a2d2e;
            }
            QStackedWidget {
                background-color: #1e1e1e;
            }
        """)

    def populate_tools(self):
        plugins = self.plugin_manager.get_plugins()
        if not plugins:
            # Emtpy state
            empty_label = QLabel("No tools loaded. Check the tools directory.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808080; font-size: 16px;")
            self.content_area.addWidget(empty_label)
            return

        for plugin in plugins:
            item = QListWidgetItem(plugin.name)
            try:
                icon = qta.icon(plugin.icon_name, color="#cccccc")
                item.setIcon(icon)
            except Exception as e:
                print(f"Warning: Could not load icon for {plugin.name}: {e}")
                
            self.sidebar.addItem(item)
            widget = plugin.get_widget()
            self.content_area.addWidget(widget)
            
        # Select first tool by default
        if self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)

    def display_tool(self, index: int):
        self.content_area.setCurrentIndex(index)
