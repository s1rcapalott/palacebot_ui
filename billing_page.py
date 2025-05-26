from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class BillingPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #0D1B2A;
                color: #E0E1DD;               
            }
            QLabel {
                font-size: 16px;            
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("Billing Page")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        placeholder = QLabel("This is where the billing profiles will be managed.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        self.setLayout(layout)