from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class AccountsPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()

        self.accounts = []
        self.storage_path = "accounts.json"
        self.switch_page_callback = switch_page_callback

        self.setStyleSheet("""
            QWidget {
                background-color: #0D1B2A;
                color: #E0E1DD;
            }
            QLineEdit {
                background-color: #1b263B;
                border: 1px solid #415A77;
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
            QPushButton {
                background-color: #415A77;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #778DA9;
            }
            QTextEdit {
                background-color: #1B263B;
                color: white;
                border-radius: 6px;
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
        
        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: switch_page_callback("home"))

        layout = QVBoxLayout()

        #Title
        title = QLabel("Account Manager")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        #Below are input fields
        input_layout = QHBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        input_layout.addWidget(self.email_input)
        input_layout.addWidget(self.password_input)

        layout.addLayout(input_layout)

        #Add button
        self.add_button = QPushButton("Add Account")
        layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.handle_add_account)

        #Output area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Accounts or logs will show here.")
        layout.addWidget(self.log_area)

        #Back to home
        self.back_button = QPushButton("Back to Home")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(lambda: self.switch_page_callback("home"))
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.load_accounts()

    def handle_add_account(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.log_area.append("Please enter both email and password.")
            return
        
        self.accounts.append((email, password))
        self.log_area.append(f"Added account: {email}")
        
        self.email_input.clear()
        self.password_input.clear()

        self.save_accounts()

    def load_accounts(self):
        import os, json

        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.accounts = json.load(f)
                    for account in self.accounts:
                        self.log_area.append(f"Loaded account: {account}")
            except Exception as e:
                self.log_area.append(f"Falied to load accounts: {e}")
    
    def save_accounts(self):
        import json
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.accounts, f, indent=4)
        except Exception as e:
            self.log_area.append(f"Failed to save accounts: {e}")
