from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QComboBox, QTextEdit, QGroupBox, QGridLayout, QTableWidget,
    QTableWidgetItem, QSpacerItem, QSizePolicy, QFrame, QHeaderView
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
                background-color: #0a0e14;
                color: #e4e6eb;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Top Navigation Bar */
            QFrame#navBar {
                background-color: #141b24;
                border-bottom: 1px solid #1e2835;
            }
            
            /* Navigation Buttons */
            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                color: #8b92a0;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            
            QPushButton#navButton:hover {
                color: #e4e6eb;
                background-color: #1a2332;
            }
            
            QPushButton#navButton:checked {
                color: #e4e6eb;
                border-bottom: 3px solid #00d9ff;
                background-color: #1a2332;
            }
            
            /* Action Buttons (Import/Export) */
            QPushButton#actionButton {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                color: #e4e6eb;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            
            QPushButton#actionButton:hover {
                background-color: #2a3544;
                border: 1px solid #3a4554;
            }
            
            /* Group Boxes */
            QGroupBox {
                background-color: #141b24;
                border: 1px solid #1e2835;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #e4e6eb;
                background-color: #141b24;
            }
            
            /* Input Fields */
            QLineEdit, QComboBox {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e4e6eb;
                font-size: 13px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00d9ff;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b92a0;
                margin-right: 5px;
            }
            
            /* Primary Buttons */
            QPushButton#primaryBtn {
                background-color: #00d9ff;
                border: none;
                border-radius: 6px;
                color: #0a0e14;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            
            QPushButton#primaryBtn:hover {
                background-color: #00b8d9;
            }
            
            /* Secondary Buttons */
            QPushButton#secondaryBtn {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                color: #e4e6eb;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            
            QPushButton#secondaryBtn:hover {
                background-color: #2a3544;
            }
            
            /* Danger Buttons */
            QPushButton#dangerBtn {
                background-color: #3d1f1f;
                border: none;
                border-radius: 6px;
                color: #ff4444;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            
            QPushButton#dangerBtn:hover {
                background-color: #4d2929;
            }
            
            /* Test Button */
            QPushButton#testBtn {
                background-color: #1f3d3d;
                border: none;
                border-radius: 6px;
                color: #00d9ff;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            
            QPushButton#testBtn:hover {
                background-color: #294d4d;
            }
            
            /* Text Edit (Log Area) */
            QTextEdit {
                background-color: #0a0e14;
                border: 1px solid #1e2835;
                border-radius: 6px;
                padding: 10px;
                color: #8b92a0;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            
            /* Status Label */
            QLabel#statusLabel {
                color: #00d9ff;
                font-size: 12px;
                font-weight: 600;
                padding: 5px 0;
            }
            
            /* Table Styling */
            QTableWidget {
                background-color: #0a0e14;
                border: 1px solid #1e2835;
                border-radius: 8px;
                gridline-color: #1e2835;
                selection-background-color: #1a2332;
            }
            
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #1e2835;
                color: #e4e6eb;
            }
            
            QTableWidget::item:selected {
                background-color: #1a2332;
            }
            
            QHeaderView::section {
                background-color: #141b24;
                color: #8b92a0;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #1e2835;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === TOP NAVIGATION BAR ===
        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav_bar.setFixedHeight(60)
        nav_bar_layout = QHBoxLayout(nav_bar)
        nav_bar_layout.setContentsMargins(20, 0, 20, 0)
        nav_bar_layout.setSpacing(0)

        # Logo/Brand
        brand_label = QLabel("Palace")
        brand_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        brand_label.setStyleSheet("color: #00d9ff; padding: 0 20px 0 0;")
        nav_bar_layout.addWidget(brand_label)

        # Navigation tabs
        nav_buttons_data = [
            ("Tasks", "tasks"),
            ("Proxies", "proxies"),
            ("Billing", "billing"),
            ("Accounts", "accounts"),
            ("Settings", None)
        ]
        
        for btn_text, page_key in nav_buttons_data:
            nav_btn = QPushButton(btn_text)
            nav_btn.setObjectName("navButton")
            nav_btn.setCheckable(True)
            if btn_text == "Proxies":  # Proxies is active
                nav_btn.setChecked(True)
            if page_key:
                nav_btn.clicked.connect(lambda checked, pk=page_key: self.switch_page_callback(pk))
            nav_bar_layout.addWidget(nav_btn)

        nav_bar_layout.addStretch()

        # Right side buttons
        import_btn = QPushButton("Import")
        import_btn.setObjectName("actionButton")
        nav_bar_layout.addWidget(import_btn)

        export_btn = QPushButton("Export")
        export_btn.setObjectName("actionButton")
        nav_bar_layout.addWidget(export_btn)

        main_layout.addWidget(nav_bar)

        # === CONTENT AREA ===
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Title
        title = QLabel("Proxy Manager")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        content_layout.addWidget(title)

        # === ADD/MANAGE PROXIES SECTION ===
        self.input_section = QGroupBox("Add & Manage Proxies")
        input_layout = QGridLayout()
        input_layout.setHorizontalSpacing(15)
        input_layout.setVerticalSpacing(15)

        # Row 1: Add Proxy
        proxy_label = QLabel("Proxy:")
        proxy_label.setStyleSheet("color: #8b92a0; font-size: 12px;")
        input_layout.addWidget(proxy_label, 0, 0, Qt.AlignmentFlag.AlignRight)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("host:port:user:pass or host:port")
        self.proxy_input.setMinimumWidth(250)
        input_layout.addWidget(self.proxy_input, 0, 1)

        group_label = QLabel("Group:")
        group_label.setStyleSheet("color: #8b92a0; font-size: 12px;")
        input_layout.addWidget(group_label, 0, 2, Qt.AlignmentFlag.AlignRight)
        
        self.group_select = QComboBox()
        self.group_select.setMinimumWidth(200)
        input_layout.addWidget(self.group_select, 0, 3)

        self.add_button = QPushButton("Add Proxy")
        self.add_button.setObjectName("primaryBtn")
        self.add_button.clicked.connect(self.handle_add_proxy)
        input_layout.addWidget(self.add_button, 0, 4)

        # Row 2: Group Management
        new_group_label = QLabel("New Group:")
        new_group_label.setStyleSheet("color: #8b92a0; font-size: 12px;")
        input_layout.addWidget(new_group_label, 1, 0, Qt.AlignmentFlag.AlignRight)
        
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Enter group name")
        self.group_input.setMinimumWidth(250)
        input_layout.addWidget(self.group_input, 1, 1)

        self.create_group_button = QPushButton("Create Group")
        self.create_group_button.setObjectName("secondaryBtn")
        self.create_group_button.clicked.connect(self.handle_create_group)
        input_layout.addWidget(self.create_group_button, 1, 2)

        self.remove_button = QPushButton("Remove Group")
        self.remove_button.setObjectName("dangerBtn")
        self.remove_button.clicked.connect(self.handle_remove_group)
        input_layout.addWidget(self.remove_button, 1, 3)

        self.test_button = QPushButton("Test Proxies")
        self.test_button.setObjectName("testBtn")
        self.test_button.clicked.connect(lambda: run_async_task(self.handle_test_proxies()))
        input_layout.addWidget(self.test_button, 1, 4)

        self.input_section.setLayout(input_layout)
        content_layout.addWidget(self.input_section)

        # === PROXY LOG SECTION ===
        self.log_section = QGroupBox("Proxy Activity Log")
        log_layout = QVBoxLayout()

        self.status_label = QLabel("● Status: Idle")
        self.status_label.setObjectName("statusLabel")
        log_layout.addWidget(self.status_label)

        self.log_area = QTextEdit()
        self.log_area.setMinimumHeight(120)
        self.log_area.setMaximumHeight(150)
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Proxy activity and test results will appear here...")
        log_layout.addWidget(self.log_area)

        self.log_section.setLayout(log_layout)
        content_layout.addWidget(self.log_section)

        # === PROXY TABLE SECTION ===
        table_header = QLabel("Proxy List")
        table_header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        content_layout.addWidget(table_header)

        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(4)
        self.proxy_table.setHorizontalHeaderLabels(["Proxy", "Ping (ms)", "Health Score", "Tags"])
        
        header = self.proxy_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.proxy_table.setColumnWidth(1, 120)
        self.proxy_table.setColumnWidth(2, 120)
        
        self.proxy_table.verticalHeader().setVisible(False)
        self.proxy_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.proxy_table.setShowGrid(False)
        self.proxy_table.setAlternatingRowColors(True)
        
        content_layout.addWidget(self.proxy_table)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        
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
            self.log_area.append("❌ Error: Please enter a proxy and select a group.")
            return
        
        self.log_area.append(f"Adding proxy '{proxy}' to group '{group}'...")
        self.status_label.setText("● Status: Adding proxy...")

        result = await self.proxy_manager.add_proxy(proxy, group)
        if result:
            self.log_area.append(f"✅ Proxy added successfully to '{group}'")
            self.status_label.setText("● Status: Proxy added")
            self.proxy_input.clear()
            self.update_proxy_table()
        else:
            self.log_area.append("❌ Failed to add proxy.")
            self.status_label.setText("● Status: Failed")

    @asyncSlot()
    async def handle_create_group(self):
        group_name = self.group_input.text().strip()
        if not group_name:
            self.log_area.append("❌ Error: Please enter a group name.")
            return
        
        self.log_area.append(f"Creating group '{group_name}'...")
        self.status_label.setText("● Status: Creating group...")

        result = await self.proxy_manager.create_group(group_name)
        if result:
            self.log_area.append(f"✅ Group '{group_name}' created successfully.")
            self.status_label.setText("● Status: Group created")
            self.load_groups()
            self.group_input.clear()
        else:
            self.log_area.append(f"❌ Failed to create group '{group_name}'.")
            self.status_label.setText("● Status: Failed")
    
    @asyncSlot()
    async def handle_remove_group(self):
        group = self.group_select.currentText().strip()

        if not group:
            self.log_area.append("❌ Error: Please select a group to remove.")
            return
        
        if group == "default":
            self.log_area.append("❌ Error: Cannot remove the 'default' group.")
            return
        
        self.log_area.append(f"Removing group '{group}'...")
        self.status_label.setText("● Status: Removing group...")

        removed = await self.proxy_manager.delete_group(group)
        if removed:
            self.log_area.append(f"✅ Group '{group}' removed.")
            self.status_label.setText("● Status: Group removed")
            self.load_groups()
        else:
            self.log_area.append(f"❌ Failed to remove group '{group}'.")
            self.status_label.setText("● Status: Failed")

    @asyncSlot()
    async def handle_test_proxies(self):
        group = self.group_select.currentText().strip()
        if not group:
            self.log_area.append("❌ Error: Please select a group to test.")
            return
        
        self.log_area.append(f"Testing proxies in group '{group}'...")
        self.status_label.setText("● Status: Testing proxies...")
        
        proxies = []
        for g in self.proxy_manager.proxylist.get("Groups", []):
            if g["group_name"] == group:
                proxies = g.get("proxies", [])
                break
        
        if not proxies:
            self.log_area.append(f"❌ No proxies found in group '{group}'.")
            self.status_label.setText("● Status: No proxies")
            return

        for proxy in proxies:
            result = await self.proxy_manager.ping_proxy(proxy["proxy"])
            if result["success"]:
                self.log_area.append(f"✅ {proxy['proxy']} - Working (Ping: {result['ping']}ms)")
                await self.proxy_manager.update_proxy_stats(proxy['proxy'], group, status = "success")
                
                for g in self.proxy_manager.proxylist["Groups"]:
                    if g["group_name"] == group:
                        for p in g["proxies"]:
                            if p["proxy"] == proxy["proxy"]:
                                p["last_checked_ping"] = result["ping"]
                                break
            else:
                self.log_area.append(f"❌ {proxy['proxy']} - Failed to respond")
                await self.proxy_manager.update_proxy_stats(proxy['proxy'], group, status = "fail")
        
        await self.proxy_manager.save_proxies()
        self.update_proxy_table()
        self.log_area.append(f"✅ Testing complete for group '{group}'.")
        self.status_label.setText("● Status: Testing complete")

    def display_proxies_for_group(self, group_name):
        proxies = []
        for group in self.proxy_manager.proxylist.get("Groups", []):
            if group["group_name"] == group_name:
                proxies = group.get("proxies", [])
                break

        self.proxy_table.setRowCount(len(proxies))
        for i, proxy_data in enumerate(proxies):
            self.proxy_table.setItem(i, 0, QTableWidgetItem(proxy_data.get("proxy", "")))
            
            ping = proxy_data.get("last_checked_ping", "N/A")
            ping_item = QTableWidgetItem(str(ping) if ping != "N/A" else "N/A")
            self.proxy_table.setItem(i, 1, ping_item)
            
            health = proxy_data.get("healthscore", "N/A")
            health_item = QTableWidgetItem(str(health) if health != "N/A" else "N/A")
            self.proxy_table.setItem(i, 2, health_item)
            
            tags = ", ".join(proxy_data.get("tags", []))
            self.proxy_table.setItem(i, 3, QTableWidgetItem(tags if tags else "No tags"))
            
            self.proxy_table.setRowHeight(i, 45)

    def update_proxy_table(self):
        selected_group = self.group_select.currentText()
        if selected_group:
            self.display_proxies_for_group(selected_group)