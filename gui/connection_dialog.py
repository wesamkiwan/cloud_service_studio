import uuid
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QLabel, QLineEdit, QComboBox, QStackedWidget, QWidget, QFormLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from core.connection_manager import ConnectionManager

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Connections")
        self.setMinimumSize(600, 400)
        self.conn_mgr = ConnectionManager()
        self.current_id = None
        self.setup_ui()
        self.load_list()

    def setup_ui(self):
        # Professional darker style for dialog
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QLabel { color: #cccccc; }
            QLineEdit, QComboBox, QListWidget {
                background-color: #252526; 
                color: #d4d4d4; 
                border: 1px solid #3c3c3c;
                padding: 4px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover { background-color: #1177bb; }
            QPushButton:disabled { background-color: #333333; color: #888888; }
            QListWidget::item:selected { background-color: #37373d; color: #ffffff; }
        """)

        main_layout = QHBoxLayout(self)

        # Left: List of connections
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self.on_add_clicked)
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)

        left_layout.addWidget(QLabel("Saved Connections:"))
        left_layout.addWidget(self.list_widget)
        left_layout.addLayout(btn_layout)

        # Right: Edit form
        right_layout = QVBoxLayout()
        self.form_widget = QWidget()
        form_layout = QFormLayout(self.form_widget)
        
        self.name_input = QLineEdit()
        self.service_combo = QComboBox()
        self.service_combo.addItems(["sql", "mongodb", "redis", "s3", "api"])
        
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(["uri", "basic"])
        self.auth_combo.currentTextChanged.connect(self.on_auth_type_changed)

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Service Type:", self.service_combo)
        form_layout.addRow("Auth Type:", self.auth_combo)

        # Dynamic auth inputs
        self.auth_stack = QStackedWidget()
        
        # URI Widget
        self.uri_widget = QWidget()
        uri_layout = QFormLayout(self.uri_widget)
        self.uri_input = QLineEdit()
        uri_layout.addRow("Connection String:", self.uri_input)
        
        # Basic Auth Widget
        self.basic_widget = QWidget()
        basic_layout = QFormLayout(self.basic_widget)
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_input = QLineEdit()
        
        basic_layout.addRow("Host:", self.host_input)
        basic_layout.addRow("Port:", self.port_input)
        basic_layout.addRow("Username:", self.user_input)
        basic_layout.addRow("Password:", self.pass_input)
        basic_layout.addRow("Database:", self.db_input)

        self.auth_stack.addWidget(self.uri_widget)
        self.auth_stack.addWidget(self.basic_widget)

        right_layout.addWidget(self.form_widget)
        right_layout.addWidget(self.auth_stack)

        self.btn_save = QPushButton("Save Connection")
        self.btn_save.clicked.connect(self.on_save_clicked)
        right_layout.addStretch()
        right_layout.addWidget(self.btn_save)

        self.form_widget.setEnabled(False)
        self.auth_stack.setEnabled(False)
        self.btn_save.setEnabled(False)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=2)

    def load_list(self):
        self.list_widget.clear()
        for conn in self.conn_mgr.get_all():
            item = QListWidgetItem(conn.get('name', 'Unnamed'))
            item.setData(Qt.ItemDataRole.UserRole, conn.get('id'))
            self.list_widget.addItem(item)

    def on_selection_changed(self, index):
        if index < 0:
            self.current_id = None
            self.clear_form()
            self.form_widget.setEnabled(False)
            self.auth_stack.setEnabled(False)
            self.btn_save.setEnabled(False)
            return

        item = self.list_widget.item(index)
        self.current_id = item.data(Qt.ItemDataRole.UserRole)
        conn = self.conn_mgr.get_connection(self.current_id)
        if conn:
            self.form_widget.setEnabled(True)
            self.auth_stack.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.name_input.setText(conn.get('name', ''))
            self.service_combo.setCurrentText(conn.get('service_type', 'sql'))
            auth_type = conn.get('auth_type', 'uri')
            self.auth_combo.setCurrentText(auth_type)
            
            self.uri_input.setText(conn.get('uri', ''))
            self.host_input.setText(conn.get('host', ''))
            self.port_input.setText(str(conn.get('port', '')))
            self.user_input.setText(conn.get('username', ''))
            self.pass_input.setText(conn.get('password', ''))
            self.db_input.setText(conn.get('database', ''))

    def clear_form(self):
        self.name_input.clear()
        self.uri_input.clear()
        self.host_input.clear()
        self.port_input.clear()
        self.user_input.clear()
        self.pass_input.clear()
        self.db_input.clear()

    def on_add_clicked(self):
        self.list_widget.clearSelection()
        self.current_id = None
        self.clear_form()
        self.form_widget.setEnabled(True)
        self.auth_stack.setEnabled(True)
        self.btn_save.setEnabled(True)

    def on_delete_clicked(self):
        if not self.current_id:
            return
        if self.conn_mgr.delete_connection(self.current_id):
            self.load_list()

    def on_auth_type_changed(self, text):
        if text == "uri":
            self.auth_stack.setCurrentIndex(0)
        else:
            self.auth_stack.setCurrentIndex(1)

    def on_save_clicked(self):
        data = {
            'name': self.name_input.text().strip() or "Unnamed",
            'service_type': self.service_combo.currentText(),
            'auth_type': self.auth_combo.currentText()
        }
        if data['auth_type'] == 'uri':
            data['uri'] = self.uri_input.text().strip()
        else:
            data['host'] = self.host_input.text().strip()
            p = self.port_input.text().strip()
            data['port'] = int(p) if p.isdigit() else ""
            data['username'] = self.user_input.text().strip()
            data['password'] = self.pass_input.text().strip()
            data['database'] = self.db_input.text().strip()

        if self.current_id:
            self.conn_mgr.update_connection(self.current_id, data)
        else:
            self.current_id = self.conn_mgr.add_connection(data)

        self.load_list()
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == self.current_id:
                self.list_widget.setCurrentRow(i)
                break
