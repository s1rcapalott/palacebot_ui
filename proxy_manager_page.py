from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QComboBox, QTextEdit, QGroupBox, QGridLayout, QTableWidget,
    QTableWidgetItem, QSpacerItem, QSizePolicy
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
                padding: 10px 16px;
                font-weight: bold;           
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
            QComboBox:hover {
                border: 1px solid #778DA9;               
            }
            QGroupBox {
                border: 1px solid #415A77;
                margin-top: 10px;
                padding: 10px;               
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 10px;
                color: #E0E1DD;
                font-weight: bold;
            }
            QPushButton#backButton {
                background-color: #415A77;
                color: #E0E1DD;
                border-radius: 6px;
                padding: 10px 20px;              
            }
            QPushButton#backButton:hover {
                background-color: #778DA9;               
            }
            QHeaderView::section {
                background-color: #1B263B;
                color: #E0E1DD;
                font-weight: bold;
                border: none;               
            }
            QTableWidget {
                background-color: #1B263B;
                color: #E0E1DD;
                gridline-color: #415A77;
                border: 1px solid #415A77;               
            }
            QTableWidget::item:selected{
                background-color: #778DA9;
                color: #0D1B2A;               
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        #Header
        title = QLabel("Proxy Manager")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setContentsMargins(0, 0, 0, 10)
        main_layout.addWidget(title)

        #Input Section
        self.input_section = QGroupBox("Add / Manage Proxies")
        input_layout = QGridLayout()
        input_layout.setHorizontalSpacing(12)
        input_layout.setVerticalSpacing(12)

        #Add proxy section
        input_layout.addWidget(QLabel("Proxy:"), 0, 0)
        self.proxy_input = QLineEdit()
        self.proxy_input.setFixedWidth(250)
        input_layout.addWidget(self.proxy_input, 0, 1)

        input_layout.addWidget(QLabel("Group:"), 0, 2)
        self.group_select = QComboBox()
        self.group_select.setFixedWidth(250)
        input_layout.addWidget(self.group_select, 0, 3)

        self.add_button = QPushButton("Add Proxy")
        self.add_button.clicked.connect(self.handle_add_proxy)
        input_layout.addWidget(self.add_button, 0, 4)

        #Create/Remove Group
        input_layout.addWidget(QLabel("New Group:"), 1, 0)
        self.group_input = QLineEdit()
        self.group_input.setFixedWidth(250)
        input_layout.addWidget(self.group_input, 1, 1)

        self.create_group_button = QPushButton("Create Group")
        self.create_group_button.clicked.connect(self.handle_create_group)
        input_layout.addWidget(self.create_group_button, 1, 2)

        self.remove_button = QPushButton("Remove Group")
        self.remove_button.clicked.connect(self.handle_remove_group)
        input_layout.addWidget(self.remove_button, 1, 3)

        self.input_section.setLayout(input_layout)
        main_layout.addWidget(self.input_section)

        #Test proxies button
        self.test_button = QPushButton("Test Proxies")
        self.test_button.clicked.connect(lambda: run_async_task(self.handle_test_proxies()))
        input_layout.addWidget(self.test_button, 1, 4)

        #How logs will appear
        self.log_section = QGroupBox("Proxy Log")
        log_layout = QVBoxLayout()

        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("color: #E0E1DD; font-size: 12px;")
        log_layout.addWidget(self.status_label)

        self.log_area = QTextEdit()
        self.log_area.setMinimumHeight(120)
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Proxy logs appear here")
        log_layout.addWidget(self.log_area)

        self.log_section.setLayout(log_layout)
        main_layout.addWidget(self.log_section)

        #Proxy table section
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(4)
        self.proxy_table.setHorizontalHeaderLabels(["Proxy", "Ping", "Health", "Tags"])
        self.proxy_table.horizontalHeader().setStretchLastSection(True)
        self.proxy_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.proxy_table)

        #spacer(home button always at the bottom)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(spacer)

        #Back to home button
        self.back_button = QPushButton("Back to Home")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(lambda: self.switch_page_callback("home"))
        main_layout.addWidget(self.back_button)

        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.load_groups()

        self.group_select.currentIndexChanged.connect(self.update_proxy_table)

    def load_groups(self):
        print("Called load_groups()")
        print("Proxy groups loaded: ", self.proxy_manager.proxylist)
        self.group_select.clear()
        for group in self.proxy_manager.proxylist.get("Groups", []):
            self.group_select.addItem(group["group_name"])
        
        self.update_proxy_table()
    
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

        print("create_group is:", self.proxy_manager.creat_group)

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

    @asyncSlot()
    async def handle_test_proxies(self):
        group = self.group_select.currentText().strip()
        if not group:
            self.log_area.append("Please select a group to test.")
            return
        
        self.log_area.append(f"Testing proxies in group '{group}'...")
        proxies = []
        for g in self.proxy_manager.proxylist.get("Groups", []):
            if g["group_name"] == group:
                proxies = g.get("proxies", [])
                break
            if not proxies:
                self.log_area.append(f"No proxies found in group '{group}'.")
                return

            for proxy in proxies:
                result = await self.proxy_manager.ping_proxy(proxy["proxy"])
                if result["success"]:
                    self.log_area.append(f"{proxy['proxy']} is working (Ping: {result['ping']}s)")
                else:
                    self.log_area.append(f"{proxy['proxy']} failed to respond.")

    def display_proxies_for_group(self, group_name):
        proxies = []
        for group in self.proxy_manager.proxylist.get("Groups", []):
            if group["group_name"] == group_name:
                proxies = group.get("proxies", [])
                break

        self.proxy_table.setRowCount(len(proxies))
        for i, proxy_data in enumerate(proxies):
            self.proxy_table.setItem(i, 0, QTableWidgetItem(proxy_data.get("proxy", "")))
            self.proxy_table.setItem(i, 1, QTableWidgetItem(str(proxy_data.get("last_checked_ping", "N/A"))))
            self.proxy_table.setItem(i, 2, QTableWidgetItem(str(proxy_data.get("healthscore", "N/A"))))
            self.proxy_table.setItem(i, 3, QTableWidgetItem(", ".join(proxy_data.get("tags", []))))

    def update_proxy_table(self):
        selected_group = self.group_select.currentText()
        if selected_group:
            self.display_proxies_for_group(selected_group)