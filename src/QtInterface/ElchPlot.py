from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.font_manager as fm
import matplotlib.ticker
from matplotlib.figure import Figure
import matplotlib.style
import matplotlib.pyplot as plt
import numpy as np
import pubsub.pub
import matplotlib.font_manager as font_manager


class ElchPlot(FigureCanvasQTAgg):
    def __init__(self):
        font_dir = ['src/Fonts']
        for font in font_manager.findSystemFonts(font_dir):
            font_manager.fontManager.addfont(font)
        matplotlib.style.use('QtInterface/App.mplstyle')
        super().__init__(Figure(figsize=(8, 6)))

        self.axes = self.figure.subplots()
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Pressure (mbar)')

        self.colors = {1: '#9686f8', 2: '#f488f9', 3: '#86f9de'}
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
            pubsub.pub.subscribe(self.add_data_point, 'engine.answer.pressure')
        else:
            pubsub.pub.unsubscribe(self.add_data_point, 'engine.answer.pressure')

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
