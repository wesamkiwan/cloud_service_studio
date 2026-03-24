from core.base_tool import BaseTool
from PyQt6.QtWidgets import QWidget
from .ui import NotebookIdeWidget

class NotebookIdePlugin(BaseTool):
    def __init__(self):
        self._widget = None
        
    @property
    def name(self) -> str:
        return "Spark Notebook Editor"
        
    @property
    def icon_name(self) -> str:
        return "fa5s.book"
        
    def get_widget(self) -> QWidget:
        if not self._widget:
            self._widget = NotebookIdeWidget()
        return self._widget
        
    def on_loaded(self):
        print("Spark Notebook Editor plugin loaded")
        
    def on_unloaded(self):
        pass
