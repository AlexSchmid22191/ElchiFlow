import matplotlib.font_manager as fm
import matplotlib.style
import matplotlib.ticker
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src.Signals import signals_engine

# TODO: Add zoom functionality


class ElchPlot(FigureCanvasQTAgg):
    def __init__(self):
        matplotlib.style.use('QtInterface/App.mplstyle')
        super().__init__(Figure(figsize=(8, 6)))

        self.axes = self.figure.subplots()
        self.axes.set_xlabel('Time (s)', fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=14))
        self.axes.set_ylabel('Pressure (mbar)',
                             fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=14))

        self.axes.set_xticks(range(11))
        self.axes.set_yticks(range(11))
        self.axes.set_xticklabels(range(11), fontproperties=fm.FontProperties(fname='Fonts/Roboto-Light.ttf', size=11))
        self.axes.set_yticklabels(range(11), fontproperties=fm.FontProperties(fname='Fonts/Roboto-Light.ttf', size=11))
        self.axes.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())
        self.axes.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())
        self.axes.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        self.axes.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        self.colors = {1: '#f488f9', 2: '#86f8ab', 3: '#faf0b1'}
        self.plots = {key: self.axes.plot([], color=self.colors[key], marker='')[0] for key in range(1, 4)}

        self.figure.tight_layout()

    def add_data_point(self, channel, pressure, runtime):
        self.plots[channel].set_data(np.append(self.plots[channel].get_xdata(), runtime),
                                     np.append(self.plots[channel].get_ydata(), pressure))

        self.axes.relim()
        self.axes.autoscale()
        self.figure.canvas.draw()
        self.figure.tight_layout()

    def set_plot_visibility(self, plot, visible):
        self.plots[int(plot.objectName())].set_linestyle('-' if visible else '')

    def start_plotting(self, plotting):
        if plotting:
            signals_engine.pressure.connect(self.add_data_point)
        else:
            signals_engine.pressure.disconnect(self.add_data_point)

    def clear_plot(self):
        for plot in self.plots.values():
            plot.set_data([], [])
        self.figure.canvas.draw()

    def switch_scale(self, state):
        if state:
            self.axes.set_yscale('log')
        else:
            self.axes.set_yscale('linear')
        self.axes.relim()
        self.axes.autoscale()
        self.figure.canvas.draw()
        self.figure.tight_layout()
