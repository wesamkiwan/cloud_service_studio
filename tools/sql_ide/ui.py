from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QSplitter, QMessageBox, QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt
from .backend import SqlBackend
from .highlighter import SqlHighlighter
from core.connection_manager import ConnectionManager

class SqlIdeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.backend = SqlBackend()
        self.conn_mgr = ConnectionManager()
        self.setup_ui()
        self.refresh_connections()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Connection Header
        conn_layout = QHBoxLayout()
        self.conn_combo = QComboBox()
        self.conn_combo.setStyleSheet("padding: 5px; font-size: 13px; border: 1px solid #444;")
        
        self.btn_refresh_conns = QPushButton("Refresh")
        self.btn_refresh_conns.clicked.connect(self.refresh_connections)
        self.btn_refresh_conns.setStyleSheet("background-color: #555; color: white; padding: 5px; border: none;")

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_connect.setStyleSheet("background-color: #0e639c; color: white; padding: 5px 15px; border: none;")
        self.btn_connect.clicked.connect(self.handle_connect)
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #cc3333; font-weight: bold;")
        
        conn_layout.addWidget(QLabel("Connection:"))
        conn_layout.addWidget(self.conn_combo, stretch=1)
        conn_layout.addWidget(self.btn_refresh_conns)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.status_label)
        
        # Main Splitter (Query Editor Top, Results Bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Query Editor
        query_widget = QWidget()
        query_layout = QVBoxLayout(query_widget)
        query_layout.setContentsMargins(0, 0, 0, 0)
        
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("SELECT * FROM ...")
        self.query_editor.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace; 
                font-size: 14px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
            }
        """)
        self.highlighter = SqlHighlighter(self.query_editor.document())
        
        btn_run = QPushButton("Execute (F5)")
        btn_run.setShortcut("F5")
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.clicked.connect(self.run_query)
        btn_run.setStyleSheet("background-color: #2da042; color: white; padding: 8px; border: none; font-weight: bold;")
        
        query_layout.addWidget(self.query_editor)
        query_layout.addWidget(btn_run)
        
        # Results View
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget { 
                background-color: #1e1e1e;
                color: #d4d4d4;
                gridline-color: #333333;
                border: 1px solid #333;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 4px;
                border: 1px solid #333;
            }
        """)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        splitter.addWidget(query_widget)
        splitter.addWidget(self.table_widget)
        splitter.setSizes([200, 400])
        
        main_layout.addLayout(conn_layout)
        main_layout.addWidget(splitter)
        
    def refresh_connections(self):
        self.conn_mgr.load_connections()
        self.conn_combo.clear()
        conns = self.conn_mgr.get_by_service('sql')
        for c in conns:
            self.conn_combo.addItem(c.get('name', 'Unnamed'), c.get('id'))

    def handle_connect(self):
        conn_id = self.conn_combo.currentData()
        if not conn_id:
            QMessageBox.warning(self, "No Connection", "Please select a generated SQL connection.")
            return

        conn_profile = self.conn_mgr.get_connection(conn_id)
        if not conn_profile:
            return
            
        success, msg = self.backend.connect(conn_profile)
        if success:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #33cc33; font-weight: bold;")
        else:
            self.status_label.setText("Connection Failed")
            self.status_label.setStyleSheet("color: #cc3333; font-weight: bold;")
            QMessageBox.critical(self, "Error", msg)
            
    def run_query(self):
        query = self.query_editor.toPlainText().strip()
        if not query:
            return
            
        success, msg, columns, data = self.backend.execute_query(query)
        
        if success:
            self._populate_table(columns, data)
            # QMessageBox.information(self, "Success", msg) # Too annoying for quick queries
            self.status_label.setText(msg[:60]) # Show brief status message
        else:
            QMessageBox.critical(self, "Query Error", msg)
            
    def _populate_table(self, columns, data):
        self.table_widget.clear()
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setRowCount(len(data))
        self.table_widget.setHorizontalHeaderLabels(columns)
        
        for row_idx, row_data in enumerate(data):
            for col_idx, col_value in enumerate(row_data):
                item = QTableWidgetItem(str(col_value))
                self.table_widget.setItem(row_idx, col_idx, item)
                
    def cleanup(self):
        self.backend.disconnect()
