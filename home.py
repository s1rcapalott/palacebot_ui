import sys
from PyQt6.QtWidgets import QMainWindow, QLabel, QGridLayout,QBoxLayout, QWidget, QApplication,QPushButton,QCharts,QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPainter, QPen, QIcon, QPixmap,QFont,Q
from PyQt6.QtCore import Qt

from PyQt6.QtCharts import QChart, QChartView, QLineSeries

# Custom sidebar widget
class SideBar(QWidget):
    def __init__(self):
        super().__init__()

        # Set background color and rounded corners
        self.setStyleSheet("""
            background-color: #121212;  /* Dark theme background */
            border-radius: 12px;
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)  # Add spacing between elements
        self.layout.setContentsMargins(20, 20, 20, 20)  # Padding

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("logo.jpg")
        scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(logo_label)

        # Sidebar Buttons
        self.addSidebarButton("Dashboard", "icons/dashboard.png")
        self.addSidebarButton("Settings", "icons/settings.png")
        self.addSidebarButton("Exit", "icons/exit.png")

        self.setLayout(self.layout)

    def addSidebarButton(self, text, icon_path):
        """Creates and adds a sidebar button with an icon."""
        button = QPushButton(text)
        button.setIcon(QIcon(icon_path))  # Set icon
        button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #1E1E1E;
                border-radius: 8px;
                padding: 10px;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        button.setFixedHeight(40)
        button.setIconSize(button.sizeHint())
        self.layout.addWidget(button)



class StatisticsGraph(QChart):
    def __init__(self, parent=None):
        super().__init__(parent)
        chart = self.QChart()
        self._max_value = 100

    def setValue(self, value):
        self._value = min(value, self._max_value)
        self.update()

    def setMaximum(self, max_value):
        self._max_value = max_value
        self.update()

    def paintEvent(self, event):
        pass


class Home(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palace Bot")
        self.resize(800, 600)
        self.setStyleSheet("background-color: black;")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)
        self.layout.addWidget(SideBar())
        
        # Custom graph widget


        #custom side bar

        

def main():
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


