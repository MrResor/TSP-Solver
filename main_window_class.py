from __init__ import Qtw, Qtc, Qtg, sqlite3, path
from auxilary import ErrDialog, MplCanvas
from solve import solveWindow


class MainWindow(Qtw.QMainWindow):
    """ Class for displaying main window and it's components.\n

        Attributes:\n
        progress_signal -- signal for handling any errors
        

    """
    progress_signal = Qtc.pyqtSignal(int)

    def __init__(self, parent=None):
        # setting up windows title for the whole class
        super().__init__(parent)
        self.toVisit = []
        self.setWindowTitle('Route Planning Support')
        self.progress_signal.connect(self.handle_err_signal)
        self.initUI()

    def initUI(self):
        # function prepairing each part of main window UI
        mainwindow = Qtw.QWidget()

        hlayout = Qtw.QHBoxLayout()

        vlayout = self.list_widget()
        hlayout.addLayout(vlayout)

        vlayout = self.map_widget()

        hlayout.addLayout(vlayout)

        mainwindow.setLayout(hlayout)
        self.setCentralWidget(mainwindow)

    def list_widget(self):
        # creating vertical layout with cityList
        vlayout = Qtw.QVBoxLayout()
        self.cityList = Qtw.QListWidget()
        self.cityList.setMaximumWidth(600)
        if (self.populateCityList()) == 0:
            return 0
        self.cityList.itemChanged.connect(self.replot)
        self.cityList.itemActivated.connect(self.mark)
        vlayout.addWidget(self.cityList)
        return vlayout

    def populateCityList(self):
        # reading city list from database
        if path.exists("database.db"):
            con = sqlite3.connect("database.db")
        else:
            dlg = ErrDialog("Database file missing!\nIt is neccessary for this\
                            application to work.", 2)
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
        self.rows = []
        r = 1
        # filling list row by row with checkbox and city name
        for row in self.cities:
            rlay = Qtw.QListWidgetItem()
            rlay.setCheckState(Qtc.Qt.Unchecked)
            rlay.setText(row[1] + " (" + str(r) + ")")
            rlay.setFont(Qtg.QFont('Arial', 16))
            self.rows.append(rlay)
            self.cityList.insertItem(r, rlay)
            r += 1

    def replot(self):
        # itterating through rows and if it was marked we plot it red, otherwise blue
        self.maptile.axes.cla()
        for r, row in enumerate(self.rows):
            if row.checkState() == 2:
                self.maptile.axes.plot(self.cities[r][3], self.cities[r][2],
                                       marker='o', color='r')
                self.maptile.axes.text(self.cities[r][3], self.cities[r][2],
                                       r+1, fontsize=10)
                if self.cities[r] not in self.toVisit:
                    self.toVisit.append(self.cities[r])
            else:
                self.maptile.axes.plot(self.cities[r][3], self.cities[r][2],
                                       marker='o', color='b')
                if self.cities[r] in self.toVisit:
                    self.toVisit.remove(self.cities[r])
        self.maptile.draw()

    def mark(self):
        # function to mark unmarked item and unmark marked one
        var = self.cityList.item(self.cityList.currentRow())
        var.setCheckState(Qtc.Qt.Checked if var.checkState()
                          == 0 else Qtc.Qt.Unchecked)

    def map_widget(self):
        # creating vertical layout with map, button and label
        vlayout = Qtw.QVBoxLayout()

        self.maptile = MplCanvas(self)
        self.maptile.setMinimumHeight(600)
        self.replot()

        vlayout.addWidget(self.maptile)

        box = Qtw.QHBoxLayout()
        self.button = Qtw.QPushButton()
        self.button.setText("Find Path")
        self.button.setMaximumWidth(300)
        self.button.pressed.connect(self.dialog)
        box.addWidget(self.button)
        box.setAlignment(Qtc.Qt.AlignCenter)
        vlayout.addLayout(box)

        label = Qtw.QLabel()
        label.setText("Source: openstreetmap.org\ngeofabrik.de")
        label.setAlignment(Qtc.Qt.AlignBottom | Qtc.Qt.AlignRight)

        vlayout.addWidget(label)
        return vlayout

    def dialog(self):
        # we check if user marked at least two cities and we create toVisit list
        self.button.setEnabled(False)
        if len(self.toVisit) < 2:
            # user did not mark at least two cities, we want to go back after he clicks ok
            self.dlg = ErrDialog("Please choose more than two cities for " +
                                 "the algorithm to work.", 0)
            self.dlg.button_control.connect(self.Activate_button)
            self.dlg.exec_()
        else:
            # we have enough cities to continue so we calculate shortest path
            self.win = solveWindow(self.cities, self.toVisit)
            self.button.setText("Working...")

    def activate_button(self):
        self.button.setEnabled(True)

    def handle_err_signal(self, code: int) -> None:
        dlg = ErrDialog("Incorrect Database file found!\nPlease use\
                correct one, provided by creator.", code)
        # def dbDataLoad(self):
        # function to load data from db and check it's contents correctness
