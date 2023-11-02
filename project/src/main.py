import sys
import os
from PyQt5.QtWidgets import QApplication
from auth import Authorization
from registration import Registration
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from main_admin import AdminWindow


window = None


def setPath():
    os.chdir("../scripts")


def setIcon(window):
    window.setWindowIcon(QIcon(f"C:/Lyceum_lessons/project/scripts/images/Icon.png"))
    window.setIconSize(QSize(100, 100))


def show_main_admin_window():
    global window
    setPath()
    window = AdminWindow()
    setIcon(window)
    window.show()


def show_authorization_window():
    global window
    setPath()
    window = Authorization()
    setIcon(window)
    window.regButton.clicked.connect(show_registration_window)
    window.enterButton.clicked.connect(check_status_bar)
    window.show()


def check_status_bar():
    global window
    if window.statusbar.currentMessage() == "ok_reg":
        show_authorization_window()
    if window.statusbar.currentMessage() == "ok_login":
        show_main_admin_window()


def show_registration_window():
    global window
    setPath()
    window = Registration()
    setIcon(window)
    window.backButton.clicked.connect(show_authorization_window)
    window.statusbar.messageChanged.connect(check_status_bar)
    window.show()


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    show_authorization_window()
    sys.excepthook = except_hook
    sys.exit(app.exec())
