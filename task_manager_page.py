from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QLineEdit, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

class TaskManagerPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        
        # Main stylesheet - dark, modern theme
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
                padding: 0px;
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
            
            /* Action Buttons (Import/Export/etc) */
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
            
            /* Search Box */
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
            
            /* Table Styling */
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
            
            /* Table Header */
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
            
            /* Status Labels */
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
            
            /* Table Action Buttons */
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
            
            /* Bottom Action Buttons */
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

        # Main layout
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
        nav_buttons = ["Tasks", "Proxies", "Billing", "Accounts", "Rates", "Settings"]
        for i, btn_text in enumerate(nav_buttons):
            nav_btn = QPushButton(btn_text)
            nav_btn.setObjectName("navButton")
            nav_btn.setCheckable(True)
            if i == 0:  # Tasks is active
                nav_btn.setChecked(True)
            if btn_text.lower() in ["proxies", "billing", "accounts"]:
                nav_btn.clicked.connect(lambda checked, page=btn_text.lower(): self.switch_page_callback(page))
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
        content_layout.setSpacing(15)

        # Title and search row
        title_row = QHBoxLayout()
        
        task_title = QLabel("Tasks (10 Total)")
        task_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_row.addWidget(task_title)

        title_row.addStretch()

        # Search box
        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText(" Search")
        search_box.setFixedWidth(250)
        title_row.addWidget(search_box)

        content_layout.addLayout(title_row)

        # === TASK TABLE ===
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels([
            "Store", "Product", "Size", "Profile", "Proxies", "Status", "Actions"
        ])
        
        # Set column widths
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        
        self.task_table.setColumnWidth(0, 120)
        self.task_table.setColumnWidth(2, 80)
        self.task_table.setColumnWidth(3, 120)
        self.task_table.setColumnWidth(4, 100)
        self.task_table.setColumnWidth(5, 180)
        self.task_table.setColumnWidth(6, 150)
        
        self.task_table.verticalHeader().setVisible(False)
        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.task_table.setShowGrid(False)

        # Add sample data
        sample_data = [
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "10", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "11.5", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "12", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "10", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "7.5", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "8.5", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "9", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "10", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "10.5", "Profile 1", "None", "Successfully Checked Out"),
            ("Kith\nShopify", "adidas Yeezy 350 - Black", "12", "Profile 1", "None", "Successfully Checked Out"),
        ]

        self.task_table.setRowCount(len(sample_data))
        
        for row, data in enumerate(sample_data):
            # Store with icon
            store_widget = QWidget()
            store_layout = QHBoxLayout(store_widget)
            store_layout.setContentsMargins(8, 0, 0, 0)
            store_icon = QLabel("🛍️")
            store_text = QLabel(data[0])
            store_text.setStyleSheet("color: #e4e6eb;")
            store_layout.addWidget(store_icon)
            store_layout.addWidget(store_text)
            store_layout.addStretch()
            self.task_table.setCellWidget(row, 0, store_widget)
            
            # Product
            self.task_table.setItem(row, 1, QTableWidgetItem(data[1]))
            
            # Size
            self.task_table.setItem(row, 2, QTableWidgetItem(data[2]))
            
            # Profile
            self.task_table.setItem(row, 3, QTableWidgetItem(data[3]))
            
            # Proxies
            self.task_table.setItem(row, 4, QTableWidgetItem(data[4]))
            
            # Status
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 4, 8, 4)
            status_label = QLabel(f"● {data[5]}")
            status_label.setObjectName("statusSuccess")
            status_label.setStyleSheet("""
                background-color: #0d3a2e;
                color: #00ff88;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            """)
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            self.task_table.setCellWidget(row, 5, status_widget)
            
            # Actions
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
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setObjectName("tableActionBtn")
            delete_btn.setToolTip("Delete Task")
            
            actions_layout.addWidget(play_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.task_table.setCellWidget(row, 6, actions_widget)
            
            # Set row height
            self.task_table.setRowHeight(row, 50)

        content_layout.addWidget(self.task_table)

        # === BOTTOM ACTION BUTTONS ===
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        create_btn = QPushButton("+ Create Tasks")
        create_btn.setObjectName("createTaskBtn")
        bottom_layout.addWidget(create_btn)

        clear_btn = QPushButton("🗑️ Clear Tasks")
        clear_btn.setObjectName("clearTasksBtn")
        bottom_layout.addWidget(clear_btn)

        bottom_layout.addStretch()

        start_btn = QPushButton("▶ Start Tasks")
        start_btn.setObjectName("startTasksBtn")
        bottom_layout.addWidget(start_btn)

        stop_btn = QPushButton("⏹ Stop Tasks")
        stop_btn.setObjectName("stopTasksBtn")
        bottom_layout.addWidget(stop_btn)

        content_layout.addLayout(bottom_layout)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)