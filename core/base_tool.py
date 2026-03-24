from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget

class BaseTool(ABC):
    """Abstract base class for all cloud framework subtools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the tool displayed in the GUI."""
        pass
        
    @property
    @abstractmethod
    def icon_name(self) -> str:
        """Name or path of the icon to represent the tool."""
        pass
        
    @abstractmethod
    def get_widget(self) -> QWidget:
        """Return the main QWidget for this tool to be embedded in the UI."""
        pass
    
    def on_loaded(self):
        """Lifecycle hook called when the tool is loaded."""
        pass
        
    def on_unloaded(self):
        """Lifecycle hook called when the tool is unloaded (cleanup)."""
        pass
