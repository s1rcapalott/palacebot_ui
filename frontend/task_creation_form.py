from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox, 
    QDoubleSpinBox, QComboBox, QPushButton, QCheckBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class TaskCreationForm(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #1B263B;
                color: #E0E1DD;
                border-radius: 12px;
                padding: 20px;       
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #415A77;
                border: none;
                border-radius: 8px;
                padding: 6px;
                color: white;
            }
            QPushButton {
                background-color: #668DA9;
                border-radius: 10px;
                padding: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #E0E1DD;
                color: black;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        title = QLabel("Create Task")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        #Get the product URL
        self.layout.addWWidget(QLabel("Product URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPalaceholderText("Enter product URL")
        self.layout.addWidget(self.url_input)

        #Get keywords for product
        self.layout.addWidget(QLabel("Keywords:"))
        self.keywords_input = QLineEdit()
        self.keywords_input.setPalaceholderText("Enter keywords (comma or space separated)")
        self.layout.addWidget(self.keywords_input)

        #Get the size for product
        self.layout.addWidget(QLabel("Size:"))
        self.size_input = QLineEdit()
        self.size_input.setPalaceholderText("Enter size")
        self.layout.addWidget(self.size_input)

        #Get quantity
        self.layout.addWidget(QLabel("Quantity:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quatity_input.setMaximum(10)
        self.layout.addWidget(self.quantity_input)

        #Get style code
        self.layout.addWidget(QLabel("Style Code:"))
        self.style_code_input = QLineEdit()
        self.style_code_input.setPalaceholderText("e.g., ABC123-456")
        self.layout.addWidget(self.style_code_input)

        #Set max price
        self.layout.addWidget(QLabel("Max Price ($):"))
        self.max_price_input = QDoubleSpinBox()
        self.max_price_input.setMinimum(0)
        self.max_price_input.setMaximum(500)
        self.max_price_input.setDecimals(2)
        self.max_price_input.setPrefix("$")
        self.layout.addWidget(self.max_price_input)