import sys
sys.path.append(r"C:\Users\mmira\Shoe-Palace-Bot-1")
from proxy import Proxy_Manager
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from home_page import HomePage
from task_manager_page import TaskManagerPage
from proxy_manager_page import ProxyManagerPage
from billing_page import BillingPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palace Bot")
        self.setGeometry(100, 100, 1200, 800)

        #Page container
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        #Backend logic
        self.proxy_manager = Proxy_Manager(proxy_file=r"C:\Users\mmira\Shoe-Palace-Bot-1\proxy.json")
        asyncio.run(self.proxy_manager.load_proxies())

        #Pages
        self.home_page = HomePage(self.switch_page)
        self.task_page = TaskManagerPage()
        self.proxy_page = ProxyManagerPage(self.proxy_manager)
        self.billing_page = BillingPage()

        # add pages to stack
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.task_page)
        self.stack.addWidget(self.proxy_page)
        self.stack.addWidget(self.billing_page)

        self.page_map = {
            "home": 0,
            "tasks": 1,
            "proxies": 2,
            "billing": 3
        }

    def switch_page(self, page_name):
        if page_name in self.page_map:
            self.stack.setCurrentIndex(self.page_map[page_name])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
