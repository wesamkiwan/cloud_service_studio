from core.base_tool import BaseTool
from PyQt6.QtWidgets import QWidget
from .ui import MongoIdeWidget

class MongoIdePlugin(BaseTool):
    def __init__(self):
        self._widget = None
        
    @property
    def name(self) -> str:
        return "MongoDB IDE"
        
    @property
    def icon_name(self) -> str:
        return "fa5s.server"
        
    def get_widget(self) -> QWidget:
        if not self._widget:
            self._widget = MongoIdeWidget()
        return self._widget
        
    def on_loaded(self):
        print("MongoDB IDE plugin loaded")
        
    def on_unloaded(self):
        if self._widget:
            self._widget.cleanup()
