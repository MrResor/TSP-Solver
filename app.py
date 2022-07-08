from main_window_class import MainWindow
from __init__ import *
import sys

class Application:
    """Class responsible for PyQt initialization and exiting the program when it is finished
    
        Atributes:
        app     -- holds application, for which we will present windows
        win     -- holds main window and it's contents
    """
    def __init__(self, argv):
        self.app = QApplication(argv)
        self.win = MainWindow()
        self.win.show()
        sys.exit(self.app.exec_())