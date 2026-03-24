# Cloud Service Studio

A modern, professional desktop application for managing cloud services and databases.
Built with Python, PyQt6, and a plugin-based architecture.

## Features

- **Professional UI**: Dark mode, responsive design, and intuitive layout.
- **Plugin Architecture**: Easily extend the application by dropping new tools into the `tools/` directory.
- **SQL IDE**: Connect to relational databases (SQLite, PostgreSQL, MySQL) using SQLAlchemy. Execute queries and view tabular results.
- **MongoDB IDE**: Connect to MongoDB clusters, browse databases and collections, and filter documents with a tree viewer.

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python main.py
```

## Adding New Tools

To create a new tool, create a folder under `tools/` (e.g. `tools/my_tool/`).
It must contain a `plugin.py` file with a class inheriting from `core.base_tool.BaseTool`.

```python
from core.base_tool import BaseTool
from PyQt6.QtWidgets import QLabel

class MyCustomTool(BaseTool):
    @property
    def name(self): return "My Custom Tool"
    
    @property
    def icon_name(self): return "custom_icon"
    
    def get_widget(self):
        return QLabel("Hello from my new tool!")
```
The application will automatically discover and load your tool.
