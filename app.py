from main_window_class import MainWindow
from __init__ import *
import sys

class Application:
    """Class responsible for PyQt initialization and exiting the program when it is finished
        Atributes:
        app  -- engine responsible for code to database communication 
        base    -- variable holding the schema of automapped database
        session -- variable responsible for passing querries
        Methods:
        refresh -- refreshes automaping of the database
    """
    def __init__(self, argv):
        self.app = QApplication(argv)
        self.win = MainWindow()
        self.win.show()
        sys.exit(self.app.exec_())