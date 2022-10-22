from __init__ import Qtw, Qtc, path, sqlite3, randrange, random
from auxilary import ErrDialog, ResDialog
from threading import Thread
import pandas as pd


class solveWindow(Qtw.QWidget):
    # class for solving real TSP problem with cities given by user
    progressSignal = Qtc.pyqtSignal(int)
    button_control = Qtc.pyqtSignal()

    def __init__(self, verification, toVisit):
        # constructor of solveWindow class
        super().__init__()
        self.setWindowFlags(Qtc.Qt.WindowTitleHint)
        self.setWindowTitle("Working...")
        self.verification = verification
        self.toVisit = toVisit
        self.progressSignal.connect(self.results)
        self.layout = Qtw.QVBoxLayout()
        self.message = Qtw.QLabel("Calculating Shortest path\nPlease wait...")
        self.message.setAlignment(Qtc.Qt.AlignCenter)
        self.layout.addWidget(self.message)
        self.setLayout(self.layout)
        self.show()
        t = Thread(target=lambda: self.algorithm(toVisit))
        t.start()

    def results(self, value: int) -> None:
        # function for displaying dialog with results
        self.hide()
        if value:
            if value == 1:
                self.dlg = ErrDialog("Database file missing!\nIt is neccessary\
                   for this application to work.", 2)
            else:
                self.dlg = ErrDialog("Incorrect Database file found!\nPlease\
                    use correct one, provided by creator.", 2)
        else:
            self.dlg = ResDialog(self.response)
            self.dlg.button_control.connect(self.activate_button)
            self.dlg.exec_()
        self.close()

    def algorithm(self, toVisit):
        # full algorithm, we generate non existing paths between cities from real ones using floydWarshall algorithm
        # only lengths, there is no record of what cities were used
        dist_full = self.floydWarshall()
        if dist_full == 0:
            return 0
        # with full 72 x 72 table of distances we cut unnecessary ones and pass that distance table into ants function
        size = len(toVisit)
        dist = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append(0)
            dist.append(row)
        for i in range(size):
            for j in range(i, size):
                dist[i][j] = dist_full[toVisit[i][0] - 1][toVisit[j][0] - 1]
                dist[j][i] = dist_full[toVisit[j][0] - 1][toVisit[i][0] - 1]
        order = self.ants(dist, size)
        self.response = []
        start = order.index(0)
        # prepairing correct order for data that will be displayed
        # (first city that was marked on the list is our first city on the output)
        for i in range(size):
            self.response.append(toVisit[order[(start + i) % size]][1:])
        # emmiting a signal that algorithm has finished it's work
        self.progressSignal.emit(0)

    def floydWarshall(self):
        # floyd warshall algorithm to make up for not existing connections between cities (needed for TSP)
        if path.exists("database.db"):
            con = sqlite3.connect("database.db")
        else:
            self.progressSignal.emit(1)
            return 0
        cur = con.cursor()
        cur.execute('SELECT max(id_to) FROM Distance')
        size = cur.fetchone()[0]
        cur.execute('SELECT * FROM Distance')
        val = cur.fetchall()
        con.close()
        dist = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append(1.0e+200 * (i != j))
            dist.append(row)
        for i in val:
            dist[i[0]-1][i[1]-1] = i[2]
            dist[i[1]-1][i[0]-1] = i[2]
        for k in range(size):
            for i in range(size):
                for j in range(size):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        return dist

    def ants(self, dist, size):
        # ant colony algorithm
        best = self.antsTables(dist, size)
        for trip in range(40):
            self.antAnda(size)
            self.antsTraveling(size, dist)
            min = 1e+200
            index = 0
            for i in range(size):
                if self.ant[i][size] < min:
                    index = i
                    min = self.ant[i][size]
            if best[size] > self.ant[index][size]:
                best = self.ant[index]
            self.pheromones(size)
        return best

    def antsTables(self, dist, size):
        # fucntion for creating necessary tables
        self.tau = []
        self.a = []
        self.p = []
        self.n = []
        best = []
        longest = pd.DataFrame(dist).max().max()
        for i in range(size):
            rowtau = []
            rowa = []
            rown = []
            for j in range(size):
                rowtau.append(1/longest)
                rowa.append(0)
                rown.append(1/dist[i][j] if dist[i][j] != 0 else 0)
            self.tau.append(rowtau)
            self.a.append(rowa)
            self.n.append(rown)
            self.p.append(0)
            best.append(0)
        best.append(1e+200)
        return best

    def antAnda(self, size):
        # creating anew ant table and filling a
        alpha = 1
        beta = 2
        self.ant = []
        self.start = []
        for i in range(size):
            row = []
            for j in range(size):
                self.a[i][j] = (self.tau[i][j] ** alpha) * \
                    (self.n[i][j] ** beta)
                row.append(size + 1)
            row.append(0)
            self.ant.append(row)
            self.start.append(randrange(size))
            s = sum(self.a[i])
            self.a[i] = [val / s for val in self.a[i]]

    def antsTraveling(self, size: int, dist) -> None:
        # function that simulates "travelling" of ants
        for i in range(size):
            self.ant[i][0] = self.start[i]
            for j in range(1, size):
                for q in range(size):
                    self.p[q] = self.a[self.ant[i][j-1]][q] * \
                        (q not in self.ant[i])
                s = sum(self.p)
                self.p = [val / s for val in self.p]
                r = 0
                while r == 0:
                    r = random()
                for q in range(size):
                    r -= self.p[q]
                    if r <= 0:
                        self.ant[i][j] = q
                        self.ant[i][size] += dist[self.ant[i]
                                                  [j - 1]][self.ant[i][j]]
                        break
            self.ant[i][size] += dist[self.ant[i][size-1]][self.ant[i][0]]

    def pheromones(self, size: int) -> None:
        # function for updating pheromones on each arc
        rho = 0.5
        for i in range(size):
            for j in range(size):
                self.tau[i][j] *= (1-rho)
        for i in range(size):
            for j in range(1, size):
                self.tau[self.ant[i][j - 1]][self.ant[i]
                                             [j]] += 1/self.ant[i][size]
                self.tau[self.ant[i][j]][self.ant[i]
                                         [j - 1]] += 1/self.ant[i][size]
            self.tau[self.ant[i][0]][self.ant[i]
                                     [size - 1]] += 1/self.ant[i][size]
            self.tau[self.ant[i][size - 1]][self.ant[i]
                                            [0]] += 1/self.ant[i][size]

    def activate_button(self):
        self.button_control.emit()
