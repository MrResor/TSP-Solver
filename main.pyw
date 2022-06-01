from __init__ import *
from main_window_class import *
import sys

if __name__ == '__main__':
    # Run the window
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    