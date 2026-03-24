import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QSplitter, 
    QMessageBox, QTreeWidget, QTreeWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt
from .backend import MongoBackend
from .highlighter import JsonHighlighter
from core.connection_manager import ConnectionManager

class MongoIdeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.backend = MongoBackend()
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
        
        # Selectors Header
        selectors_layout = QHBoxLayout()
        self.db_combo = QComboBox()
        self.db_combo.setStyleSheet("padding: 3px;")
        self.db_combo.currentTextChanged.connect(self.handle_db_change)
        
        self.col_combo = QComboBox()
        self.col_combo.setStyleSheet("padding: 3px;")
        self.col_combo.currentTextChanged.connect(self.handle_col_change)
        
        self.btn_refresh = QPushButton("Refresh List")
        self.btn_refresh.clicked.connect(self.refresh_dbs)
        
        selectors_layout.addWidget(QLabel("Database:"))
        selectors_layout.addWidget(self.db_combo, stretch=1)
        selectors_layout.addWidget(QLabel("Collection:"))
        selectors_layout.addWidget(self.col_combo, stretch=1)
        selectors_layout.addWidget(self.btn_refresh)
        
        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Query Editor
        query_widget = QWidget()
        query_layout = QVBoxLayout(query_widget)
        query_layout.setContentsMargins(0, 0, 0, 0)
        
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("Filter JSON layout e.g. {\"status\": \"active\"}")
        self.query_editor.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace; 
                font-size: 14px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
            }
        """)
        self.highlighter = JsonHighlighter(self.query_editor.document())
        
        btn_find = QPushButton("Find (F5)")
        btn_find.setShortcut("F5")
        btn_find.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_find.clicked.connect(self.run_query)
        btn_find.setStyleSheet("background-color: #2da042; color: white; padding: 8px; border: none; font-weight: bold;")
        
        query_layout.addWidget(QLabel("Filter Dictionary:"))
        query_layout.addWidget(self.query_editor)
        query_layout.addWidget(btn_find)
        
        # Document Tree View
        self.doc_tree = QTreeWidget()
        self.doc_tree.setHeaderLabels(["Field", "Value"])
        self.doc_tree.setStyleSheet("""
            QTreeWidget { 
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 4px;
                border: 1px solid #333;
            }
        """)
        
        splitter.addWidget(query_widget)
        splitter.addWidget(self.doc_tree)
        splitter.setSizes([150, 450])
        
        main_layout.addLayout(conn_layout)
        main_layout.addLayout(selectors_layout)
        main_layout.addWidget(splitter)
        
    def refresh_connections(self):
        self.conn_mgr.load_connections()
        self.conn_combo.clear()
        conns = self.conn_mgr.get_by_service('mongodb')
        for c in conns:
            self.conn_combo.addItem(c.get('name', 'Unnamed'), c.get('id'))

    def handle_connect(self):
        conn_id = self.conn_combo.currentData()
        if not conn_id:
            QMessageBox.warning(self, "No Connection", "Please select a generated MongoDB connection.")
            return
            
        conn_profile = self.conn_mgr.get_connection(conn_id)
        if not conn_profile: return
        
        success, msg = self.backend.connect(conn_profile)
        if success:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #33cc33; font-weight: bold;")
            self.refresh_dbs()
        else:
            self.status_label.setText("Connection Failed")
            self.status_label.setStyleSheet("color: #cc3333; font-weight: bold;")
            QMessageBox.critical(self, "Error", msg)
            
    def refresh_dbs(self):
        self.db_combo.clear()
        dbs = self.backend.get_databases()
        self.db_combo.addItems(dbs)
        
    def handle_db_change(self, db_name):
        self.col_combo.clear()
        if db_name:
            cols = self.backend.get_collections(db_name)
            self.col_combo.addItems(cols)
            
    def handle_col_change(self, col_name):
        db_name = self.db_combo.currentText()
        if db_name and col_name:
            self.backend.set_db_col(db_name, col_name)
            
    def run_query(self):
        query_str = self.query_editor.toPlainText().strip()
        filter_dict = {}
        if query_str:
            try:
                # Need to use strict JSON for now
                filter_dict = json.loads(query_str)
            except Exception as e:
                QMessageBox.critical(self, "Invalid JSON", f"Filter must be valid JSON: {e}")
                return
                
        success, msg, docs = self.backend.query_documents(filter_dict)
        if success:
            self._populate_tree(docs)
            self.status_label.setText(msg[:60])
        else:
            QMessageBox.critical(self, "Query Error", msg)
            
    def _populate_tree(self, docs):
        self.doc_tree.clear()
        for doc in docs:
            # Create a top-level item for the document
            doc_id = str(doc.get('_id', 'Document'))
            root_item = QTreeWidgetItem([f"Document {doc_id}", ""])
            self.doc_tree.addTopLevelItem(root_item)
            self._dict_to_tree(doc, root_item)
            
    def _dict_to_tree(self, data_dict, parent_item):
        for key, value in data_dict.items():
            if isinstance(value, dict):
                item = QTreeWidgetItem([str(key), "{...}"])
                parent_item.addChild(item)
                self._dict_to_tree(value, item)
            elif isinstance(value, list):
                item = QTreeWidgetItem([str(key), "[...]"])
                parent_item.addChild(item)
                for i, v in enumerate(value):
                    if isinstance(v, dict):
                        sub_item = QTreeWidgetItem([f"[{i}]", "{...}"])
                        item.addChild(sub_item)
                        self._dict_to_tree(v, sub_item)
                    else:
                        sub_item = QTreeWidgetItem([f"[{i}]", str(v)])
                        item.addChild(sub_item)
            else:
                item = QTreeWidgetItem([str(key), str(value)])
                parent_item.addChild(item)

    def cleanup(self):
        self.backend.disconnect()
