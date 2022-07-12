from __init__ import mplb, mplf, Qtw, Qtc


class MplCanvas(mplb.FigureCanvasQTAgg):
    """ class found on https://www.pythonguis.com/tutorials/plotting-matplotlib/
        for showing matplotlib plots in PyQt\n

        Atributes:\n
        fig     -- holds Figure class that can present plots\n
        axes    -- varaible used to access the plot (to plot something on it
        or clear it)\n
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = mplf.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


# following classes are based on the one from
# https://www.pythonguis.com/tutorials/pyqt-dialogs/
class ErrDialog(Qtw.QDialog):
    """ class for displaying dialog window with errors.\n

        Attributes:\n
        button_control  -- pyqt signal for activating button on main window.\n
        Methods:\n
        err_disp        -- displays provided error message and if flag is
        raised closes program with given flag
    """
    def __init__(self, error: str, exit_flag=0):
        super().__init__()
        self.setWindowTitle("Error")
        self.button_control = Qtc.pyqtSignal()
        self.Err_disp(error, exit_flag)
        self.button_control.emit()

    def Err_disp(self, error: str, exit_flag: int) -> None:
        QBtn = Qtw.QDialogButtonBox.Ok

        button_box = Qtw.QDialogButtonBox(QBtn)
        button_box.setCenterButtons(True)
        button_box.accepted.connect(self.accept)

        layout = Qtw.QVBoxLayout()
        message = Qtw.QLabel(error)
        message.setAlignment(Qtc.Qt.AlignCenter)
        layout.addWidget(message)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.exec()
        if (exit_flag):
            quit(exit_flag)


class ResDialog(Qtw.Qdialog):
    """ Class for displaying dialog window with obtained results.\n

        Attributes:\n
        button_control  -- pyqt signal for activating button on main window.\n
        Methods:\n
        res_disp    -- displays result obtained by the program.
    """
    def __init__(self, to_plot):
        super().__init__()
        self.setWindowTitle("Path")
        self.button_control = Qtc.pyqtSignal()
        self.Res_disp(to_plot)
        self.button_control.emit()

    def Res_disp(self, to_plot: list) -> None:
        """ Function that displays results obtained by program, both on a plot
            and a order of cities to visit.\n
            takes list of tuples as a parameter as it should contain the
            result.
        """
        QBtn = Qtw.QDialogButtonBox.Ok

        button_box = Qtw.QDialogButtonBox(QBtn)
        button_box.setCenterButtons(True)
        button_box.accepted.connect(self.accept)

        layout = Qtw.QVBoxLayout()

        names, mapres = self.Prep_names_and_plot(to_plot)
        layout.addWidget(mapres)
        message = Qtw.QLabel(names)
        message.setAlignment(Qtc.Qt.AlignCenter)
        layout.addWidget(message)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.exec()

    def Prep_names_and_plot(self, to_plot: list) -> tuple[str, MplCanvas]:
        """ Function to prepaire the data that will be displayed by Res_disp.\n
            Takes list as parameter and based on it it creates a plot
            and a string that represents the result.
        """
        mapres = MplCanvas(self)
        x = []
        y = []
        names = ""
        for i in range(len(to_plot)):
            x.append(to_plot[i][2])
            y.append(to_plot[i][1])
            mapres.axes.text(x[i], y[i], i + 1)
            names += (to_plot[i][0] + " (" + str(i + 1) + ") -> ")
            if (i + 1) % 6 == 0:
                names += "\n"
        names += to_plot[0][0] + " (1)"
        mapres.axes.plot(x, y, marker='o', color='r')
        mapres.axes.plot(x, y, color='b')
        mapres.axes.plot([x[0], x[len(to_plot) - 1]], [y[0],
                         y[len(to_plot) - 1]], color='b')
        return names, mapres
