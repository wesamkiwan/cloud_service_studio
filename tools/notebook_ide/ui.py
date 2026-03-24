from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QScrollArea, QMessageBox,
    QTextEdit, QComboBox, QFrame
)
from PyQt6.QtCore import Qt
import nbformat
from .backend import NotebookBackend

class CellWidget(QFrame):
    def __init__(self, cell_data, parent_controller, index):
        super().__init__()
        self.cell_data = cell_data
        self.parent_controller = parent_controller
        self.index = index
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("CellWidget { border: 1px solid #444; margin-bottom: 5px; background-color: #252526; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header (Type, Actions)
        header_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["code", "markdown", "raw"])
        self.type_combo.setStyleSheet("padding: 2px;")
        
        btn_delete = QPushButton("Delete")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("background-color: #cc3333; color: white; padding: 4px; border: none;")
        btn_delete.clicked.connect(self.request_delete)
        
        header_layout.addWidget(QLabel(f"Cell [{self.index}]"))
        header_layout.addWidget(self.type_combo)
        header_layout.addStretch()
        header_layout.addWidget(btn_delete)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 14px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
            }
        """)
        self.editor.setMinimumHeight(100)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.editor)
        
    def load_data(self):
        # type combo could throw error if nbformat has arbitrary unknown type, but we handle safe ones
        idx = self.type_combo.findText(self.cell_data.cell_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        else:
            self.type_combo.addItems([self.cell_data.cell_type])
            self.type_combo.setCurrentText(self.cell_data.cell_type)
            
        self.editor.setPlainText(self.cell_data.source)
        
    def request_delete(self):
        self.parent_controller.delete_cell(self.index)
        
    def sync_data(self):
        new_type = self.type_combo.currentText()
        if self.cell_data.cell_type != new_type:
            # Type changed, nbformat expects a proper dictionary structure for different types
            self.cell_data.cell_type = new_type
            if new_type == "code" and "execution_count" not in self.cell_data:
                self.cell_data["execution_count"] = None
                self.cell_data["outputs"] = []
        self.cell_data.source = self.editor.toPlainText()

class NotebookIdeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.backend = NotebookBackend()
        self.cell_widgets = []
        self.setup_ui()
        self.handle_new() # Create an empty notebook
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header / Toolbar
        toolbar = QHBoxLayout()
        
        btn_new = QPushButton("New")
        btn_new.clicked.connect(self.handle_new)
        
        btn_open = QPushButton("Open")
        btn_open.clicked.connect(self.handle_open)
        
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.handle_save)
        
        btn_save_as = QPushButton("Save As")
        btn_save_as.clicked.connect(self.handle_save_as)
        
        btn_add_cell = QPushButton("+ Add Cell")
        btn_add_cell.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_cell.setStyleSheet("background-color: #2da042; color: white; font-weight: bold;")
        btn_add_cell.clicked.connect(self.add_cell)
        
        self.status_label = QLabel("No file loaded")
        self.status_label.setStyleSheet("color: #888;")
        
        for btn in [btn_new, btn_open, btn_save, btn_save_as]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    background-color: #333;
                    color: #ccc;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover { background-color: #444; }
            """)
            toolbar.addWidget(btn)
            
        toolbar.addStretch()
        toolbar.addWidget(btn_add_cell)
        
        # Scroll Area for Cells
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        self.cells_container = QWidget()
        self.cells_layout = QVBoxLayout(self.cells_container)
        self.cells_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.cells_container)
        
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.status_label)

    def handle_new(self):
        self.backend.new_notebook()
        self.status_label.setText("New un-saved notebook")
        self.render_cells()
        
    def handle_open(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Notebook", "", "Jupyter Notebooks (*.ipynb);;All Files (*)")
        if filepath:
            success, msg, _ = self.backend.load_notebook(filepath)
            if success:
                self.status_label.setText(f"Loaded: {filepath}")
                self.render_cells()
            else:
                QMessageBox.critical(self, "Error", msg)
                
    def handle_save(self):
        self.sync_all_cells()
        if not self.backend.current_filepath:
            self.handle_save_as()
            return
            
        success, msg = self.backend.save_notebook()
        if success:
            self.status_label.setText(f"Saved: {self.backend.current_filepath}")
        else:
            QMessageBox.critical(self, "Error", msg)
            
    def handle_save_as(self):
        self.sync_all_cells()
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Notebook As", "", "Jupyter Notebooks (*.ipynb)")
        if filepath:
            if not filepath.endswith(".ipynb"):
                filepath += ".ipynb"
            success, msg = self.backend.save_notebook(filepath)
            if success:
                self.status_label.setText(f"Saved: {filepath}")
            else:
                QMessageBox.critical(self, "Error", msg)

    def add_cell(self):
        if not self.backend.notebook:
            return
        
        self.sync_all_cells()
        # Add a new code cell by default
        new_cell = nbformat.v4.new_code_cell()
        self.backend.notebook.cells.append(new_cell)
        self.render_cells()

    def delete_cell(self, index):
        if not self.backend.notebook:
            return
            
        self.sync_all_cells()
        if 0 <= index < len(self.backend.notebook.cells):
            del self.backend.notebook.cells[index]
            self.render_cells()

    def sync_all_cells(self):
        """Update the underlying notebook object with UI content."""
        for cw in self.cell_widgets:
            cw.sync_data()

    def render_cells(self):
        # Clear existing
        for i in reversed(range(self.cells_layout.count())): 
            widget = self.cells_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
                
        self.cell_widgets.clear()
        
        if not self.backend.notebook:
            return
            
        for i, cell in enumerate(self.backend.notebook.cells):
            cw = CellWidget(cell, self, i)
            self.cells_layout.addWidget(cw)
            self.cell_widgets.append(cw)
