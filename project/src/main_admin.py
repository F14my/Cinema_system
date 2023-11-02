import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QListView, QComboBox, QInputDialog, QPushButton
from resorces import AdminCinema
from db import Cinema


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.path = os.getcwd()
        self.path = self.path.replace("\\", "/")
        uic.loadUi(f"{self.path}/Main.ui", self)
        self.initUI()
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self.seat1.isChecked():
            self.seat1.move(round(event.x(), -1), round(event.y(), -1))

    def initUI(self):
        self.showMaximized()
        self.selectCinema.currentTextChanged.connect(self.combo_checker)
        self.selectHall.currentTextChanged.connect(self.combo_checker)
        self.createSeat.clicked.connect(self.create_seat)
        self.db = Cinema()
        self.db.connect()
        self.load_cinema()

    def create_seat(self):
        self.seat1 = QPushButton(self)
        self.seat1.resize(40, 40)
        self.seat1.move(700, 100)
        self.seat1.setCheckable(True)
        self.seat1.show()


    def combo_checker(self):
        if self.selectCinema.currentText() == "Добавить кинотеатр":
            self.add_cinema()
        if self.selectHall.currentText() == "Добавить зал":
            self.add_hall()
        if self.sender().objectName() == "selectCinema":
            self.load_hall()

    def load_cinema(self):
        self.selectCinema.insertItems(1, self.db.load_cinema_list())

    def load_hall(self):
        cinema = self.selectCinema.currentText()
        update = self.db.load_hall_list(cinema)
        self.selectHall.insertItems(1, update)
        if len(update) == 0:
            self.selectHall.clear()
            self.selectHall.addItems(["Выберите зал", "Добавить зал"])

    def add_cinema(self):
        name, ok_pressed = QInputDialog.getText(self, "ScreenPass", "Введите название кинотеатра")
        if ok_pressed:
            self.sender().setCurrentIndex(0)
            self.sender().insertItems(1, [name])
            self.sender().setCurrentIndex(1)
            self.db.add_cinema(self.selectCinema.currentText())
        else:
            self.sender().setCurrentIndex(0)

    def add_hall(self):
        name, ok_pressed = QInputDialog.getText(self, "ScreenPass", "Введите название зала")
        if ok_pressed:
            self.sender().setCurrentIndex(0)
            self.sender().insertItems(1, [name])
            self.sender().setCurrentIndex(1)
            self.db.add_hall(self.selectCinema.currentText(), self.selectHall.currentText())
        else:
            self.sender().setCurrentIndex(0)
