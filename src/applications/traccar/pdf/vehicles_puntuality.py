import os
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Vehicles
from applications.tenants.models import Tenant
from applications.traccar.pdf.chart_generator import ChartGenerator

vehicles = np.array(['1234 Clio', '4312 Zoe', '2314 Zoe', '5413 Traffic', '5312 Scenic'])


class VehiclePuntuality(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.takes = np.array([1.4, 0.5, 2.3, 1.2, 2.2])
        self.frees = np.array([2.5, 3.5, 3.3, 3.2, 1.7])

    def generate_image(self, filename):
        fig = make_subplots()
        takes_scatter = self.get_takes_scatter()
        frees_scatter = self.get_frees_scatter()
        traces = [takes_scatter, frees_scatter]
        fig.add_traces(traces)
        fig.update_layout(title_text=f'Puntualidad por vehículo {self.month_title}')
        fig.update_yaxes(title_text='Horas')
        fig.write_image(f'images/{filename}')
        fig.show()

    def get_takes_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.takes,
                          name='Recoger',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='blue'))

    def get_frees_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.frees,
                          name='Liberar',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='orange'))


