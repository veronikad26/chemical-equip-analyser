import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTabWidget, QFormLayout, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.backend_url = "http://localhost:8000/api"  # Configure this
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setGeometry(300, 300, 500, 600)
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
            }
            QTabWidget::pane {
                border: 1px solid #cbd5e1;
                background: white;
                border-radius: 8px;
            }
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                background: white;
            }
        """)

        layout = QVBoxLayout()

        # Header with logo and title
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #06b6d4);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QVBoxLayout(header)

        logo_label = QLabel("⚗️")
        logo_label.setFont(QFont("Arial", 40))
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        title = QLabel("Chemical Equipment Visualizer")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Data-driven insights for industrial equipment")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8);")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # Tabs for Login/Register
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 5px 5px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #3b82f6;
            }
        """)

        # Login tab
        login_tab = QWidget()
        login_layout = QFormLayout(login_tab)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter username")
        login_layout.addRow("Username:", self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter password")
        login_layout.addRow("Password:", self.login_password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        login_layout.addRow(self.login_btn)

        self.tabs.addTab(login_tab, "Login")

        # Register tab
        register_tab = QWidget()
        register_layout = QFormLayout(register_tab)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose username")
        register_layout.addRow("Username:", self.reg_username)

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Enter email")
        register_layout.addRow("Email:", self.reg_email)

        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setPlaceholderText("Choose password")
        register_layout.addRow("Password:", self.reg_password)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        register_layout.addRow(self.register_btn)

        self.tabs.addTab(register_tab, "Register")

        # Create main container matching auth-layout (grid)
        container = QWidget()
        main_layout = QHBoxLayout(container)

        # Left side - Marketing section
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignCenter)

        marketing_title = QLabel("Chemical Equipment Visualizer")
        marketing_title.setObjectName("titleLabel")
        marketing_title.setFont(QFont("Work Sans", 48, QFont.Bold))
        left_layout.addWidget(marketing_title)

        marketing_subtitle = QLabel("Please login/register to continue")
        marketing_subtitle.setObjectName("subtitleLabel")
        marketing_subtitle.setFont(QFont("Work Sans", 20))
        left_layout.addWidget(marketing_subtitle)

        # Right side - Form section
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)

        # Form card
        form_card = QFrame()
        form_card.setObjectName("authCard")
        form_layout = QVBoxLayout(form_card)

        # Auth header inside card
        auth_header = QWidget()
        header_layout = QVBoxLayout(auth_header)
        header_layout.setContentsMargins(0, 0, 0, 32)

        # Small logo inside card
        logo_label = QLabel("⚗️")
        logo_label.setObjectName("smallLogo")
        logo_label.setFixedSize(48, 48)
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        card_title = QLabel("Chemical Equipment Visualizer")
        card_title.setObjectName("cardTitle")
        header_layout.addWidget(card_title, alignment=Qt.AlignCenter)

        card_subtitle = QLabel("Data-driven insights for industrial equipment")
        card_subtitle.setObjectName("cardSubtitle")
        header_layout.addWidget(card_subtitle, alignment=Qt.AlignCenter)

        form_layout.addWidget(auth_header)

        # Add tabs to form layout
        form_layout.addWidget(self.tabs)

        right_layout.addWidget(form_card)

        # Add left and right to main layout
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

        layout.addWidget(container)
        self.setLayout(layout)

    def login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        try:
            response = requests.post(f"{self.backend_url}/auth/login/", {
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    # Save token
                    with open('token.txt', 'w') as f:
                        f.write(token)
                    QMessageBox.information(self, "Success", "Login successful!")
                    self.open_dashboard(token)
                else:
                    QMessageBox.warning(self, "Error", "Invalid response from server")
            elif response.status_code == 404:
                QMessageBox.warning(self, "Error", "User not registered")
            else:
                QMessageBox.warning(self, "Error", "Login failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

    def register(self):
        username = self.reg_username.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text().strip()

        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        try:
            response = requests.post(f"{self.backend_url}/auth/register/", {
                "username": username,
                "email": email,
                "password": password
            })

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Registration successful! Please login.")
                self.tabs.setCurrentIndex(0)  # Switch to login tab
            else:
                data = response.json()
                error = data.get("error", "Registration failed")
                QMessageBox.warning(self, "Error", error)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

    def open_dashboard(self, token):
        from dashboard_window import DashboardWindow
        self.dashboard = DashboardWindow(token)
        self.dashboard.show()
        self.close()