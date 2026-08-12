from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox, 
    QDoubleSpinBox, QComboBox, QPushButton, QDialog, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class TaskCreationDialog(QDialog):
    def __init__(self, parent=None, billing_profiles=None, proxy_groups=None, accounts=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Task")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        # Store available options
        self.billing_profiles = billing_profiles or []
        self.proxy_groups = proxy_groups or []
        self.accounts = accounts or []

        self.setStyleSheet("""
            QDialog {
                background-color: #0a0e14;
                color: #e4e6eb;
            }
            QLabel {
                color: #8b92a0;
                font-size: 12px;
                font-weight: 500;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                padding: 8px;
                color: #e4e6eb;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00d9ff;
            }
            QPushButton {
                background-color: #00d9ff;
                border: none;
                border-radius: 6px;
                color: #0a0e14;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #00b8d9;
            }
            QPushButton#cancelBtn {
                background-color: #1e2835;
                color: #e4e6eb;
            }
            QPushButton#cancelBtn:hover {
                background-color: #2a3544;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Create New Task")
        title.setFont(QFont("Segoe Ui", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #e4e6eb; font-size: 16px;")
        layout.addWidget(title)
        
        # Form gid
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(12)
        
        row = 0

        # Product URL
        form_layout.addWidget(QLabel("Product URL:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.shoepalace.com/product/...")
        form_layout.addWidget(self.url_input, row, 1, 1, 2)
        row += 1
        
        # Product Name
        form_layout.addWidget(QLabel("Product Name:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("eg., Air Jordan 1 Retro")
        form_layout.addWidget(self.product_name_input, row, 1, 1, 2)
        row += 1
        
        # Keywords
        form_layout.addWidget(QLabel("Keywords:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Jordan, Retro, High (comma seperated)")
        form_layout.addWidget(self.keywords_input, row, 1, 1, 2)
        row += 1
        
        # Size
        form_layout.addWidget(QLabel("Size:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("10, 10.5, 11, etc.")
        form_layout.addWidget(self.size_input, row, 1)
        row += 1
        
        # Quantity
        form_layout.addWidget(QLabel("Quantity:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.quantity_input = QSpinBox() 
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(10)
        self.quantity_input.setValue(1)
        form_layout.addWidget(self.quantity_input, row, 1)
        row += 1
        
        # Max Price
        form_layout.addWidget(QLabel("Max Price:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.max_price_input = QDoubleSpinBox()
        self.max_price_input.setMinimum(0)
        self.max_price_input.setMaximum(9999)
        self.max_price_input.setDecimals(2)
        self.max_price_input.setPrefix("$")
        self.max_price_input.setValue(200.00)
        form_layout.addWidget(self.max_price_input, row, 1)
        row += 1
        
        # Billing Profile
        form_layout.addWidget(QLabel("Billing Profile:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.profile_select = QComboBox()
        if self.billing_profiles:
            self.profile_select.addItems(self.billing_profiles)
        else:
            self.profile_select.addItem("None")
        form_layout.addWidget(self.profile_select, row, 1, 1, 2)
        row += 1
        
        # Proxy Group
        form_layout.addWidget(QLabel("Proxy Group:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.proxy_group_select = QComboBox()
        if self.proxy_groups:
            self.proxy_group_select.addItems(self.proxy_groups)
        else:
            self.proxy_group_select.addItem("default")
        form_layout.addWidget(self.proxy_group_select, row, 1, 1, 2)
        row += 1
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Create Task")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def get_task_data(self):
        keywords_text = self.keywords_input.text().strip()
        keywords = [k.strip() for k in keywords_text.split(', ') if k.strip()] 
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        
        return {
            "product_url": self.url_input.text().strip(),
            "product_name": self.product_name_input.text().strip(),
            "keywords": keywords,
            "size": self.size_input.text().strip(),
            "quantity": self.quantity_input.value(), # was quantiy_input
            "max_price": self.max_price_input.value(),
            "profile": self.profile_select.currentText(),
            "proxy_group": self.proxy_group_select.currentText(), 
        }
