import logging

import numpy as np
import plotly.graph_objects as go

from applications.reports.services.pdf.charts.chart_generator import ChartGenerator
from applications.reports.services.pdf.charts.use_of_vehicles.theoretical_use_of_vehicle import TheoreticalUseOfVehicleChart
from applications.reports.services.pdf.charts.vehicle_punctuality import PunctualityChart
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.tenants.models import Tenant

logger = logging.getLogger(__name__)


class RealUseOfVehicleChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int,
                 theoretical_chart: TheoreticalUseOfVehicleChart, punctuality_chart: PunctualityChart,
                 hour_config: HoursChartConfiguration = None,
                 by: str = 'vehicle',
                 n_values: int = 25,
                 orientation: str = 'h'):
        super().__init__(tenant, month, year, hour_config, by, n_values, orientation)
        self.punctuality_chart = punctuality_chart
        self.theoretical_chart = theoretical_chart
        self.reserved_hours = self.get_reserved_hours()
        self.free_hours = self.get_free_hours()
        self.reserved_hours_percentages = self.serialize_to_percentages(self.reserved_hours)
        self.free_hours_percentages = self.serialize_to_percentages(self.free_hours)

    def generate_image(self, filename, start, end, i):
        reserved_bar = self.get_reserved_hours_bar(start, end)
        free_bar = self.get_free_hours_bar(start, end)
        fig = go.Figure(data=[reserved_bar, free_bar])
        self.update_axes(fig)
        fig.update_layout(barmode='stack')
        fig.update_layout(plot_bgcolor='rgb(255,255,255)')
        fig.write_image(f'{filename}{i}.png')
        self.remove_image_header(f'{filename}{i}.png')
        self.images.append(f'{filename}{i}.png')
        logger.info('RealUseOfVehicleChart image generated')

    def update_axes(self, fig):
        if self.orientation == 'h':
            fig.update_xaxes(showgrid=False)
            fig.update_xaxes(title_text='Tiempo (horas)')
        else:
            fig.update_yaxes(showgrid=False)
            fig.update_yaxes(title_text='Tiempo (horas)')

    def get_reserved_hours(self):
        reserved_hours, _ = self.theoretical_chart.get_stats()
        takes_out, takes_in, not_taken, frees_out, frees_in = self.punctuality_chart.get_stats()
        hours = reserved_hours - (takes_out + takes_in + not_taken + frees_out + frees_in)
        return hours

    def get_free_hours(self):
        free_hours = np.array(self.WORK_HOURS_PER_MONTH - self.reserved_hours)
        return free_hours

    def serialize_to_percentages(self, hours):
        percentages = np.around(hours / self.WORK_HOURS_PER_MONTH * 100, decimals=2)
        percentages = np.array([f'{percentage} %' for percentage in percentages])
        return percentages

    def get_reserved_hours_bar(self, start, end):
        x, y = self.get_xy(self.reserved_hours)
        return go.Bar(
            name='Tiempo reservado',
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='#a6bde3'),
            textposition='auto',
            text=self.reserved_hours_percentages[start:end],
            orientation=self.orientation
        )

    def get_free_hours_bar(self, start, end):
        x, y = self.get_xy(self.free_hours)
        return go.Bar(
            name='Tiempo disponible',
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='white'),
            textposition='auto',
            text=self.free_hours_percentages[start:end],
            orientation=self.orientation
        )

    def get_stats(self):
        return np.array(self.reserved_hours, float), \
               np.array(self.free_hours, float)
