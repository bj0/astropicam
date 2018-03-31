from collections import deque

from kivy.garden.graph import Graph, MeshLinePlot
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex as rgb


class PlotScreen(Screen):
    current = StringProperty("0")

    values = deque([0] * 100)

    _P = 1.0

    def init(self):
        # use kivy garden's graph widget
        graph = Graph(xlabel='t', ylabel='HFR', x_ticks_minor=5, x_ticks_major=10,
                      y_ticks_minor=1, y_ticks_major=5, y_grid_label=True,
                      x_grid_label=False, padding=0, y_grid=False, x_grid=False,
                      xmin=0, ymin=0, xmax=100, ymax=30,
                      _with_stencilbuffer=False,  # or it does not work in ScreenManager
                      label_options={'color': rgb('808080')})
        y = (float(i) for i in range(50))
        x = (float(i) for i in range(50))
        plot = MeshLinePlot(color=rgb('1100aa'))
        pts = list(zip(x, y))
        plot.points = pts
        graph.add_plot(plot)

        self.ids.plot.add_widget(graph)

        self.plot = plot
        self.graph = graph

    def update_plot(self, values):
        self.plot.points = zip(range(len(values)), values)

        self.graph.ymax = int(max(values) + 5)
        self.graph.ymin = int(min(values) - 5)

    def update_measure(self, _, fm):
        # use 1-d kalman filter
        xh = self.values[-1]
        k = self._P / (self._P + 0.5)
        fme = xh + k * (fm - xh)
        self._P = (1 - k) * self._P

        self.values.popleft()
        self.values.append(fme)

        print('new measure: {},{},{}'.format(fm, fme, self._P))
        self.update_plot(self.values)
        self.current = "{}".format(int(fme))
