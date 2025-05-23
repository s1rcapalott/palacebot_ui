from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ProxyManagerPage(QWidget):
    def __init__(self, proxy_manager):
        super().__init__()
        self.proxy_manager = proxy_manager

        self.setStyleSheet("""
            QWidget {
                background-color: #0D1B2A;
                color: #E0E1DD;                
            }
            QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit {
                font-size: 14px;
            }
            QPushButton {
                background-color: #415A77;
                border: none;
                border-radius: 8px;
                padding: 10px;                
            }
            QPushButton:hover {
                background-color: #778DA9;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #1B263B;
                border-radius: 6px;
                border: 1px solid #415A77;
                padding: 6px;
                color: white;                
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("Proxy Manager")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        #input Field and group selector
        input_layout = QHBoxLayout()

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("Enter proxy")
        input_layout.addWidget(self.proxy_input)

        self.group_select = QComboBox()
        self.group_select.addItem("default") #place holder
        input_layout.addWidget(self.group_select)

        self.add_button = QPushButton("Add Proxy")
        input_layout.addWidget(self.add_button)

        layout.addLayout(input_layout)

        #Output log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Proxy logs appear here")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.load_groups()

    def load_groups(self):
        print("Called load_groups()")
        print("Proxy groups loaded: ", self.proxy_manager.proxylist)
        self.group_select.clear()
        for group in self.proxy_manager.proxylist.get("Groups", []):
            self.group_select.addItem(group["group_name"])