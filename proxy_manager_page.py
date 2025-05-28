from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from qasync import asyncSlot
import asyncio
import threading

def run_async_task(coro):
    def runner():
        asyncio.run(coro)
    threading.Thread(target=runner).start()

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
            QPushButton#backButton {
                background-color: #415A77;
                color: #E0E1DD;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;               
            }
            QPushButton#backButton:hover {
                background-color: #778DA9;               
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

        #Create group
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("New group name")
        input_layout.addWidget(self.group_input)

        self.create_group_button = QPushButton("Create Group")
        self.create_group_button.clicked.connect(self.handle_create_group)
        input_layout.addWidget(self.create_group_button)

        #Remove group
        self.remove_button = QPushButton("Remove Group")
        input_layout.addWidget(self.remove_button)
        self.remove_button.clicked.connect(self.handle_remove_group)

        #Output log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Proxy logs appear here")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.load_groups()

        #Back to home
        self.back_button = QPushButton("Back to Home")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(lambda: self.switch_page_callback("home"))
        layout.addWidget(self.back_button)

    def load_groups(self):
        print("Called load_groups()")
        print("Proxy groups loaded: ", self.proxy_manager.proxylist)
        self.group_select.clear()
        for group in self.proxy_manager.proxylist.get("Groups", []):
            self.group_select.addItem(group["group_name"])
    
    @asyncSlot()
    async def handle_add_proxy(self):
        proxy = self.proxy_input.text().strip()
        group = self.group_select.currentText().strip()

        if not proxy or not group:
            self.log_area.append("Please enter a proxy and select a group.")
            return
        
        self.log_area.append(f"Adding proxy '{proxy}' to group '{group}'...")

        result = await self.proxy_manager.add_proxy(proxy, group)
        if result:
            self.log_area.append("Proxy added successfully.")
            self.proxy_input.clear()
        else:
            self.log_area.append("Failed to add proxy.")

    @asyncSlot()
    async def handle_create_group(self):
        group_name = self.group_input.text().strip()
        if not group_name:
            self.log_area.append("Please enter a group name.")
            return
        
        self.log_area.append(f"Creating group '{group_name}'...")

        result = await self.proxy_manager.create_group(group_name)
        if result:
            self.log_area.append(f"Group '{group_name}' created successfully.")
            self.load_groups()
            self.group_input.clear()
        else:
            self.log_area.append(f"Failed to create group '{group_name}'.")
    
    @asyncSlot()
    async def handle_remove_group(self):
        group = self.group_select.currentText().strip()

        if not group:
            self.log_area.append("Please select a group to remove.")
            return
        
        if group == "default":
            self.log_area.append("You cannot remove the 'default' group.")
            return
        
        self.log_area.append(f"Removing group '{group}'...")

        print("Calling delete_group now...")
        removed = await self.proxy_manager.delete_group(group)
        print(f"Result of delete_group: {removed}")
        if removed:
            self.log_area.append(f"Group '{group}' removed.")
            self.load_groups()
        else:
            self.log_area.append(f"Failed to remove group '{group}'.")