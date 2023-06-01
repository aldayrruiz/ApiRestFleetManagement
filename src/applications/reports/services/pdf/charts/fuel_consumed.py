import logging

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from applications.reports.services.pdf.charts.chart_generator import ChartGenerator
from applications.reports.services.pdf.charts.distance_max_average_speed import DistanceMaxAverageSpeedChart
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.tenants.models import Tenant
from applications.vehicles.models import Fuel

logger = logging.getLogger(__name__)


class FuelConsumedChart(ChartGenerator):
    def __init__(self, tenant: Tenant, month: int, year: int, chart: DistanceMaxAverageSpeedChart,
                 hour_config: HoursChartConfiguration = None,
                 by: str = 'vehicle',
                 n__values: int = 25,
                 orientation: str = 'h'):
        super().__init__(tenant, month, year, hour_config, by, n__values, orientation)
        self.chart = chart
        self.fuels = self.get_fuels()

    def generate_image(self, filename, start, end, i):
        histogram = self.get_histogram(start, end)
        fig = make_subplots()
        fig.add_trace(histogram)
        fig.update_layout(plot_bgcolor='rgb(255,255,255)')
        self.update_axes(fig)
        fig.write_image(f'{filename}{i}.png')
        self.remove_image_header(f'{filename}{i}.png')
        self.images.append(f'{filename}{i}.png')
        logger.info('FuelConsumedChart image generated')

    def update_axes(self, fig):
        if self.orientation == 'h':
            fig.update_xaxes(title_text='Combustible consumido (€)')
        else:
            fig.update_yaxes(title_text='Combustible consumido (€)')
        fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
        fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

    def get_fuels(self):
        fuels = []
        distances = self.chart.get_stats()[0]
        # diesel: 1,8 euros/litro y 8 litros/100km
        # eléctrico: 0,55 euros/kWh y 18kWh/100km
        # gasolina: 1,7 euros/litro y 6 litros/100km
        for i, vehicle in enumerate(self.vehicles):
            fuels.append(self.calculate_fuel_consumed(vehicle, distances[i]))
        return fuels

    def get_consumed_in_euros(self):
        result = [f'{fuel:.2f} €' for fuel in self.fuels]
        return result

    @staticmethod
    def calculate_fuel_consumed(vehicle, distance):
        if vehicle.fuel == Fuel.DIESEL:
            fuel = (distance * 1.8 * 8) / 100
        elif vehicle.fuel == Fuel.ELECTRIC:
            fuel = (distance * 0.25 * 18) / 100
        else:
            fuel = (distance * 1.7 * 6) / 100
        return fuel

    def get_histogram(self, start, end):
        x, y = self.get_xy(self.fuels)
        text = self.get_consumed_in_euros()
        return go.Bar(
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='#0353A4'),
            orientation=self.orientation,
            text=text[start:end],
        )

    def get_stats(self):
        return np.array(self.fuels, float)
