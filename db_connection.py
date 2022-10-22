from __init__ import sqlite3, path, Qtc
from decorators import db_con, db_querry, db_data
from numpy import array


class signal(Qtc.QObject):
    """ Dummy for signal, class needs to inherit from Qobject
        to use signals.\n

        Attributes:\n
        error_signal    -- pyqt signal to send out when error is caught.
    """
    error_signal = Qtc.pyqtSignal(int)


class db():

    error_signal = signal()

    @db_con
    def __init__(self) -> None:
        """ Connects to database and creates cursor for querries.
        """
        if path.exists("database.db"):
            self._con = sqlite3.connect("database.db")
            self._cur = self._con.cursor()
        else:
            raise FileNotFoundError
        self.ensure_data_integrity()

    @db_querry
    def querry(self, querry: str) -> list:
        """ Runs anny passed querries and returns result,
            wrapped to catch any db errors.
        """
        self._cur.execute(querry)
        return self._cur.fetchall()

    @db_data
    def ensure_data_integrity(self) -> None:
        """ Checks if the data in database is saved in a format
            that will not break the program.
        """
        size1 = self.querry('SELECT COUNT(*) FROM Cities')
        size2 = self.querry('SELECT MAX(ID) FROM Cities')
        if size1 != size2:
            raise RuntimeError("Table Cities is incorrect.")
        data = self.querry('PRAGMA TABLE_INFO(Cities)')
        data = array([list(d) for d in data])
        if (data[:, 1] != ['ID', 'Name', 'Lat', 'Lon']).any() or \
                (data[:, 2] != ['INTEGER', 'TEXT', 'REAL', 'REAL']).any():
            raise RuntimeError("Table Cities is incorrect.")
        size2 = self.querry('SELECT MAX(ID_to) FROM Distance')
        if size1 != size2:
            raise RuntimeError("Table Distance is incorrect.")
        data = self.querry('PRAGMA TABLE_INFO(Distance)')
        data = array([list(d) for d in data])
        if (data[:, 1] != ['ID_from', 'ID_to', 'Distance']).any() or \
                (data[:, 2] != ['INTEGER', 'INTEGER', 'REAL']).any():
            raise RuntimeError("Table Distance is incorrect.")

    def __del__(self) -> None:
        """ Closes database connection.
        """
        self._con.close()
