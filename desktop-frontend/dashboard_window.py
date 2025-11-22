import sys
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QFileDialog,
    QProgressBar, QTableWidget, QTableWidgetItem, QFrame, QGridLayout,
    QMessageBox, QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os

# Utility function to clear layouts
def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().setParent(None)
class UploadThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, backend_url, token, file_path):
        super().__init__()
        self.backend_url = backend_url
        self.token = token
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                data = {'token': self.token}
                response = requests.post(f"{self.backend_url}/upload/", files=files, data=data)
                if response.status_code == 201:
                    self.finished.emit(response.json())
                else:
                    self.error.emit(f"Upload failed: {response.text}")
        except Exception as e:
            self.error.emit(str(e))

class DashboardWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.backend_url = "http://localhost:8000/api"
        self.token = token
        self.current_data = None
        self.init_ui()
        self.load_history()

    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Visualizer - Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Navbar
        navbar = QFrame()
        navbar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #06b6d4);
                padding: 10px;
            }
        """)
        navbar_layout = QHBoxLayout(navbar)

        brand = QLabel("⚗️ Chemical Equipment Analytics")
        brand.setFont(QFont("Arial", 16, QFont.Bold))
        brand.setStyleSheet("color: white;")
        navbar_layout.addWidget(brand)

        navbar_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
        """)
        logout_btn.clicked.connect(self.logout)
        navbar_layout.addWidget(logout_btn)

        main_layout.addWidget(navbar)

        # Hero banner
        hero = QFrame()
        hero.setObjectName("heroBanner")
        hero_layout = QHBoxLayout(hero)

        hero_text = QWidget()
        hero_text_layout = QVBoxLayout(hero_text)
        title = QLabel("Advanced Visualization & Insights")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        hero_text_layout.addWidget(title)

        subtitle = QLabel("Chemical equipment performance analytics powered by data")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        hero_text_layout.addWidget(subtitle)

        hero_layout.addWidget(hero_text)
        hero_layout.addStretch()

        main_layout.addWidget(hero)

        # Main content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setMaximumWidth(300)
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Upload section
        upload_frame = QFrame()
        upload_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
        """)
        upload_layout = QVBoxLayout(upload_frame)

        upload_title = QLabel("📤 Upload CSV")
        upload_title.setFont(QFont("Arial", 20, QFont.Bold))
        upload_title.setStyleSheet("margin: 15px 0px 20px 0px; padding: 10px;")
        upload_layout.addWidget(upload_title)

        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Arial", 11))
        self.file_label.setStyleSheet("color: #6b7280; margin: 8px 0px; padding: 5px;")
        upload_layout.addWidget(self.file_label)

        select_file_btn = QPushButton("Select File")
        select_file_btn.setFont(QFont("Arial", 12, QFont.Bold))
        select_file_btn.setMinimumHeight(45)
        select_file_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                margin: 8px 0px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
        """)
        select_file_btn.clicked.connect(self.select_file)
        upload_layout.addWidget(select_file_btn)

        self.upload_btn = QPushButton("Upload & Analyze")
        self.upload_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.upload_btn.setMinimumHeight(45)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                margin: 8px 0px;
            }
            QPushButton:hover:not(:disabled) {
                background: #059669;
            }
            QPushButton:pressed:not(:disabled) {
                background: #047857;
            }
            QPushButton:disabled {
                background: #6b7280;
                color: #9ca3af;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setEnabled(False)
        upload_layout.addWidget(self.upload_btn)

        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        upload_layout.addWidget(self.upload_progress)

        sidebar_layout.addWidget(upload_frame)

        # History section
        history_frame = QFrame()
        history_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        history_layout = QVBoxLayout(history_frame)

        history_title = QLabel("📋 Recent Datasets")
        history_title.setFont(QFont("Arial", 14, QFont.Bold))
        history_layout.addWidget(history_title)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_dataset)
        history_layout.addWidget(self.history_list)

        sidebar_layout.addWidget(history_frame)

        content_splitter.addWidget(self.sidebar)

        # Main content
        self.main_content = QScrollArea()
        self.main_content.setWidgetResizable(True)
        self.main_content.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.main_content.setWidget(content_widget)

        # Initial empty state
        self.show_empty_state()

        content_splitter.addWidget(self.main_content)
        content_splitter.setSizes([300, 1100])

        main_layout.addWidget(content_splitter)

        # Set styles
        self.setStyleSheet("""
            QMainWindow {
                background: #f8fafc;
            }
        """)

    def show_empty_state(self):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        empty_frame = QFrame()
        empty_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px dashed #cbd5e1;
                border-radius: 10px;
                padding: 40px;
                margin: 20px;
            }
        """)
        empty_layout = QVBoxLayout(empty_frame)
        empty_layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("📤")
        icon.setFont(QFont("Arial", 48))
        icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(icon)

        title = QLabel("No Data Yet")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(title)

        subtitle = QLabel("Upload a CSV file to get started with equipment analysis")
        subtitle.setStyleSheet("color: #6b7280;")
        subtitle.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(subtitle)

        self.content_layout.addWidget(empty_frame)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.upload_btn.setEnabled(True)

    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            return

        self.upload_progress.setVisible(True)
        self.upload_progress.setRange(0, 0)  # Indeterminate progress

        self.upload_thread = UploadThread(self.backend_url, self.token, self.selected_file)
        self.upload_thread.finished.connect(self.on_upload_finished)
        self.upload_thread.error.connect(self.on_upload_error)
        self.upload_thread.start()

    def on_upload_finished(self, data):
        self.upload_progress.setVisible(False)
        QMessageBox.information(self, "Success", "File uploaded successfully!")
        self.current_data = data
        self.load_history()
        self.display_data()

    def on_upload_error(self, error_msg):
        self.upload_progress.setVisible(False)
        QMessageBox.warning(self, "Error", error_msg)

    def load_history(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.backend_url}/history/", headers=headers)
            if response.status_code == 200:
                datasets = response.json()
                self.history_list.clear()
                for dataset in datasets:
                    item = QListWidgetItem(f"{dataset['filename']} - {dataset['uploaded_at'][:10]}")
                    item.setData(Qt.UserRole, dataset['id'])
                    self.history_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load history: {str(e)}")

    def load_dataset(self, item):
        dataset_id = item.data(Qt.UserRole)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.backend_url}/datasets/{dataset_id}/", headers=headers)
            if response.status_code == 200:
                self.current_data = response.json()
                self.display_data()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load dataset: {str(e)}")

    def display_data(self):
        if not self.current_data:
            return

        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)

        title = QLabel(self.current_data.get('filename', 'Uploaded Data'))
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        download_btn = QPushButton("📄 Download PDF")
        download_btn.clicked.connect(self.download_pdf)
        header_layout.addWidget(download_btn)

        self.content_layout.addWidget(header_frame)

        # Stats grid
        if 'summary' in self.current_data:
            summary = self.current_data['summary']
            stats_grid = QGridLayout()

            # Equipment Count
            count_card = self.create_stat_card("Equipment Count", str(summary['equipment_count']), "📊")
            stats_grid.addWidget(count_card, 0, 0)

            # Avg Flowrate
            flow_card = self.create_stat_card("Avg Flowrate", f"{summary['avg_flowrate']:.2f}", "🌊")
            stats_grid.addWidget(flow_card, 0, 1)

            # Avg Pressure
            pressure_card = self.create_stat_card("Avg Pressure", f"{summary['avg_pressure']:.2f}", "⚡")
            stats_grid.addWidget(pressure_card, 1, 0)

            # Avg Temperature
            temp_card = self.create_stat_card("Avg Temperature", f"{summary['avg_temperature']:.2f}", "🔥")
            stats_grid.addWidget(temp_card, 1, 1)

            stats_widget = QWidget()
            stats_widget.setLayout(stats_grid)
            self.content_layout.addWidget(stats_widget)

        # Charts
        if hasattr(self, 'charts_widget'):
            clear_layout(self.charts_layout)
        else:
            self.charts_widget = QWidget()
            self.charts_layout = QHBoxLayout(self.charts_widget)
            self.content_layout.addWidget(self.charts_widget)

        # Type distribution pie chart
        if 'summary' in self.current_data and 'type_distribution' in self.current_data['summary']:
            pie_frame = QFrame()
            pie_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 15px; }")
            pie_frame.setMinimumSize(450, 450)
            pie_layout = QVBoxLayout(pie_frame)

            pie_title = QLabel("Equipment Type Distribution")
            pie_title.setFont(QFont("Arial", 16, QFont.Bold))
            pie_title.setStyleSheet("margin-bottom: 10px;")
            pie_layout.addWidget(pie_title)

            self.create_pie_chart(pie_layout)

            self.charts_layout.addWidget(pie_frame)

        # Average parameters bar chart
        if 'summary' in self.current_data:
            bar_frame = QFrame()
            bar_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 15px; }")
            bar_frame.setMinimumSize(300, 300)
            bar_layout = QVBoxLayout(bar_frame)

            bar_title = QLabel("Average Parameter Values")
            bar_title.setFont(QFont("Arial", 14, QFont.Bold))
            bar_layout.addWidget(bar_title)

            self.create_bar_chart(bar_layout)

            self.charts_layout.addWidget(bar_frame)

        # Data table
        table_frame = QFrame()
        table_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 15px; margin-top: 20px; }")
        table_layout = QVBoxLayout(table_frame)

        table_title = QLabel("Equipment Data (First 100 records)")
        table_title.setFont(QFont("Arial", 14, QFont.Bold))
        table_layout.addWidget(table_title)

        self.create_data_table(table_layout)

        self.content_layout.addWidget(table_frame)

    def create_stat_card(self, title, value, icon):
        card = QFrame()
        card.setObjectName("statCard")
        layout = QVBoxLayout(card)

        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        layout.addWidget(value_label)

        return card

    def create_pie_chart(self, layout):
        if 'type_distribution' not in self.current_data['summary']:
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        type_dist = self.current_data['summary']['type_distribution']
        labels = list(type_dist.keys())
        sizes = list(type_dist.values())

        colors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        # Enhance appearance
        ax.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold', pad=20)
        plt.setp(autotexts, size=10, weight="bold", color="white")
        plt.setp(texts, size=12)

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        canvas.draw()  # Explicitly draw canvas

    def create_bar_chart(self, layout):
        if 'summary' not in self.current_data:
            return

        summary = self.current_data['summary']
        fig, ax = plt.subplots(figsize=(6, 4))

        labels = ['Flowrate', 'Pressure', 'Temperature']
        values = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]

        bars = ax.bar(labels, values, color='#3b82f6')
        ax.set_ylabel('Average Values')
        ax.set_title('Average Parameter Values')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

    def create_data_table(self, layout):
        if 'data' not in self.current_data:
            return

        table = QTableWidget()
        data = self.current_data['data'][:100]  # First 100 records

        if data:
            table.setRowCount(len(data))
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])

            # Increase table size and font
            table.setMinimumHeight(400)
            table.setMinimumWidth(800)
            table.setFont(QFont("Arial", 11))

            # Style the header
            header = table.horizontalHeader()
            header.setFont(QFont("Arial", 12, QFont.Bold))
            header.setDefaultAlignment(Qt.AlignLeft)
            header.setStretchLastSection(True)

            # Set column widths
            table.setColumnWidth(0, 200)  # Equipment Name
            table.setColumnWidth(1, 150)  # Type
            table.setColumnWidth(2, 120)  # Flowrate
            table.setColumnWidth(3, 120)  # Pressure
            table.setColumnWidth(4, 120)  # Temperature

            for row_idx, row in enumerate(data):
                table.setItem(row_idx, 0, QTableWidgetItem(str(row.get('Equipment Name', ''))))
                table.setItem(row_idx, 1, QTableWidgetItem(str(row.get('Type', ''))))
                table.setItem(row_idx, 2, QTableWidgetItem(str(row.get('Flowrate', ''))))
                table.setItem(row_idx, 3, QTableWidgetItem(str(row.get('Pressure', ''))))
                table.setItem(row_idx, 4, QTableWidgetItem(str(row.get('Temperature', ''))))

            # Style the table
            table.setStyleSheet("""
                QTableWidget {
                    gridline-color: #e5e7eb;
                    selection-background-color: #dbeafe;
                    font-size: 11px;
                }
                QHeaderView::section {
                    background-color: #f8fafc;
                    padding: 8px;
                    border: 1px solid #e5e7eb;
                    font-weight: bold;
                    color: #374151;
                }
                QTableWidget::item {
                    padding: 6px;
                    border-bottom: 1px solid #f3f4f6;
                }
                QTableWidget::item:selected {
                    background-color: #dbeafe;
                }
            """)

        layout.addWidget(table)

    def download_pdf(self):
        if not self.current_data:
            return

        try:
            # For simplicity, we'll make a request to generate PDF
            # Note: In the original code, PDF generation seems to happen on upload
            # We'll assume the backend has an endpoint for this
            QMessageBox.information(self, "Download", "PDF download functionality would be implemented here")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to download PDF: {str(e)}")

    def logout(self):
        if os.path.exists('token.txt'):
            os.remove('token.txt')
        self.close()
        from auth_window import AuthWindow
        self.auth = AuthWindow()
        self.auth.show()