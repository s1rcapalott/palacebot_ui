from PyQt6.QtWidgets import(
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class HomePage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback

        self.setStyleSheet("""
            QWidget {
                background-color: #0D1B2A;
                color: #E0E1DD;
            }
            QPushButton {
                background-color: #1B263B;
                border: 2px solid #415A77;
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #415A77;
            }
        """)

        main_layout = QVBoxLayout()

        #Title card
        title = QLabel("Palace Bot")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        #Button grids
        grid = QGridLayout()
        grid.setSpacing(20)

        #Button for task page
        self.task_btn = QPushButton("Tasks")
        self.task_btn.clicked.connect(lambda: self.switch_page_callback("tasks"))
        grid.addWidget(self.task_btn, 0, 0)

        #Button for proxy page
        self.proxy_btn = QPushButton("Proxies")
        self.proxy_btn.clicked.connect(lambda: self.switch_page_callback("proxies"))
        grid.addWidget(self.proxy_btn, 0, 1)

        #Placeholder for billing
        self.billing_btn = QPushButton("Billing")
        self.billing_btn.clicked.connect(lambda: self.switch_page_callback("billing"))
        grid.addWidget(self.billing_btn, 1, 0)

        #Placeholder for Account
        self.accounts_btn = QPushButton("Accounts")
        self.accounts_btn.clicked.connect(lambda: self.switch_page_callback("account"))
        grid.addWidget(self.accounts_btn, 1, 1)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)