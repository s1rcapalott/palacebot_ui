from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QLineEdit, QSpacerItem, QSizePolicy,QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from pathlib import Path
import json
import os
from datetime import datetime
import random
import asyncio
from qasync import asyncSlot
from selenium.webdriver.common.by import By


class TaskManagerPage(QWidget):
    def __init__(self, switch_page_callback, proxy_manager=None, billing_manager=None):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.proxy_manager = proxy_manager
        self.billing_manager = billing_manager
        
        self.tasks = []
        # FIXED: absolute path so it works from -m
        self.storage_path = Path(__file__).resolve().parent.parent / "backend" / "tasks.json"
        # fallback to project root if backend/tasks.json not found
        if not self.storage_path.exists():
            alt = Path(__file__).resolve().parent.parent.parent / "tasks.json"
            if alt.exists():
                self.storage_path = alt
        self.task_counter = 0
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0e14;
                color: #e4e6eb;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#navBar {
                background-color: #141b24;
                border-bottom: 1px solid #1e2835;
                padding: 0px;
            }
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
            QLineEdit#searchBox {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e4e6eb;
                font-size: 13px;
            }
            QLineEdit#searchBox:focus {
                border: 1px solid #00d9ff;
            }
            QTableWidget {
                background-color: #0a0e14;
                border: none;
                gridline-color: #1e2835;
                selection-background-color: #1e2835;
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
                background-color: #0a0e14;
                color: #8b92a0;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #1e2835;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QLabel#statusSuccess {
                background-color: #0d3a2e;
                color: #00ff88;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#statusIdle {
                background-color: #2a3544;
                color: #8b92a0;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton#tableActionBtn {
                background-color: transparent;
                border: none;
                color: #8b92a0;
                padding: 4px;
                font-size: 16px;
            }
            QPushButton#tableActionBtn:hover {
                color: #00d9ff;
                background-color: #1a2332;
                border-radius: 4px;
            }
            QPushButton#createTaskBtn {
                background-color: #00d9ff;
                border: none;
                border-radius: 6px;
                color: #0a0e14;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#createTaskBtn:hover {
                background-color: #00b8d9;
            }
            QPushButton#clearTasksBtn {
                background-color: #3d1f1f;
                border: none;
                border-radius: 6px;
                color: #ff4444;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#clearTasksBtn:hover {
                background-color: #4d2929;
            }
            QPushButton#startTasksBtn {
                background-color: #1f3d1f;
                border: none;
                border-radius: 6px;
                color: #00ff88;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#startTasksBtn:hover {
                background-color: #294d29;
            }
            QPushButton#stopTasksBtn {
                background-color: #3d2f1f;
                border: none;
                border-radius: 6px;
                color: #ffaa44;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#stopTasksBtn:hover {
                background-color: #4d3929;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav_bar.setFixedHeight(60)
        nav_bar_layout = QHBoxLayout(nav_bar)
        nav_bar_layout.setContentsMargins(20, 0, 20, 0)
        nav_bar_layout.setSpacing(0)

        brand_label = QLabel("Palace")
        brand_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        brand_label.setStyleSheet("color: #00d9ff; padding: 0 20px 0 0;")
        nav_bar_layout.addWidget(brand_label)

        nav_buttons = ["Tasks", "Proxies", "Billing", "Accounts", "Settings"]
        for i, btn_text in enumerate(nav_buttons):
            nav_btn = QPushButton(btn_text)
            nav_btn.setObjectName("navButton")
            nav_btn.setCheckable(True)
            if i == 0:
                nav_btn.setChecked(True)
            if btn_text.lower() in ["proxies", "billing", "accounts"]:
                nav_btn.clicked.connect(lambda checked, page=btn_text.lower(): self.switch_page_callback(page))
            nav_bar_layout.addWidget(nav_btn)

        nav_bar_layout.addStretch()

        import_btn = QPushButton("Import")
        import_btn.setObjectName("actionButton")
        nav_bar_layout.addWidget(import_btn)

        export_btn = QPushButton("Export")
        export_btn.setObjectName("actionButton")
        nav_bar_layout.addWidget(export_btn)

        main_layout.addWidget(nav_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        title_row = QHBoxLayout()
        
        self.task_title = QLabel("Tasks (0 Total)") # FIXED: dynamic
        self.task_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_row.addWidget(self.task_title)

        title_row.addStretch()

        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText(" Search")
        search_box.setFixedWidth(250)
        title_row.addWidget(search_box)

        content_layout.addLayout(title_row)

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels([
            "Store", "Product", "Size", "Profile", "Proxies", "Status", "Actions"
        ])
        
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        
        self.task_table.setColumnWidth(0, 150)
        self.task_table.setColumnWidth(2, 80)
        self.task_table.setColumnWidth(3, 120)
        self.task_table.setColumnWidth(4, 100)
        self.task_table.setColumnWidth(5, 180)
        self.task_table.setColumnWidth(6, 150)
        
        self.task_table.verticalHeader().setVisible(False)
        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.task_table.setShowGrid(False)

        content_layout.addWidget(self.task_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        create_btn = QPushButton("+ Create Tasks")
        create_btn.setObjectName("createTaskBtn")
        create_btn.clicked.connect(self.open_create_task_dialog)
        bottom_layout.addWidget(create_btn)

        clear_btn = QPushButton("🗑️ Clear Tasks")
        clear_btn.setObjectName("clearTasksBtn")
        clear_btn.clicked.connect(self.clear_all_tasks)
        bottom_layout.addWidget(clear_btn)

        bottom_layout.addStretch()

        self.start_btn = QPushButton("▶ Start Tasks")
        self.start_btn.setObjectName("startTasksBtn")
        self.start_btn.clicked.connect(self.start_tasks)    
        bottom_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹ Stop Tasks")
        self.stop_btn.setObjectName("stopTasksBtn")
        self.stop_btn.clicked.connect(self.stop_tasks)
        bottom_layout.addWidget(self.stop_btn)

        self.running = False
        self.active_tasks = []


        content_layout.addLayout(bottom_layout)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        self.load_tasks()
        
    def load_tasks(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    # handle both list and dict formats
                    self.tasks = data if isinstance(data, list) else []
                    print(f"Loaded {len(self.tasks)} task(s) from {self.storage_path}")
                    if self.tasks:
                        task_nums = []
                        for task in self.tasks:
                            try:
                                num = int(str(task.get("id","")).split("_")[1])
                                task_nums.append(num)
                            except:
                                pass
                        if task_nums:
                            self.task_counter = max(task_nums) + 1
                    self.update_task_table()
            except Exception as e:
                print(f"Failed to load tasks: {e}")
                self.tasks = []
        else:
            print(f"No existing tasks found at {self.storage_path}")
            self.tasks = []
            self.update_task_table()
            
    def save_tasks(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(self.tasks, f, indent=4)
            print(f" Saved {len(self.tasks)} task(s) to {self.storage_path}")
        except Exception as e:
            print(f"Failed to save tasks: {e}")
    
    def update_task_table(self):
        # FIXED: update header count
        self.task_title.setText(f"Tasks ({len(self.tasks)} Total)")
        self.task_table.setRowCount(len(self.tasks))
        
        for row, task in enumerate(self.tasks):
            store_widget = QWidget()
            store_layout = QHBoxLayout(store_widget)
            store_layout.setContentsMargins(8, 0, 0, 0)
            store_icon = QLabel("🛍️")
            store_text = QLabel(task.get("store", "Shoe Palace"))
            store_text.setStyleSheet("color: #e4e6eb")
            store_layout.addWidget(store_icon)
            store_layout.addWidget(store_text)
            store_layout.addStretch()
            self.task_table.setCellWidget(row, 0, store_widget)
            
            product_name = task.get("product_name", "Unknown Product")
            self.task_table.setItem(row, 1, QTableWidgetItem(product_name))
            
            size = str(task.get("size", "N/A"))
            self.task_table.setItem(row, 2, QTableWidgetItem(size))
            
            profile = task.get("profile", "None")
            self.task_table.setItem(row, 3, QTableWidgetItem(profile))
            
            proxy_group = task.get("proxy_group", "None")
            self.task_table.setItem(row, 4, QTableWidgetItem(proxy_group))
            
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 4, 8, 4)
            
            status = task.get("status", "Idle")
            
            if "Success" in status or "Checked Out" in status:
                color = "#0d3a2e"
                text_color = "#00ff88"
            elif "Running" in status or "Monitoring" in status:
                color = "#1f3d3d"
                text_color = "#00d9ff"
            elif "Failed" in status or "Error" in status:
                color = "#3d1f1f"
                text_color = "#ff4444"
            else:
                color = "#2a3544"
                text_color = "#8b92a0"
            
            status_label = QLabel(f"● {status}")
            status_label.setStyleSheet(f"""
                background-color: {color};
                color: {text_color};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;                       
            """)
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            self.task_table.setCellWidget(row, 5, status_widget)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)
            
            play_btn = QPushButton("▶")
            play_btn.setObjectName("tableActionBtn")
            play_btn.setToolTip("Start Task")
            
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("tableActionBtn")
            edit_btn.setToolTip("Edit Task")
            edit_btn.clicked.connect(lambda checked, task_id=task["id"]: self.edit_task(task_id))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setObjectName("tableActionBtn")
            delete_btn.setToolTip("Delete Task")
            delete_btn.clicked.connect(lambda checked, task_id=task["id"]: self.delete_task(task_id))
            
            actions_layout.addWidget(play_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.task_table.setCellWidget(row, 6, actions_widget)
            
            self.task_table.setRowHeight(row, 50)

    def clear_all_tasks(self):
        self.tasks = []
        self.task_counter = 0
        self.save_tasks()
        self.update_task_table()
    
    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                product_name = task.get("product_name", "Unknown")
                self.tasks.pop(i)
                self.save_tasks()
                self.update_task_table()
                print(f"Deleted task: {product_name}")
                return
        print(f"Task {task_id} not found")

    def edit_task(self, task_id):
        from palacebot_ui.frontend.task_creation_form import TaskCreationDialog
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task: return
        proxy_groups = [g["group_name"] for g in self.proxy_manager.proxylist.get("Groups", [])] if self.proxy_manager else ["default"]
        dialog = TaskCreationDialog(self, billing_profiles=["default"], proxy_groups=proxy_groups or ["default"])
        dialog.load_task(task)
        if dialog.exec():
            data = dialog.get_task_data()
            task.update(data)
            self.save_tasks()
            self.update_task_table()

    @asyncSlot()
    async def start_tasks(self):
        if self.running:
            return
        if not self.tasks:
            QMessageBox.warning(self, "No Tasks", "Create a task first.")
            return
        self.running = True
        self.start_btn.setEnabled(False)
        print(f"Starting {len(self.tasks)} task(s)")
        for task in self.tasks:
            if not self.running:
                break
            if "Success" in task.get("status",""):
                continue
            await self.run_single_task(task)
        self.running = False
        self.start_btn.setEnabled(True)
        print("All tasks finished")

    def stop_tasks(self):
        self.running = False
        print("Stop requested")

    async def run_single_task(self, task):
        from palacebot_ui.backend.seleniumscraperupgrade import SeleniumScraper
        from selenium.webdriver.common.by import By

        task["status"] = "Running"
        self.update_task_table()
        url = task.get("product_url") or task.get("url") or ""
        if "?" in url and "variant" in url:
            url = url.split("?")[0]
        size = str(task.get("size", "10.5"))
        size_text = f"M{size}" if not size.startswith("M") else size

        scraper = SeleniumScraper(url=url, proxy_manager=self.proxy_manager, headless=False, mode="fast")
        try:
            html = await scraper.get_page(group_name=task.get("proxy_group","default"), timeout=30)
            if not html:
                raise Exception("Failed to load")
            driver = scraper.browser
            try:
                labels = driver.find_elements(By.CSS_SELECTOR, 'label.SizeSwatch')
                target = next((l for l in labels if size_text in l.text), None)
                if target:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                    await asyncio.sleep(0.3)
                    driver.execute_script("arguments[0].click();", target)
                    await asyncio.sleep(0.8)
            except: pass

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(0.5)
            await asyncio.to_thread(driver.execute_script, "document.querySelectorAll('[class*=teaser],[class*=WOOPS]').forEach(e=>e.remove());")
            await asyncio.sleep(0.3)
            btn = driver.find_element(By.CSS_SELECTOR, 'form[action*="/cart/add"] button')
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            await asyncio.sleep(0.3)
            driver.execute_script("arguments[0].click();", btn)
            await asyncio.sleep(2)
            task["status"] = "Success - Added to Cart" if "cart" in driver.page_source.lower() else "Failed - Cart not detected"
        except Exception as e:
            task["status"] = f"Failed - {str(e)[:40]}"
        finally:
            try: await scraper.cleanup()
            except: pass
            self.save_tasks()
            self.update_task_table()
    
    def open_create_task_dialog(self):
        # FIXED: absolute import
        from palacebot_ui.frontend.task_creation_form import TaskCreationDialog
        
        # FIXED: load real groups, not placeholder
        if self.proxy_manager:
            proxy_groups = [g["group_name"] for g in self.proxy_manager.proxylist.get("Groups", [])]
        else:
            proxy_groups = ["default"]
        if not proxy_groups:
            proxy_groups = ["default"]

        if self.billing_manager:
            billing_profiles = self.billing_manager.get_all_profile_names()
        else:
            billing_profiles = ["default"]
        if not billing_profiles:
            billing_profiles = ["default"]
        
        dialog = TaskCreationDialog(
            self,
            billing_profiles=billing_profiles,
            proxy_groups=proxy_groups
        )
        
        if dialog.exec():
            task_data = dialog.get_task_data()
            
            if not task_data["product_name"]:
                print("Error: Product name is required")
                return
            
            if not task_data["size"]:
                print("Error: Size is required")
                return
            
            task = {
                "id": f"task_{self.task_counter:03d}",
                "store": "Shoe Palace",
                "product_name": task_data["product_name"],
                "product_url": task_data["product_url"],
                "size": task_data["size"],
                "profile": task_data["profile"],
                "proxy_group": task_data["proxy_group"],
                "status": "Idle",
                "keywords": task_data["keywords"],
                "quantity": task_data["quantity"],
                "max_price": task_data["max_price"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.tasks.append(task)
            self.task_counter += 1
            
            self.save_tasks()
            self.update_task_table()
            
            print(f"Created task: {task['product_name']}")