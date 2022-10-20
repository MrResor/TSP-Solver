from __init__ import sqlite3, path, Qtc
from decorators import db_con


class signal(Qtc.QObject):
    error_signal = Qtc.pyqtSignal(int)


class db():

    error_signal = signal()

    @db_con
    def __init__(self):
        if path.exists("database.db"):
            self._con = sqlite3.connect("database.db")
            self._cur = self._con.cursor()
        else:
            raise FileNotFoundError
