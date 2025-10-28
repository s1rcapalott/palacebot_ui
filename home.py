import sys
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import QTimer
from qasync import QEventLoop
from home_page import HomePage
from task_manager_page import TaskManagerPage
from proxy_manager_page import ProxyManagerPage
from billing_page import BillingPage
from accounts_page import AccountsPage

#Connected the backend
sys.path.append(r"C:\Users\mmira\Shoe-Palace-Bot-1")
from backend.proxy import Proxy_Manager

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
        print("Proxy file path:", self.proxy_manager.proxy_file)

        #Pages
        self.home_page = HomePage(self.switch_page)
        self.task_page = TaskManagerPage(self.switch_page)
        self.proxy_page = ProxyManagerPage(self.proxy_manager, self.switch_page)
        self.billing_page = BillingPage(self.switch_page)
        self.accounts_page = AccountsPage(self.switch_page)

        # add pages to stack
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.task_page)
        self.stack.addWidget(self.proxy_page)
        self.stack.addWidget(self.billing_page)
        self.stack.addWidget(self.accounts_page)

        self.page_map = {
            "home": 0,
            "tasks": 1,
            "proxies": 2,
            "billing": 3,
            "accounts": 4
        }

        QTimer.singleShot(0, lambda: asyncio.create_task(self.initialize_async()))

    async def initialize_async(self):
        await self.proxy_manager.load_proxies()
        self.proxy_page.load_groups()

    def switch_page(self, page_name):
        if page_name in self.page_map:
            self.stack.setCurrentIndex(self.page_map[page_name])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        sys.exit(loop.run_forever())
