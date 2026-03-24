import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication

# Add project root to sys.path so we can import core and tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def qapp():
    """Ensure a QApplication instance exists before running tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
