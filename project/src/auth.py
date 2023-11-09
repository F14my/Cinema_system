from PyQt5.QtWidgets import QMainWindow
from db import Auth
from scripts.ui.Auth import Ui_MainWindow


class Authorization(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
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
            if db.check_user_status(self.login.text()) == 1:
                db.close()
                self.statusbar.showMessage("ok_admin")
            else:
                db.close()
                self.statusbar.showMessage("ok_user")

    def changer(self):
        style = f"""border-image: url(:/rectangles/Rectangle2.png);
                    image: url(:/rectangleImages/{self.sender().objectName()}.png);"""
        if self.sender().text() == "":
            self.sender().setStyleSheet(style)
        else:
            self.sender().setStyleSheet(f"border-image: url(:/rectangles/Rectangle2.png);")
