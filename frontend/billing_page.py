from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QGroupBox, QGridLayout, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Reviewed Billing Page:
"""
    TODO List:
    - Add load_profiles and save_profiles
    - Add storage_path
    - Call loaded profiles
    - Call save profiles
    
    Important:
    - Add card/cvv number encryption
    - Add get_profile for bot
    - Add get all profile method for tasks page dropdown
    
    Less Important
    - Add card, phone number validation
    - Add duplicate profile name check
    - Implement edit button functionality
    
    
"""

class BillingPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        
        self.profiles = []  # Store billing profiles

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
            QLineEdit, QComboBox {
                background-color: #1e2835;
                border: 1px solid #2a3544;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e4e6eb;
                font-size: 13px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00d9ff;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b92a0;
                margin-right: 5px;
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
            
            /* Scroll Area */
            QScrollArea {
                border: none;
                background-color: #0a0e14;
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
            if btn_text == "Billing":  # Billing is active
                nav_btn.setChecked(True)
            if page_key:
                nav_btn.clicked.connect(lambda checked, pk=page_key: self.switch_page_callback(pk))
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
        content_layout.setSpacing(20)

        # Title
        title = QLabel("Billing Profiles")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        content_layout.addWidget(title)

        # === CREATE PROFILE SECTION ===
        create_section = QGroupBox("Create Billing Profile")
        create_layout = QGridLayout()
        create_layout.setHorizontalSpacing(15)
        create_layout.setVerticalSpacing(12)

        # Profile Name
        name_label = QLabel("Profile Name:")
        name_label.setObjectName("fieldLabel")
        create_layout.addWidget(name_label, 0, 0, Qt.AlignmentFlag.AlignRight)
        
        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("e.g., Personal Card")
        create_layout.addWidget(self.profile_name_input, 0, 1, 1, 2)

        # Cardholder Name
        cardholder_label = QLabel("Cardholder Name:")
        cardholder_label.setObjectName("fieldLabel")
        create_layout.addWidget(cardholder_label, 1, 0, Qt.AlignmentFlag.AlignRight)
        
        self.cardholder_input = QLineEdit()
        self.cardholder_input.setPlaceholderText("Full name on card")
        create_layout.addWidget(self.cardholder_input, 1, 1, 1, 2)

        # Card Number
        card_num_label = QLabel("Card Number:")
        card_num_label.setObjectName("fieldLabel")
        create_layout.addWidget(card_num_label, 2, 0, Qt.AlignmentFlag.AlignRight)
        
        self.card_number_input = QLineEdit()
        self.card_number_input.setPlaceholderText("1234 5678 9012 3456")
        self.card_number_input.setMaxLength(19)
        create_layout.addWidget(self.card_number_input, 2, 1, 1, 2)

        # Expiry Date
        expiry_label = QLabel("Expiry Date:")
        expiry_label.setObjectName("fieldLabel")
        create_layout.addWidget(expiry_label, 3, 0, Qt.AlignmentFlag.AlignRight)
        
        self.expiry_month = QComboBox()
        self.expiry_month.addItems([f"{i:02d}" for i in range(1, 13)])
        create_layout.addWidget(self.expiry_month, 3, 1)
        
        self.expiry_year = QComboBox()
        self.expiry_year.addItems([str(2025 + i) for i in range(10)])
        create_layout.addWidget(self.expiry_year, 3, 2)

        # CVV
        cvv_label = QLabel("CVV:")
        cvv_label.setObjectName("fieldLabel")
        create_layout.addWidget(cvv_label, 4, 0, Qt.AlignmentFlag.AlignRight)
        
        self.cvv_input = QLineEdit()
        self.cvv_input.setPlaceholderText("123")
        self.cvv_input.setMaxLength(4)
        self.cvv_input.setEchoMode(QLineEdit.EchoMode.Password)
        create_layout.addWidget(self.cvv_input, 4, 1)

        # Billing Address
        address_label = QLabel("Billing Address:")
        address_label.setObjectName("fieldLabel")
        create_layout.addWidget(address_label, 5, 0, Qt.AlignmentFlag.AlignRight)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("123 Main St")
        create_layout.addWidget(self.address_input, 5, 1, 1, 2)

        # City, State, ZIP
        city_label = QLabel("City:")
        city_label.setObjectName("fieldLabel")
        create_layout.addWidget(city_label, 6, 0, Qt.AlignmentFlag.AlignRight)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City")
        create_layout.addWidget(self.city_input, 6, 1)

        state_label = QLabel("State:")
        state_label.setObjectName("fieldLabel")
        state_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        create_layout.addWidget(state_label, 6, 2)
        
        self.state_input = QComboBox()
        self.state_input.addItems(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"])
        create_layout.addWidget(self.state_input, 6, 3)

        zip_label = QLabel("ZIP Code:")
        zip_label.setObjectName("fieldLabel")
        create_layout.addWidget(zip_label, 7, 0, Qt.AlignmentFlag.AlignRight)
        
        self.zip_input = QLineEdit()
        self.zip_input.setPlaceholderText("12345")
        self.zip_input.setMaxLength(10)
        create_layout.addWidget(self.zip_input, 7, 1)

        # Country
        country_label = QLabel("Country:")
        country_label.setObjectName("fieldLabel")
        country_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        create_layout.addWidget(country_label, 7, 2)
        
        self.country_input = QComboBox()
        self.country_input.addItems(["United States", "Canada", "United Kingdom"])
        create_layout.addWidget(self.country_input, 7, 3)

        # Phone
        phone_label = QLabel("Phone:")
        phone_label.setObjectName("fieldLabel")
        create_layout.addWidget(phone_label, 8, 0, Qt.AlignmentFlag.AlignRight)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("(555) 123-4567")
        create_layout.addWidget(self.phone_input, 8, 1, 1, 2)

        # Email
        email_label = QLabel("Email:")
        email_label.setObjectName("fieldLabel")
        create_layout.addWidget(email_label, 9, 0, Qt.AlignmentFlag.AlignRight)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        create_layout.addWidget(self.email_input, 9, 1, 1, 2)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("💾 Save Profile")
        self.save_button.setObjectName("primaryBtn")
        self.save_button.clicked.connect(self.save_profile)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setObjectName("secondaryBtn")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        create_layout.addLayout(button_layout, 10, 0, 1, 4)

        create_section.setLayout(create_layout)
        content_layout.addWidget(create_section)

        # === SAVED PROFILES TABLE ===
        profiles_header = QLabel("Saved Profiles")
        profiles_header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        content_layout.addWidget(profiles_header)

        self.profiles_table = QTableWidget()
        self.profiles_table.setColumnCount(6)
        self.profiles_table.setHorizontalHeaderLabels([
            "Profile Name", "Cardholder", "Card Number", "Expiry", "Address", "Actions"
        ])
        
        header = self.profiles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.profiles_table.setColumnWidth(0, 150)
        self.profiles_table.setColumnWidth(2, 180)
        self.profiles_table.setColumnWidth(3, 100)
        self.profiles_table.setColumnWidth(5, 120)
        
        self.profiles_table.verticalHeader().setVisible(False)
        self.profiles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.profiles_table.setShowGrid(False)
        self.profiles_table.setAlternatingRowColors(True)
        
        content_layout.addWidget(self.profiles_table)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

    def save_profile(self):
        profile = {
            "name": self.profile_name_input.text().strip(),
            "cardholder": self.cardholder_input.text().strip(),
            "card_number": self.card_number_input.text().strip(),
            "expiry_month": self.expiry_month.currentText(),
            "expiry_year": self.expiry_year.currentText(),
            "cvv": self.cvv_input.text().strip(),
            "address": self.address_input.text().strip(),
            "city": self.city_input.text().strip(),
            "state": self.state_input.currentText(),
            "zip": self.zip_input.text().strip(),
            "country": self.country_input.currentText(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip()
        }
        
        if not profile["name"] or not profile["cardholder"] or not profile["card_number"]:
            return  # Basic validation
        
        self.profiles.append(profile)
        self.update_profiles_table()
        self.clear_form()
    
    def clear_form(self):
        self.profile_name_input.clear()
        self.cardholder_input.clear()
        self.card_number_input.clear()
        self.cvv_input.clear()
        self.address_input.clear()
        self.city_input.clear()
        self.zip_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.expiry_month.setCurrentIndex(0)
        self.expiry_year.setCurrentIndex(0)
    
    def update_profiles_table(self):
        self.profiles_table.setRowCount(len(self.profiles))
        
        for row, profile in enumerate(self.profiles):
            self.profiles_table.setItem(row, 0, QTableWidgetItem(profile["name"]))
            self.profiles_table.setItem(row, 1, QTableWidgetItem(profile["cardholder"]))
            
            # Mask card number
            card_num = profile["card_number"]
            masked = f"****  ****  ****  {card_num[-4:]}" if len(card_num) >= 4 else card_num
            self.profiles_table.setItem(row, 2, QTableWidgetItem(masked))
            
            expiry = f"{profile['expiry_month']}/{profile['expiry_year']}"
            self.profiles_table.setItem(row, 3, QTableWidgetItem(expiry))
            
            address = f"{profile['address']}, {profile['city']}, {profile['state']}"
            self.profiles_table.setItem(row, 4, QTableWidgetItem(address))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("tableActionBtn")
            edit_btn.setToolTip("Edit Profile")
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setObjectName("tableActionBtn")
            delete_btn.setToolTip("Delete Profile")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_profile(r))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.profiles_table.setCellWidget(row, 5, actions_widget)
            self.profiles_table.setRowHeight(row, 45)
    
    def delete_profile(self, row):
        if 0 <= row < len(self.profiles):
            self.profiles.pop(row)
            self.update_profiles_table()