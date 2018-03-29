from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex as rgb


class PlotScreen(Screen):
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
