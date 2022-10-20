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
        con = sqlite3.connect("database")
        cur = con.cursor()
        # try:
        #     cur.execute('PRAGMA TABLE_INFO(cities)')
        #     temp = cur.fetchall()
        #     if len(temp) != 5 or temp[0][1] != "id" or temp[0][2] != 'INTEGER' or temp[1][1] != 'node_id' \
        #             or temp[1][2] != 'INTEGER' or temp[2][1] != "name" or temp[2][2] != 'TEXT' or temp[3][1] != 'lat' \
        #             or temp[3][2] != 'REAL' or temp[4][1] != 'lon' or temp[4][2] != 'REAL':
        #         con.close()
        #         self.progressSignal.emit(2)
        #         return 0
        #     cur.execute('SELECT * FROM cities ORDER BY name')
        cur.execute('SELECT * FROM Cities')
        #     self.cities = cur.fetchall()
        self.cities = cur.fetchall()
        #     cur.execute('SELECT max(id_to) FROM distance')
        cur.execute('SELECT max(id_to) from Distance')
        #     size = cur.fetchone()[0]
        size = cur.fetchone()[0]
        #     if size != len(self.cities):
        #         con.close()
        #         self.progressSignal.emit(2)
        #         return 0
        #     cur.execute('PRAGMA TABLE_INFO(distance)')
        #     temp = cur.fetchall()
        #     if len(temp) != 3 or temp[0][1] != 'id_from' or temp[0][2] != "INTEGER" or temp[1][1] != 'id_to' \
        #             or temp[1][2] != "INTEGER" or temp[2][1] != 'distance' or temp[2][2] != "REAL":
        #         con.close()
        #         self.progressSignal.emit(2)
        #         return 0
        # except sqlite3.OperationalError:
        #     # if there is no table cities in db, it means it is not mine db,
        #     # so we close connection, remove the file we just created and show error dialog
        #     self.progressSignal.emit(2)
        #     con.close()
        #     return 0
        con.close()
        # filling list row by row with checkbox and city name
        for row in self.cities:
            rlay = Qtw.QListWidgetItem()
            rlay.setCheckState(Qtc.Qt.Unchecked)
            rlay.setText(row[1] + " (" + str(row[0]) + ")")
            rlay.setFont(Qtg.QFont('Arial', 16))
            self.city_list.insertItem(row[0], rlay)

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
            # user did not mark at least two cities, we want to go back after he clicks ok
            self.dlg = ErrDialog("Please choose more than two cities for " +
                                 "the algorithm to work.", 0)
            self.dlg.button_control.connect(self.activate_button)
            self.dlg.exec_()
        else:
            # we have enough cities to continue so we calculate shortest path
            self.win = solveWindow(self.cities, self.to_visit)
            self.button.setText("Working...")

    def activate_button(self) -> None:
        """ Method called by signal to activate disabled button.
        """
        self.button.setEnabled(True)

    def handle_err_signal(self, code: int) -> None:
        if code == 1:
            self.dlg = ErrDialog(
                f'Database file missing! It is neccessary for this application to work.', code)
            self.dlg.exec_()
        # dlg = ErrDialog("Incorrect Database file found!\nPlease use\
        #         correct one, provided by creator.", code)
        # def dbDataLoad(self):
        # function to load data from db and check it's contents correctness
