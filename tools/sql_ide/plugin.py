from core.base_tool import BaseTool
from PyQt6.QtWidgets import QWidget
from .ui import SqlIdeWidget

class SqlIdePlugin(BaseTool):
    def __init__(self):
        self._widget = None
        
    @property
    def name(self) -> str:
        return "SQL IDE"
        
    @property
    def icon_name(self) -> str:
        return "fa5s.database"
        
    def get_widget(self) -> QWidget:
        if not self._widget:
            self._widget = SqlIdeWidget()
        return self._widget
        
    def on_loaded(self):
        print("SQL IDE plugin loaded")
        
    def on_unloaded(self):
        if self._widget:
            self._widget.cleanup()
