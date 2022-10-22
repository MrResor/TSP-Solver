from __init__ import Qtw, Qtc, Qtg, sqlite3, path
from auxilary import ErrDialog, MplCanvas
from solve import solveWindow
from db_connection import db


class MainWindow(Qtw.QMainWindow):
    """ Class for displaying main window and it's components.\n

        Attributes:\n
        progress_signal     -- signal for handling any errors.\n
        to_visit            -- initially empty list of cities chosen by user.\n
        cities              -- variable holding data from database.\n
        city_list           -- variable holding list widget that allows for
        choosing the cities by the user.\n
        map_tile            -- holds widget with plot.\n
        button              -- a button widget.\n
        dlg                 -- holds dialog widget.\n
        win                 -- widget which solves the TSP problem.\n

        Methods:\n
        init_ui             -- method to setup the user interface.\n
        list_widget         -- prepairs a list widget.\n
        polulate_city_list  -- fills up list widget with data from database.\n
        replot              -- redraws a plot to show chosen cities.\n
        mark                -- handles visual marking of the chosen cities.\n
        map_widget          -- Set's up right side of the UI, map and button.
    """
    progress_signal = Qtc.pyqtSignal(int)

    def __init__(self, parent=None):
        """ Constructor, changes window name and calls other setup functions.
        """
        super().__init__(parent)
        self.to_visit = []
        self.setWindowTitle('Route Planning Support')
        self.progress_signal.connect(self.handle_err_signal)
        db.error_signal.error_signal.connect(self.handle_err_signal)
        self.db = db()
        self.init_ui()

    def init_ui(self) -> None:
        """ Method that initialises all UI elements or calls respective
            functions to do so.
        """
        main_window = Qtw.QWidget()
        h_layout = Qtw.QHBoxLayout()
        v_layout = self.list_widget()
        h_layout.addLayout(v_layout)
        v_layout = self.map_widget()
        h_layout.addLayout(v_layout)
        main_window.setLayout(h_layout)
        self.setCentralWidget(main_window)

    def list_widget(self) -> Qtw.QVBoxLayout:
        """ Sets up list widget and calls a function that will populate it.
        """
        v_layout = Qtw.QVBoxLayout()
        self.city_list = Qtw.QListWidget()
        self.city_list.setMaximumWidth(600)
        self.populate_city_list()
        self.city_list.itemChanged.connect(self.replot)
        self.city_list.itemActivated.connect(self.mark)
        v_layout.addWidget(self.city_list)
        return v_layout

    def populate_city_list(self) -> None:
        """ Method responsible for connecting to database, obtaining list of cities,
            and lastly fills the widget with that data.
        """
        self.cities = self.db.querry('SELECT * FROM Cities')
        for city in self.cities:
            row = Qtw.QListWidgetItem()
            row.setCheckState(Qtc.Qt.Unchecked)
            row.setText(city[1] + " (" + str(city[0]) + ")")
            row.setFont(Qtg.QFont('Arial', 16))
            self.city_list.insertItem(city[0], row)

    def replot(self) -> None:
        """ Replots the plot of cities. Marked cities are plotted red,
            unmarked ones are blue.
        """
        self.map_tile.axes.cla()
        for r in range(self.city_list.count()):
            if self.city_list.item(r).checkState() == 2:
                self.map_tile.axes.plot(self.cities[r][3], self.cities[r][2],
                                        marker='o', color='r')
                self.map_tile.axes.text(self.cities[r][3], self.cities[r][2],
                                        self.cities[r][0], fontsize=10)
                if self.cities[r] not in self.to_visit:
                    self.to_visit.append(self.cities[r])
            else:
                self.map_tile.axes.plot(self.cities[r][3], self.cities[r][2],
                                        marker='o', color='b')
                if self.cities[r] in self.to_visit:
                    self.to_visit.remove(self.cities[r])
        self.map_tile.draw()

    def mark(self) -> None:
        """ Method that handles visual marking of the cities chosen
            by the user on the list.
        """
        var = self.city_list.item(self.city_list.currentRow())
        var.setCheckState(Qtc.Qt.Checked if var.checkState()
                          == 0 else Qtc.Qt.Unchecked)

    def map_widget(self) -> None:
        """ Setup for map widget, as well as few remaining elements.
        """
        v_layout = Qtw.QVBoxLayout()
        self.map_tile = MplCanvas(self)
        self.map_tile.setMinimumHeight(600)
        self.replot()
        v_layout.addWidget(self.map_tile)
        box = Qtw.QHBoxLayout()
        self.button = Qtw.QPushButton()
        self.button.setText("Find Path")
        self.button.setMaximumWidth(300)
        self.button.pressed.connect(self.dialog)
        box.addWidget(self.button)
        box.setAlignment(Qtc.Qt.AlignCenter)
        v_layout.addLayout(box)
        label = Qtw.QLabel()
        label.setText("Source: openstreetmap.org\ngeofabrik.de")
        label.setAlignment(Qtc.Qt.AlignBottom | Qtc.Qt.AlignRight)
        v_layout.addWidget(label)
        return v_layout

    def dialog(self) -> None:
        # we check if user marked at least two cities and we create to_visit list
        self.button.setEnabled(False)
        if len(self.to_visit) < 2:
            self.progress_signal.emit(0)
        else:
            # we have enough cities to continue so we calculate shortest path
            self.win = solveWindow(self.cities, self.to_visit)
            self.button.setText("Working...")

    def activate_button(self) -> None:
        """ Method called by signal to activate disabled button.
        """
        self.button.setEnabled(True)

    def handle_err_signal(self, code: int) -> None:
        """ Creates error message to present.
        """
        err = {
            0: f'Please choose more than two cities for the algorithm to work.',
            1: f'Database file missing! It is neccessary for this application to work.',
            2: f'Database file incorrect! Necessary table was not found.',
            3: f'Database file incorrect! Table Cities is not as expected.',
            4: f'Database file incorrect! Table Distance is not as expected.'
        }
        self.dlg = ErrDialog(err[code], code)
        if code == 0:
            self.dlg.button_control.connect(self.activate_button)
        self.dlg.exec_()
