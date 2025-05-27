from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import asyncio

class ProxyManagerPage(QWidget):
    def __init__(self, proxy_manager, switch_page_callback):
        super().__init__()
        self.proxy_manager = proxy_manager
        self.switch_page_callback = switch_page_callback

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
        self.add_button.clicked.connect(self.handle_add_proxy)

        layout.addLayout(input_layout)

        #Output log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Proxy logs appear here")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.load_groups()

        #Back to home
        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.switch_page_callback("home"))
        layout.addWidget(self.back_button)

    def load_groups(self):
        print("Called load_groups()")
        print("Proxy groups loaded: ", self.proxy_manager.proxylist)
        self.group_select.clear()
        for group in self.proxy_manager.proxylist.get("Groups", []):
            self.group_select.addItem(group["group_name"])
    
    def handle_add_proxy(self):
        proxy = self.proxy_input.text().strip()
        group = self.group_select.currentText().strip()

        if not proxy or not group:
            self.log_area.append("Please enter a proxy and select a group.")
            return
        
        self.log_area.append(f"Adding proxy '{proxy}' to group '{group}'...")

        async def add_and_log():
            result = await self.proxy_manager.add_proxy(proxy, group)
            if result:
                self.log_area.append(f"Proxy added successfully.")
                self.proxy_input.clear()
            else:
                self.log_area.append(f"Failed to add proxy")

        asyncio.run(add_and_log())