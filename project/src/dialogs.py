from PyQt5.QtWidgets import QMainWindow
from scripts.ui.CreateSeats import Ui_MainWindow
from scripts.ui.Ticket import Ui_MainWindow2
from scripts.ui.AddSession import Ui_MainWindow3


class CreateSeats(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.sizes = {"Маленькие кресла": [30, 20], "Средние кресла": [40, 15], "Большие кресла": [50, 13],
                      "Диваны": [60, 10]}
        self.next.clicked.connect(self.close_window)
        self.seatType.currentTextChanged.connect(self.changer)

    def changer(self):
        self.rowCount.setMaximum(self.sizes[self.seatType.currentText()][1])
        self.seatCount.setMaximum(self.sizes[self.seatType.currentText()][1])

    def close_window(self):
        self.parent().generate_seats(int(self.rowCount.text()), int(self.seatCount.text()),
                                     self.sizes[self.seatType.currentText()][0], self.seatType.currentText())
        self.close()


class Ticket(QMainWindow, Ui_MainWindow2):
    def __init__(self, seats, hall, parent=None):
        super().__init__(parent)
        self.seats = seats
        self.setupUi(self)
        self.hall.setText(hall)
        self.load_seats()

    def load_seats(self):
        self.seatList.addItems(self.seats)


class AddSession(QMainWindow, Ui_MainWindow3):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.next.clicked.connect(self.close_window)

    def checker(self):
        if not self.duration.text().isdigit():
            self.statusbar.showMessage("Данные заполнены некорректно!")
            return False
        if self.parent().check_hall_is_free(self.date.selectedDate().toString('yyyy/MM/dd'),
                                            self.time.time().toString(), self.duration.text()) is False:
            self.statusbar.showMessage("Этот зал занят в это время!")
            return False
        return True

    def close_window(self):
        if self.checker():
            self.parent().add_session(self.date.selectedDate(), self.time.time(), self.filmName.text(),
                                      self.duration.text())
            self.close()
