from __init__ import *
from auxilary import Dialog, MplCanvas
from solve import solveWindow

class MainWindow(QMainWindow):

    def __init__(self, parent = None):
        # setting up windows title for the whole class
        super().__init__(parent)
        self.toVisit = []
        self.setWindowTitle('Route Planning Support')
        self.initUI()

    def initUI(self):
        # function prepairing each part of main window UI
        mainwindow = QWidget()

        hlayout = QHBoxLayout()
        vlayout = self.listWidget()

        hlayout.addLayout(vlayout)

        vlayout = self.mapWidget()

        hlayout.addLayout(vlayout)

        mainwindow.setLayout(hlayout)
        self.setCentralWidget(mainwindow)

    def listWidget(self):
        # creating vertical layout with cityList
        vlayout = QVBoxLayout()

        self.cityList = QListWidget()
        self.cityList.setMaximumWidth(600)
        self.populateCityList()
        self.cityList.itemChanged.connect(self.replot)
        self.cityList.itemActivated.connect(self.mark)
        vlayout.addWidget(self.cityList)
        return vlayout

    def populateCityList(self):
        # reading city list from database
        if path.exists("database.db"):
            con = sqlite3.connect("database.db")
        else:
            dlg = Dialog(2, None, [], "Database file missing!\nIt is neccessary for this application to work.")
        cur = con.cursor()
        try:
            cur.execute('PRAGMA TABLE_INFO(cities)')
            temp = cur.fetchall()
            if len(temp) != 5 or temp[0][1] != "id" or temp[0][2] != 'INTEGER' or temp[1][1] != 'node_id' \
                    or temp[1][2] != 'INTEGER' or temp[2][1] != "name" or temp[2][2] != 'TEXT' or temp[3][1] != 'lat' \
                    or temp[3][2] != 'REAL' or temp[4][1] != 'lon' or temp[4][2] != 'REAL':
                con.close()
                self.progressSignal.emit(2)
                return 0
            cur.execute('SELECT * FROM cities ORDER BY name')
            self.cities = cur.fetchall()
            cur.execute('SELECT max(id_to) FROM distance')
            size = cur.fetchone()[0]
            if size != len(self.cities):
                con.close()
                self.progressSignal.emit(2)
                return 0
            cur.execute('PRAGMA TABLE_INFO(distance)')
            temp = cur.fetchall()
            if len(temp) != 3 or temp[0][1] != 'id_from' or temp[0][2] != "INTEGER" or temp[1][1] != 'id_to' \
                    or temp[1][2] != "INTEGER" or temp[2][1] != 'distance' or temp[2][2] != "REAL":
                con.close()
                self.progressSignal.emit(2)
                return 0
        except sqlite3.OperationalError:
            # if there is no table cities in db, it means it is not mine db,
            # so we close connection, remove the file we just created and show error dialog
            con.close()
            dlg = Dialog(2, None, [], "Incorrect Database file found!\nPlease use correct one, provided by creator.")
        con.close()
        self.rows = []
        r = 1
        # filling list row by row with checkbox and city name
        for row in self.cities:
            rlay = QListWidgetItem()
            rlay.setCheckState(Qt.Unchecked)
            rlay.setText(row[2] + " (" + str(r) +")")
            rlay.setFont(QFont('Arial', 16))
            self.rows.append(rlay)
            self.cityList.insertItem(r,rlay)
            r+=1

    def replot(self):
        # itterating through rows and if it was marked we plot it red, otherwise blue
        self.maptile.axes.cla()
        for r, row in enumerate(self.rows):
            if r.checkState() == 2:
                self.maptile.axes.plot(self.cities[row][4], self.cities[row][3], marker = 'o', color = 'r')
                self.maptile.axes.text(self.cities[row][4], self.cities[row][3], row + 1, fontsize = 10)
                if self.cities[row] not in self.toVisit:
                    self.toVisit.append(self.cities[row])
            else:
                self.maptile.axes.plot(self.cities[row][4], self.cities[row][3], marker = 'o', color = 'b')
                if self.cities[row] in self.toVisit:
                    self.toVisit.remove(self.cities[row])   
        self.maptile.draw()

    def mark(self):
        # function to mark unmarked item and unmark marked one
        var = self.cityList.item(self.cityList.currentRow())
        var.setCheckState(Qt.Checked if var.checkState() == 0 else Qt.Unchecked)

    def mapWidget(self):
        # creating vertical layout with map, button and label
        vlayout = QVBoxLayout()

        self.maptile = MplCanvas(self, width = 5, height = 4, dpi = 100)
        self.maptile.setMinimumHeight(600)
        self.replot()

        vlayout.addWidget(self.maptile)

        box = QHBoxLayout()
        self.button = QPushButton()
        self.button.setText("Find Path")
        self.button.setMaximumWidth(300)
        self.button.pressed.connect(self.dialog)
        box.addWidget(self.button)
        box.setAlignment(Qt.AlignCenter)
        vlayout.addLayout(box)

        label = QLabel()
        label.setText("Source: openstreetmap.org\ngeofabrik.de")
        label.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        vlayout.addWidget(label)
        return vlayout    

    def dialog(self):
        # we check if user marked at least two cities and we create toVisit list
        self.button.setEnabled(False)
        if len(self.toVisit) < 2:
            # user did not mark at least two cities, we want to go back after he clicks ok
            self.dlg = Dialog(1, [self.button])
        else:
            # we have enough cities to continue so we calculate shortest path
            self.win = solveWindow(self.cities, self.toVisit, [self.button])
            self.button.setText("Working...")
