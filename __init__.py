# file containing most of the imports the imports
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QCheckBox, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QPushButton, QDialog, QDialogButtonBox
from PyQt5.QtGui import QPixmap, QKeySequence, QFont
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtSlot
import matplotlib.figure as mplf
import matplotlib.backends.backend_qt5agg as mplb
import sqlite3
from random import random, randrange
from os import path