import sys
from PyQt5.QtWidgets import QApplication
from auth import Authorization
from registration import Registration
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from main_admin import AdminWindow
from main_user import UserWindow
from PyQt5 import QtGui
from resorces import AdminCinema
from resorces import AuthReg

window = Authorization


def setPath():
    QtGui.QFontDatabase.addApplicationFont(fr'scripts/other/VAG_WORLD.ttf')


def setIcon(window):
    window.setWindowIcon(QIcon(f"scripts/other/Icon.png"))
    window.setIconSize(QSize(100, 100))


def show_main_admin_window():
    global window
    setPath()
    window = AdminWindow()
    setIcon(window)
    window.exit.clicked.connect(show_authorization_window)
    window.show()


def show_main_user_window():
    global window
    setPath()
    window = UserWindow()
    setIcon(window)
    window.exit.clicked.connect(show_authorization_window)
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
    if window.statusbar.currentMessage() == "ok_admin":
        show_main_admin_window()
    if window.statusbar.currentMessage() == "ok_user":
        show_main_user_window()


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
