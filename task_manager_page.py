from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class TaskManagerPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.setStyleSheet("""
            QWidget {
                background-color: #0D1B2A;
                color: #E0E1DD;
            }
            QListWidget {
                background-color: #1B263B;
                border-radius: 8px;
                padding: 10px;               
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget {
                background-color:#1B263B;
                border-radius: 8px;               
            }
            QHeaderView::section {
                background-color: #415A77;
                color: white;
                padding: 6px;
                border: none;
            }
            QTableWidgetItem {
                color: #E0E1DD;               
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

        #Main page
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        #sidebar (Left)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        top_layout.addWidget(self.sidebar)

        #Test products
        for product in ["Jordan 1 Low", "Yeezy Slide", "Air Max 90"]:
            item = QListWidgetItem(product)
            self.sidebar.addItem(item)

        #Display task (Right)
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(["Site", "Size", "Product", "Status", "Profile", "Actions"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setRowCount(3)

        #Test products (rows)
        self.task_table.setRowCount(3)
        for row in range(3):
            self.task_table.setItem(row, 0, QTableWidgetItem("Shoe Palace"))
            self.task_table.setItem(row, 1, QTableWidgetItem("10"))
            self.task_table.setItem(row, 2, QTableWidgetItem("Jordan 1 Low"))
            self.task_table.setItem(row, 3, QTableWidgetItem("Idle"))
            self.task_table.setItem(row, 4, QTableWidgetItem("Default"))
            self.task_table.setItem(row, 5, QTableWidgetItem("✏️ 🗑️ ▶️ ⏹️"))
        
        top_layout.addWidget(self.task_table)

        main_layout.addLayout(top_layout)

        #Back to home
        self.back_button = QPushButton("Back to home")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(lambda:self.switch_page_callback("home"))
        main_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)


        self.setLayout(main_layout)