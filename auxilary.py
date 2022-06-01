from __init__ import *

class MplCanvas(mplb.FigureCanvasQTAgg):
    # class found on https://www.pythonguis.com/tutorials/plotting-matplotlib/ for showing matplotlib plots in PyQt
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = mplf.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Dialog(QDialog):
    # class taken from https://www.pythonguis.com/tutorials/pyqt-dialogs/
    def __init__(self, err, button, selected = [], error = ""):
        super().__init__()
        self.setWindowTitle("Error")

        # check which dialog we want to present
        if err == 1:
            self.error(button)
        elif err == 0:
            self.results(selected)
        elif err == 2:
            self.dberror(error)
        button[0].setText("Find Path")
        button[0].setEnabled(True)
        
    def error(self):
        # dialog when user choose less than 2 cities
        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.setCenterButtons(True)
        buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        message = QLabel("Please select at least two cities!")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.exec()

    def results(self, toPlot):
        # dialog with results of a path finding algorithm properly presented
        self.setWindowTitle("Path")
        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.setCenterButtons(True)
        buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        
        names, mapres = self.prepNamesAndPlot(toPlot)
        layout.addWidget(mapres)
        message = QLabel(names)
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.exec()

    def prepNamesAndPlot(self, toPlot):
        # function that prepairs names data to be outputed and plots lat lon data
        mapres = MplCanvas(self, width=5, height=4, dpi=100)
        x = []
        y = []
        names = ""
        for i in range(len(toPlot)):
            x.append(toPlot[i][2])
            y.append(toPlot[i][1])
            mapres.axes.text(x[i], y[i], i + 1)
            names += (toPlot[i][0] + " (" + str(i + 1) + ") -> ")
            if (i + 1) % 6 == 0:
                names += "\n"
        names += toPlot[0][0] + " (1)"
        mapres.axes.plot(x, y, marker = 'o', color = 'r')
        mapres.axes.plot(x, y, color = 'b')
        mapres.axes.plot([x[0], x[len(toPlot) - 1]], [y[0], y[len(toPlot) - 1]], color = 'b')
        return names, mapres

    def dberror(self, error):
        # dialog when database file is missing
        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.setCenterButtons(True)
        buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        message = QLabel(error)
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.exec()
        quit(2)
