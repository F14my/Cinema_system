import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from db import Auth
from resorces import AuthReg


class Authorization(QMainWindow):
    def __init__(self):
        super().__init__()
        os.chdir("../scripts")
        self.path = os.getcwd()
        self.path = self.path.replace("\\", "/")
        uic.loadUi(f"{self.path}/Auth.ui", self)
        self.initUI()

    def initUI(self):
        self.login.textEdited.connect(self.changer)
        self.password.textEdited.connect(self.changer)
        self.enterButton.clicked.connect(self.enter)

    def enter(self):
        db = Auth()
        db.connect()
        if db.check_user_in_system(self.login.text()) is False:
            self.statusbar.showMessage("Такого пользователя не существует. Зарегистрируйтесь!")
        elif db.check_password(self.login.text(), self.password.text()) is False:
            self.statusbar.showMessage("Невреный пароль")
        else:
            db.close()
            self.statusbar.showMessage("ok_login")

    def changer(self):
        style = f"""border-image: url(:/rectangles/Rectangle2.png);
                    image: url(:/rectangleImages/{self.sender().objectName()}.png);"""
        if self.sender().text() == "":
            self.sender().setStyleSheet(style)
        else:
            self.sender().setStyleSheet(f"border-image: url(:/rectangles/Rectangle2.png);")
