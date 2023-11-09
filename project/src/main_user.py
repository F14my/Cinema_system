from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtWidgets import QMainWindow
from styles import *
from dialogs import Ticket
from scripts.ui.User import Ui_MainWindow
from db import Cinema


class UserWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.db = Cinema()
        self.db.connect()
        self.showMaximized()
        self.widget.hide()
        self.pricesWidget.hide()
        self.load_cinema_list()
        self.scrollArea.setWidgetResizable(True)
        self.selectCinema.currentTextChanged.connect(self.combo_checker)
        self.selectFilm.currentTextChanged.connect(self.combo_checker)
        self.selectTime.currentTextChanged.connect(self.combo_checker)
        self.date.selectionChanged.connect(self.load_time_list)
        self.paySeats.clicked.connect(self.pay)

    def combo_checker(self):
        ban_index = [0, -1]
        if self.selectTime.currentText() == "Выберите время":
            self.unload()
        if self.sender().objectName() == "selectCinema":
            self.load_film_list()
        if self.sender().objectName() == "selectFilm":
            self.load_time_list()
        if self.sender().objectName() == "selectTime" and self.sender().currentIndex() not in ban_index:
            self.load_hall_config()

    def unload(self):
        try:
            self.seats = [i.hide() for i in self.seats]
            self.seats = []
        except AttributeError:
            pass

    def load_prices(self):
        if self.selectTime.currentText() == "Выберите время":
            self.pricesWidget.hide()
            return
        prices_lbl = [self.pricelabel1, self.pricelabel2, self.pricelabel3, self.pricelabel4]
        prices_lines = [self.price1, self.price2, self.price3, self.price4]
        seat_types = {30: "Маленькие кресла", 40: "Средние кресла", 50: "Большие кресла", 60: "Диваны"}
        for i, size in enumerate(self.prices):
            prices_lbl[i].setText(seat_types[size])
            prices_lines[i].setText(str(self.prices[size]))
        prices_lbl = [i.hide() for i in prices_lbl if i.text() == ""]
        prices = [i.hide() for i in prices_lines if i.text() == ""]
        self.pricesWidget.show()

    def load_cinema_list(self):
        self.selectCinema.clear()
        self.selectCinema.addItem("Выберите кинотеатр")
        cinema_list = self.db.load_cinema_list()
        self.selectCinema.insertItems(1, cinema_list)

    def load_film_list(self):
        self.selectFilm.clear()
        self.selectFilm.addItem("Выберите фильм")
        film_list = set(self.db.load_film_list(self.selectCinema.currentText()))
        self.selectFilm.insertItems(1, film_list)

    def load_hall_config(self):
        cinema, film, time = self.selectCinema.currentText(), self.selectFilm.currentText(), self.selectTime.currentText()
        self.hall_name = self.db.check_hall(cinema, film, time)
        self.seats = []
        self.prices = dict()
        self.types = {30: "small", 40: "medium", 50: "big", 60: "gigant"}
        self.config = self.db.load_hall_config(self.selectCinema.currentText(), self.hall_name)
        self.book_config = eval(self.db.load_book_config(cinema, self.hall_name, self.date_str, time))
        if self.config:
            self.config = eval(self.config)
            for r, row in enumerate(self.config):
                for p, geometry in enumerate(row):
                    if geometry[2] not in self.prices:
                        self.prices[geometry[2]] = geometry[4]
                    self.temp = QPushButton(self)
                    self.temp.setGeometry(*geometry[:4])
                    enable = self.book_config[r][p]
                    self.temp.setEnabled(enable)
                    if self.temp.isEnabled():
                        self.temp.setStyleSheet(seat_style.replace("chair", self.types[self.temp.width()]))
                    else:
                        self.temp.setStyleSheet(reserved_seat_style.replace("chair", self.types[self.temp.width()]))
                    self.temp.setCheckable(True)
                    self.temp.setCursor(Qt.PointingHandCursor)
                    self.temp.setObjectName(f"seat_{r + 1}_{p + 1}")
                    self.temp.clicked.connect(self.seat_select)
                    self.temp.show()
                    self.temp.clicked.connect(self.select_cinema)
                    self.seats.append(self.temp)
        self.load_prices()

    def seat_select(self):
        self.seatList.clear()
        self.selected_seats = [str(int(i.objectName().split("_")[-2])) + " ряд " +
                               str(int(i.objectName().split("_")[-1])) + " место" for i in self.seats if i.isChecked()]
        pay = sum([self.prices[i.width()] for i in self.seats if i.isChecked()])
        self.toPay.setText(str(pay))
        if len(self.selected_seats) == 0:
            self.widget.hide()
            return
        self.widget.show()
        self.seatList.addItems(self.selected_seats)

    def select_cinema(self):
        if self.sender().isChecked():
            self.sender().setStyleSheet(selected_seat_style.replace("chair", self.types[self.sender().width()]))
        else:
            self.sender().setStyleSheet(seat_style.replace("chair", self.types[self.sender().width()]))

    def load_time_list(self):
        self.selectTime.clear()
        self.selectTime.addItem("Выберите время")
        cinema, film = self.selectCinema.currentText(), self.selectFilm.currentText()
        self.date_str = self.date.selectedDate().toString('yyyy/MM/dd')
        time_list = self.db.load_time_list(self.selectCinema.currentText(), self.selectFilm.currentText(),
                                           self.date_str)
        for time in time_list:
            hall_name = self.db.check_hall(cinema, film, time)
            self.db.delete_past_sessions(cinema, hall_name, self.date.selectedDate().toString('yyyy/MM/dd'), time)
        time_list = self.db.load_time_list(self.selectCinema.currentText(), self.selectFilm.currentText(),
                                           self.date_str)
        time_list = sorted(time_list, key=lambda x: (int(x[0:2]), int(x[3:5])))
        self.selectTime.insertItems(1, time_list)

    def pay(self):
        for seat in self.seats:
            if seat.isChecked():
                seat.setEnabled(False)
        for i in self.selected_seats:
            r, s = int(i.split(" ")[0]) - 1, int(i.split(" ")[-2]) - 1
            self.book_config[r][s] = False
        cinema, hall, config = self.selectCinema.currentText(), self.hall_name, self.config
        date, time = self.date.selectedDate().toString('yyyy/MM/dd'), self.selectTime.currentText()
        self.db.save_hall_config(cinema, hall, config)
        self.db.update_book_config(self.selectCinema.currentText(), self.hall_name, date, time, self.book_config)
        self.pay_animation()

    def pay_animation(self):
        self.movie = QMovie(f"scripts/other/payment.gif")
        self.payLabel.setMovie(self.movie)
        self.movie.start()
        self.movie.frameChanged.connect(self.frame_changed)

    def frame_changed(self, c):
        if self.movie.frameCount() == c + 1:
            self.movie.stop()
            self.payLabel.clear()
            self.selectCinema.setCurrentIndex(0)
            self.unload()
            items = [self.seatList.item(i).text() for i in range(self.seatList.count())]
            self.window = Ticket(items, str(self.hall_name))
            self.window.setIconSize(QSize(100, 100))
            self.window.setWindowIcon(QIcon(f"scripts/other/Icon.png"))
            self.window.show()
            self.seat_select()
            self.load_prices()
