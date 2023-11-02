import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from db import Auth
from string import ascii_letters
from resorces import AuthReg


class Registration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.path = os.getcwd()
        self.path = self.path.replace("\\", "/")
        uic.loadUi(f"{self.path}/Registration.ui", self)
        self.initUI()

    def initUI(self):
        self.nextWindow = None
        self.login.textEdited.connect(self.changer)
        self.password.textEdited.connect(self.changer)
        self.confirmPassword.textEdited.connect(self.changer)
        self.admin.clicked.connect(self.changerRadio)
        self.user.clicked.connect(self.changerRadio)
        self.confirmButton.clicked.connect(self.check_data)

    def check_login(self, login):
        if all(map(lambda c: c in ascii_letters, login)):
            return True
        self.statusbar.showMessage("Никнейм должен быть на английском")

    def check_safety_data(self):
        if len(self.password.text()) <= 9:
            self.statusbar.showMessage("Слишком короткий пароль. Должно быть больше 9 символов!")
        elif len([i for i in self.password.text() if i.isdigit()]) == 0:
            self.statusbar.showMessage("Пароль должен содержать в себе цифры!")
        elif len([i for i in self.password.text() if i.isalpha()]) == 0:
            self.statusbar.showMessage("Пароль должен содержать в себе буквы!")
        else:
            return True

    def check_data(self):
        if self.login.text() == "":
            self.statusbar.showMessage("Придумайте никнейм!")
        elif self.password.text() == "":
            self.statusbar.showMessage("Придумайте пароль!")
        elif self.confirmPassword.text() == "":
            self.statusbar.showMessage("Повторите пароль!")
        elif self.password.text() != self.confirmPassword.text():
            self.statusbar.showMessage("Пароли не совпадают!")
        else:
            if self.check_safety_data() is True and self.check_login(self.login.text()) is True:
                self.confirm()

    def confirm(self):
        db = Auth()
        db.connect()
        if db.check_login_free(self.login.text()) is False:
            self.statusbar.showMessage("Такой никнейм уже используется :(")
        else:
            admin = True if "5" in self.admin.styleSheet() else False
            db.add_user(self.login.text(), self.password.text(), admin)
            db.close()
            self.statusbar.showMessage("ok_reg")

    def changerRadio(self):
        name = self.user if self.sender().objectName() == "admin" else self.admin
        sender_style = f"""border-image: url(:/rectangles/Rectangle5.png);
        image: url(:/rectangleImages/{self.sender().objectName()}.png);"""
        name_style = f"""border-image: url(:/rectangles/Rectangle4.png);
        image: url(:/rectangleImages/{name.objectName()}.png);"""
        self.sender().setStyleSheet(sender_style)
        name.setStyleSheet(name_style)

    def changer(self):
        style = f"""border-image: url(:/rectangles/Rectangle2.png);
                    image: url(:/rectangleImages/{self.sender().objectName()}.png);"""
        if self.sender().text() == "":
            self.sender().setStyleSheet(style)
        else:
            self.sender().setStyleSheet(f"border-image: url(:/rectangles/Rectangle2.png);")
