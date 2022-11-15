from __init__ import mplb, mplf, Qtw, Qtc


class MplCanvas(mplb.FigureCanvasQTAgg):
    """ Class found on https://www.pythonguis.com/tutorials/plotting-matplotlib/
        for showing matplotlib plots in PyQt\n

        Atributes:\n
        fig     -- holds Figure class that can present plots\n
        axes    -- varaible used to access the plot (to plot something on it
        or clear it)\n
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """ Setup for a single plot figure, equivalent to matlab's figure()
        """
        self.fig = mplf.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


# following classes are based on the one from
# https://www.pythonguis.com/tutorials/pyqt-dialogs/
class ErrDialog(Qtw.QDialog):
    """ Flass for displaying dialog window with errors.\n

        Attributes:\n
        button_control  -- pyqt signal for activating button on main window.\n
        Methods:\n
        err_disp        -- displays provided error message and if flag is
        raised closes program with given flag
    """
    button_control = Qtc.pyqtSignal()

    def __init__(self, error: str, exit_flag=0):
        """ Sets up the error dialog window, takes in error string and
            exit code as parameters.
        """
        super().__init__()
        self.setWindowFlags(Qtc.Qt.WindowTitleHint)
        self._exit_flag = exit_flag
        self.setWindowTitle("Error")
        self.err_disp(error)

    def err_disp(self, error: str) -> None:
        """ Function to display desired error message in the dialog.\n
            Takes error string and exit flag as parameters. Presents the
            message and if flag is other then zero terminates program.
        """
        message = Qtw.QLabel(error)
        message.setAlignment(Qtc.Qt.AlignCenter)

        button = Qtw.QPushButton(text="OK")
        button.setMaximumWidth(75)
        button.pressed.connect(self.finish)

        h_box = Qtw.QHBoxLayout()
        h_box.addWidget(button)
        h_box.setAlignment(Qtc.Qt.AlignCenter)

        layout = Qtw.QVBoxLayout()
        layout.addWidget(message)
        layout.addLayout(h_box)
        self.setLayout(layout)

    def finish(self):
        """ Function called when users clicks a button."""
        self.button_control.emit()
        if (self._exit_flag):
            quit(self._exit_flag)
        self.accept()


class ResDialog(Qtw.QDialog):
    """ Class for displaying dialog window with obtained results.\n

        Attributes:\n
        button_control  -- pyqt signal for activating button on main window.\n
        Methods:\n
        res_disp    -- displays result obtained by the program.
    """
    button_control = Qtc.pyqtSignal()

    def __init__(self, to_plot):
        """ Sets up the dialog window with the results, takes
        """
        super().__init__()
        self.setWindowFlags(Qtc.Qt.WindowTitleHint)
        self.setWindowTitle("Path")
        self.res_disp(to_plot)

    def res_disp(self, to_plot: list) -> None:
        """ Function that displays results obtained by program, both on a plot
            and a order of cities to visit.\n
            takes list of tuples as a parameter as it should contain the
            result.
        """
        names, mapres = self.Prep_names_and_plot(to_plot)

        message = Qtw.QLabel(names)
        message.setAlignment(Qtc.Qt.AlignCenter)

        btn = Qtw.QPushButton(text="OK")
        btn.pressed.connect(self.finish)

        button_box = Qtw.QHBoxLayout()
        button_box.addWidget(btn)
        button_box.setAlignment(Qtc.Qt.AlignCenter)

        layout = Qtw.QVBoxLayout()
        layout.addWidget(mapres)
        layout.addWidget(message)
        layout.addLayout(button_box)
        self.setLayout(layout)

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

    def finish(self):
        self.button_control.emit()
        self.accept()
