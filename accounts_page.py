
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QGroupBox, QGridLayout, QHeaderView, QTextEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import json
import os

class AccountsPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()

        self.accounts = []
        self.storage_path = "accounts.json"
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
            QLineEdit {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e4e6eb;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border: 1px solid #00d9ff;
            }
            
            /* Labels */
            QLabel#fieldLabel {
                color: #8b92a0;
                font-size: 12px;
                font-weight: 500;
            }
            
            /* Primary Button */
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
            
            /* Secondary Button */
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
            
            /* Danger Button */
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
            
            /* Action Buttons in Table */
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
            if btn_text == "Accounts":  # Accounts is active
                nav_btn.setChecked(True)
            if page_key:
                nav_btn.clicked.connect(lambda checked, pk=page_key: self.switch_page_callback(pk))
            nav_bar_layout.addWidget(nav_btn)

        nav_bar_layout.addStretch()

        # Right side buttons
        import_btn = QPushButton("Import")
        import_btn.setObjectName("actionButton")
        import_btn.clicked.connect(self.import_accounts)
        nav_bar_layout.addWidget(import_btn)

        export_btn = QPushButton("Export")
        export_btn.setObjectName("actionButton")
        export_btn.clicked.connect(self.export_accounts)
        nav_bar_layout.addWidget(export_btn)

        main_layout.addWidget(nav_bar)

        # === CONTENT AREA ===
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Title
        title = QLabel("Account Manager")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        content_layout.addWidget(title)

        # === ADD ACCOUNT SECTION ===
        add_section = QGroupBox("Add New Account")
        add_layout = QGridLayout()
        add_layout.setHorizontalSpacing(15)
        add_layout.setVerticalSpacing(12)

        # Email
        email_label = QLabel("Email:")
        email_label.setObjectName("fieldLabel")
        add_layout.addWidget(email_label, 0, 0, Qt.AlignmentFlag.AlignRight)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("account@example.com")
        self.email_input.setMinimumWidth(300)
        add_layout.addWidget(self.email_input, 0, 1)

        # Password
        password_label = QLabel("Password:")
        password_label.setObjectName("fieldLabel")
        add_layout.addWidget(password_label, 0, 2, Qt.AlignmentFlag.AlignRight)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumWidth(300)
        add_layout.addWidget(self.password_input, 0, 3)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_button = QPushButton("➕ Add Account")
        self.add_button.setObjectName("primaryBtn")
        self.add_button.clicked.connect(self.handle_add_account)
        button_layout.addWidget(self.add_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondaryBtn")
        self.clear_button.clicked.connect(self.clear_inputs)
        button_layout.addWidget(self.clear_button)
        
        add_layout.addLayout(button_layout, 1, 0, 1, 4)

        add_section.setLayout(add_layout)
        content_layout.addWidget(add_section)

        # === ACCOUNTS TABLE ===
        accounts_header_layout = QHBoxLayout()
        
        accounts_header = QLabel("Saved Accounts")
        accounts_header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        accounts_header_layout.addWidget(accounts_header)
        
        accounts_header_layout.addStretch()
        
        # Clear all button
        self.clear_all_button = QPushButton("🗑️ Clear All Accounts")
        self.clear_all_button.setObjectName("dangerBtn")
        self.clear_all_button.clicked.connect(self.clear_all_accounts)
        accounts_header_layout.addWidget(self.clear_all_button)
        
        content_layout.addLayout(accounts_header_layout)

        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(3)
        self.accounts_table.setHorizontalHeaderLabels(["Email", "Password", "Actions"])
        
        header = self.accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        
        self.accounts_table.setColumnWidth(2, 120)
        
        self.accounts_table.verticalHeader().setVisible(False)
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.accounts_table.setShowGrid(False)
        self.accounts_table.setAlternatingRowColors(True)
        
        content_layout.addWidget(self.accounts_table)

        # === LOG SECTION ===
        log_section = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(120)
        self.log_area.setPlaceholderText("Account activity will appear here...")
        log_layout.addWidget(self.log_area)

        log_section.setLayout(log_layout)
        content_layout.addWidget(log_section)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        
        # Load existing accounts
        self.load_accounts()

    def handle_add_account(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.log_area.append("❌ Error: Please enter both email and password.")
            return
        
        # Check if account already exists
        for acc in self.accounts:
            if acc[0] == email:
                self.log_area.append(f"⚠️ Warning: Account {email} already exists.")
                return
        
        self.accounts.append([email, password])
        self.log_area.append(f"✅ Added account: {email}")
        
        self.clear_inputs()
        self.save_accounts()
        self.update_accounts_table()

    def clear_inputs(self):
        self.email_input.clear()
        self.password_input.clear()

    def clear_all_accounts(self):
        if not self.accounts:
            self.log_area.append("ℹ️ No accounts to clear.")
            return
        
        count = len(self.accounts)
        self.accounts.clear()
        self.save_accounts()
        self.update_accounts_table()
        self.log_area.append(f"🗑️ Cleared all {count} account(s).")

    def delete_account(self, row):
        if 0 <= row < len(self.accounts):
            email = self.accounts[row][0]
            self.accounts.pop(row)
            self.save_accounts()
            self.update_accounts_table()
            self.log_area.append(f"🗑️ Deleted account: {email}")

    def update_accounts_table(self):
        self.accounts_table.setRowCount(len(self.accounts))
        
        for row, account in enumerate(self.accounts):
            # Email
            self.accounts_table.setItem(row, 0, QTableWidgetItem(account[0]))
            
            # Password (masked)
            masked_password = "*" * len(account[1])
            self.accounts_table.setItem(row, 1, QTableWidgetItem(masked_password))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("tableActionBtn")
            edit_btn.setToolTip("Edit Account")
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setObjectName("tableActionBtn")
            delete_btn.setToolTip("Delete Account")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_account(r))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.accounts_table.setCellWidget(row, 2, actions_widget)
            self.accounts_table.setRowHeight(row, 45)

    def load_accounts(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.accounts = json.load(f)
                    self.log_area.append(f"📂 Loaded {len(self.accounts)} account(s) from file.")
                    self.update_accounts_table()
            except Exception as e:
                self.log_area.append(f"❌ Failed to load accounts: {e}")
    
    def save_accounts(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.accounts, f, indent=4)
        except Exception as e:
            self.log_area.append(f"❌ Failed to save accounts: {e}")

    def import_accounts(self):
        self.log_area.append("📥 Import functionality - coming soon!")

    def export_accounts(self):
        self.log_area.append("📤 Export functionality - coming soon!")