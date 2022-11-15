from __init__ import Qtw, Qtc, random
from auxilary import ErrDialog, ResDialog
from threading import Thread
import pandas as pd
from numpy import full, Inf, fill_diagonal, ndarray, random, power
from decorators import data_check
from db_connection import db


class solveWindow(Qtw.QWidget):
    # class for solving real TSP problem with cities given by user
    progress_signal = Qtc.pyqtSignal()
    error_signal = Qtc.pyqtSignal(int)
    button_control = Qtc.pyqtSignal()

    def __init__(self, db: db, to_visit: list):
        """ Sets up solution class and some result presentation.
        """
        super().__init__()
        self.setWindowFlags(Qtc.Qt.WindowTitleHint)
        self.setWindowTitle("Working...")
        self.to_visit = to_visit
        self.db = db
        self.progress_signal.connect(self.results)
        self.layout = Qtw.QVBoxLayout()
        self.message = Qtw.QLabel("Calculating Shortest path\nPlease wait...")
        self.message.setAlignment(Qtc.Qt.AlignCenter)
        self.layout.addWidget(self.message)
        self.setLayout(self.layout)
        self.show()
        t = Thread(target=lambda: self.algorithm())
        t.start()

    def results(self) -> None:
        # function for displaying dialog with results
        self.hide()
        self.dlg = ResDialog(self.response)
        self.dlg.button_control.connect(self.activate_button)
        self.dlg.exec_()
        self.close()

    def algorithm(self) -> None:
        # full algorithm, we generate non existing paths between cities from real ones using floydWarshall algorithm
        # only lengths, there is no record of what cities were used
        dist_full = self.floyd_warshall()
        if type(dist_full) != ndarray:
            return
        # with full 72 x 72 table of distances we cut unnecessary ones and pass that distance table into ants function
        self.size = len(self.to_visit)
        ids = [x[0] - 1 for x in self.to_visit]
        self.dist = dist_full[ids][:, ids]
        order = self.ants()
        start = list(order).index(0)
        # prepairing correct order for data that will be displayed
        # (first city that was marked on the list is our first city on the output)
        self.response = [
            self.to_visit[order[(start + i) % self.size]][1:] for i in range(self.size)]
        # emmiting a signal that algorithm has finished it's work
        self.progress_signal.emit()

    @data_check
    def floyd_warshall(self):
        # floyd warshall algorithm to make up for not existing connections between cities (needed for TSP)
        size = self.db.querry('SELECT max(id_to) FROM Distance')[0][0]
        val = self.db.querry('SELECT * FROM Distance')
        dist = full((size, size), Inf)
        fill_diagonal(dist, 0)
        for i in val:
            dist[i[0]-1][i[1]-1] = i[2]
            dist[i[1]-1][i[0]-1] = i[2]
        for k in range(size):
            for i in range(size):
                for j in range(size):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        if (dist == Inf).any():
            raise RuntimeError
        else:
            return dist

    def ants(self):
        # ant colony algorithm
        best = self.antsTables()
        for trip in range(40):
            self.antAnda()
            self.antsTraveling()
            min = Inf
            index = 0
            for i in range(self.size):
                if self.ant[i][self.size] < min:
                    index = i
                    min = self.ant[i][self.size]
            if best[self.size] > self.ant[index][self.size]:
                best = self.ant[index]
            self.pheromones()
        return best

    def antsTables(self):
        # fucntion for creating necessary tables
        self.tau = full((self.size, self.size), 1/self.dist.max())
        self.a = full((self.size, self.size), 0.0)
        self.n = 1/self.dist
        fill_diagonal(self.n, 0)
        best = full(self.size + 1, 0.0)
        best[self.size] = Inf
        return best

    def antAnda(self):
        # creating anew ant table and filling a
        alpha = 1
        beta = 2
        self.ant = full((self.size, self.size + 1), self.size + 1)
        self.ant[:, self.size] = 0
        self.a = power(self.tau, alpha) * power(self.n, beta)
        self.start = random.randint(0, self.size, self.size)
        self.a = [val / sum(val) for val in self.a]

    def antsTraveling(self) -> None:
        # function that simulates "travelling" of ants
        self.ant[:, 0] = self.start
        for i in range(self.size):
            for j in range(1, self.size):
                self.p = [self.a[self.ant[i, j-1]][q] *
                          (q not in self.ant[i]) for q in range(self.size)]
                self.p = [val / sum(self.p) for val in self.p]
                r = 0
                while r == 0:
                    r = random.rand(1)
                for q in range(self.size):
                    r -= self.p[q]
                    if r <= 0:
                        self.ant[i][j] = q
                        self.ant[i][self.size] += self.dist[self.ant[i]
                                                            [j - 1]][self.ant[i][j]]
                        break
            self.ant[i][self.size] += self.dist[self.ant[i]
                                                [self.size-1]][self.ant[i][0]]

    def pheromones(self) -> None:
        # function for updating pheromones on each arc
        rho = 0.5
        self.tau *= (1-rho)
        for i in range(self.size):
            for j in range(1, self.size):
                self.tau[self.ant[i][j - 1]][self.ant[i]
                                             [j]] += 1/self.ant[i][self.size]
                self.tau[self.ant[i][j]][self.ant[i]
                                         [j - 1]] += 1/self.ant[i][self.size]
            self.tau[self.ant[i][0]][self.ant[i]
                                     [self.size - 1]] += 1/self.ant[i][self.size]
            self.tau[self.ant[i][self.size - 1]][self.ant[i]
                                                 [0]] += 1/self.ant[i][self.size]

    def activate_button(self):
        self.button_control.emit()
