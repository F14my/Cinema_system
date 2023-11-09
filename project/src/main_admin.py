import datetime
from PyQt5.QtWidgets import QListView, QInputDialog, QPushButton, QLabel, QTableWidgetItem
from db import Cinema
from PyQt5.QtCore import Qt
from styles import *
from dialogs import *
from scripts.ui.Main import Ui_MainWindow


class AdminWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.seatcount = 0
        self.ban_words = ["Выберите зал", "Выберите кинотеатр"]
        self.seats = []
        self.blocker()
        self.db = Cinema()
        self.init_click()
        self.showMaximized()
        self.selectHall.setView(QListView())
        self.db.connect()
        self.load_cinema()

    def create_seats(self):
        self.temp = QPushButton(self)
        self.temp.setStyleSheet(seat_style.replace("chair", self.sender().objectName()))
        self.temp.setGeometry(self.sender().geometry())
        self.temp.setCheckable(True)
        self.temp.setCursor(Qt.PointingHandCursor)
        self.seats.append(self.temp)
        self.temp.show()

    def init_click(self):
        self.selectCinema.currentTextChanged.connect(self.combo_checker)
        self.selectHall.currentTextChanged.connect(self.combo_checker)
        self.small.clicked.connect(self.create_seats)
        self.medium.clicked.connect(self.create_seats)
        self.big.clicked.connect(self.create_seats)
        self.gigant.clicked.connect(self.create_seats)
        self.createSeats.clicked.connect(self.show_create_window)
        self.addSession.clicked.connect(self.add_session_window)
        self.deleteSession.clicked.connect(self.delete_session)
        self.updateButt.clicked.connect(self.update)
        self.saveConfig.clicked.connect(self.save_hall_config)
        self.clearSeats.clicked.connect(self.clear_seats)

    def clear_seats(self):
        for i in self.seats:
            i.hide()
        self.seats = []

    def blocker(self):
        try:
            self.blockLabel.hide()
            self.blockLabel2.hide()
        except AttributeError:
            pass
        self.blockLabel = QLabel(self)
        self.blockLabel.setGeometry(536, 0, 1381, 1011)
        self.blockLabel2 = QLabel(self)
        self.blockLabel2.setGeometry(0, 140, 530, 901)
        if self.selectCinema.currentIndex() not in [-1, 0] and self.selectHall.currentIndex() not in [-1, 0]:
            self.blockLabel.hide()
            self.blockLabel2.hide()
        else:
            self.blockLabel.show()
            self.blockLabel2.show()

    def generate_seats(self, row_count, seat_count, seat_size, seat_type):
        for i in self.seats:
            i.hide()
        self.seats = []
        geometry = [1000, 200, seat_size, seat_size]
        size_x = 780
        size_y = 700
        seat_name = {"Маленькие кресла": "small", "Средние кресла": "medium", "Большие кресла": "big",
                     "Диваны": "gigant"}
        seat_indent = (size_x - (seat_size * seat_count)) // (seat_count - 1)
        row_indent = (size_y - (seat_size * row_count)) // (row_count - 1)
        for i in range(row_count):
            for k in range(seat_count):
                self.seat = QPushButton(self)
                self.seat.setStyleSheet(seat_style.replace("chair", seat_name[seat_type]))
                self.seat.setGeometry(*geometry)
                self.seat.setCheckable(True)
                self.seat.setCursor(Qt.PointingHandCursor)
                self.seats.append(self.seat)
                self.seat.show()
                geometry[0] += seat_indent + seat_size
            geometry[0] = 1000
            geometry[1] += row_indent + seat_size

    def show_create_window(self):
        window = CreateSeats(self)
        window.show()

    def add_session_window(self):
        window = AddSession(self)
        window.show()

    def update(self):
        self.load_sessions()

    def delete_session(self):
        dialog = QInputDialog(self)
        id_session, ok_pressed = dialog.getText(self, "ScreenPass", "Введите айди сессии для удаления")
        if ok_pressed:
            if id_session.isalpha():
                return
            cinema, hall, row = self.selectCinema.currentText(), self.selectHall.currentText(), int(id_session) - 1
            if self.sessions.rowCount() == 0:
                return
            self.db.delete_session(cinema, hall, self.sessions.item(row, 0).text(), self.sessions.item(row, 1).text())
            self.sessions.removeRow(row)

    def load_sessions(self):
        self.sessions.setRowCount(0)
        sessions = self.db.load_session(self.selectCinema.currentText(), self.selectHall.currentText())
        cinema, hall = self.selectCinema.currentText(), self.selectHall.currentText()
        if len(sessions) != 0:
            for session in sessions:
                status = self.db.check_film_status(session[0], session[1], session[3])
                if status == "Фильм прошёл":
                    self.db.delete_session(*[i for i in [cinema, hall] + session[:2]])
                    return
                self.sessions.setRowCount(self.sessions.rowCount() + 1)
                for i, elem in enumerate(session + [status]):
                    self.sessions.setItem(self.sessions.rowCount() - 1, i, QTableWidgetItem(str(elem)))
            self.sessions.resizeColumnsToContents()

    def add_session(self, date, time, film_name, duration):
        date, time = date.toString('yyyy/MM/dd'), time.toString()
        status = self.db.check_film_status(date, time, int(duration))
        self.sessions.setRowCount(self.sessions.rowCount() + 1)
        for k, i in enumerate([date, time, film_name, duration, status]):
            self.sessions.setItem(self.sessions.rowCount() - 1, k, QTableWidgetItem(str(i)))
        self.sessions.resizeColumnsToContents()
        self.db.add_session(self.selectCinema.currentText(), self.selectHall.currentText(), date, time, film_name,
                            duration)

    def check_hall_is_free(self, date, time, duration):
        for row in range(self.sessions.rowCount()):
            if self.sessions.item(row, 0).text() == date:
                h1, m1, s1 = self.sessions.item(row, 1).text().split(":")
                h2, m2, s2 = time.split(":")
                t1 = datetime.timedelta(hours=int(h1), minutes=int(m1), seconds=int(s1))
                t2 = datetime.timedelta(hours=int(h2), minutes=int(m2), seconds=int(s2))
                time_difference = str(t2 - t1) if t2 > t1 else str(t1 - t2)
                hours, minutes, seconds = map(int, time_difference.split(':'))
                total_minutes = hours * 60 + minutes
                if t2 > t1:
                    if total_minutes < int(self.sessions.item(row, 3).text()) + 10:
                        return False
                    return True
                if total_minutes < int(duration) + 10:
                    return False
                return True

    def mouseMoveEvent(self, event):
        trash = None
        try:
            for k, seat in enumerate(self.seats):
                if seat.isChecked():
                    seat.move(int(round(event.x(), -1)), int(round(event.y(), -1)))
                if seat.x() in [i for i in range(550, 611)] and seat.y() in [i for i in range(350, 421)]:
                    trash = k
        except AttributeError:
            pass
        if trash is not None:
            self.seats[trash].hide()
            self.seats.pop(trash)

    def combo_checker(self):
        if self.selectCinema.currentText() == "Добавить кинотеатр":
            self.add_cinema()
        if self.selectHall.currentText() == "Добавить зал":
            self.add_hall()
        if self.sender().objectName() == "selectCinema":
            self.load_hall()
        if self.selectCinema.currentIndex() not in [-1, 0] and self.selectHall.currentIndex() not in [-1, 0]:
            self.load_sessions()
            self.load_hall_config()
        self.blocker()

    def load_cinema(self):
        self.selectCinema.insertItems(1, self.db.load_cinema_list())

    def load_hall(self):
        cinema = self.selectCinema.currentText()
        update = self.db.load_hall_list(cinema)
        self.selectHall.clear()
        self.selectHall.addItems(["Выберите зал", "Добавить зал"])
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

    def load_hall_config(self):
        for i in self.seats:
            i.hide()
        self.seats = []
        self.types = {30: "small", 40: "medium", 50: "big", 60: "gigant"}
        config = self.db.load_hall_config(self.selectCinema.currentText(), self.selectHall.currentText())
        if config:
            config = eval(config)
            for r, row in enumerate(config):
                for p, geometry in enumerate(row):
                    self.temp = QPushButton(self)
                    self.temp.setGeometry(*geometry[:4])
                    self.temp.setStyleSheet(seat_style.replace("chair", self.types[self.temp.width()]))
                    self.temp.setCheckable(True)
                    self.temp.setCursor(Qt.PointingHandCursor)
                    self.temp.show()
                    self.seats.append(self.temp)

    def check_prices(self):
        price = False
        for seat in self.seats:
            if seat.width() == 30 and self.smallPrice.text().isdigit():
                price = True
            if seat.width() == 40 and self.mediumPrice.text().isdigit():
                price = True
            if seat.width() == 50 and self.bigPrice.text().isdigit():
                price = True
            if seat.width() == 60 and self.gigantPrice.text().isdigit():
                price = True
        return price

    def save_hall_config(self):
        if self.check_prices() is False:
            self.statusbar.showMessage("Укажите цены на созданные сиденья!")
            return
        types = {30: self.smallPrice.text(),
                 40: self.mediumPrice.text(),
                 50: self.bigPrice.text(),
                 60: self.gigantPrice.text()}
        rows_seat = dict()
        for i in self.seats:
            if i.y() not in rows_seat:
                rows_seat[i.y()] = []
            rows_seat[i.y()].append(i)
        row = sorted(rows_seat.keys())
        seats = []
        for i in row:
            seats.append(rows_seat[i])
        seats = [[list(k.geometry().getRect()) + [int(types[k.width()])] for k in i] for i in seats]
        booked_seats = [[True for k in range(len(i))] for i in seats]
        seats = str(seats)
        booked_seats = str(booked_seats)
        self.db.save_hall_config(self.selectCinema.currentText(), self.selectHall.currentText(), seats)
        self.db.save_book_config(self.selectCinema.currentText(), self.selectHall.currentText(), booked_seats)
        self.statusbar.showMessage("Конфигурация зала успешна сохранена!")
