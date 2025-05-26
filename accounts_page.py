from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class AccountsPage(QWidget):
    def __init__(self):
        super().__init__()

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
        """)

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

        #Output area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Accounts or logs will show here.")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
