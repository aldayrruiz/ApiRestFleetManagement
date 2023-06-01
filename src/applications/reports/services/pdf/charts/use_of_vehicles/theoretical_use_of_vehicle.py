import logging

import numpy as np
import plotly.graph_objects as go

from applications.reports.services.pdf.charts.chart_generator import ChartGenerator
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.reports.services.pdf.utils.hours_calculator import HoursCalculator
from applications.tenants.models import Tenant

logger = logging.getLogger(__name__)


class TheoreticalUseOfVehicleChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int, hour_config: HoursChartConfiguration = None,
                 by: str = 'vehicle',
                 n_values: int = 25,
                 orientation: str = 'h'):
        super().__init__(tenant, month, year, hour_config, by, n_values, orientation)
        self.reserved_hours = np.array(self.get_reserved_hours())
        self.free_hours = np.array(self.get_free_hours())
        self.reserved_hours_percentages = self.serialize_to_percentages(self.reserved_hours)
        self.free_hours_percentages = self.serialize_to_percentages(self.free_hours)

    def generate_image(self, filename, start, end, i):
        reserved_bar = self.get_reserved_hours_bar(start, end)
        free_bar = self.get_free_hours_bar(start, end)
        fig = go.Figure(data=[reserved_bar, free_bar])
        fig.update_layout(barmode='stack')
        fig.update_layout(plot_bgcolor='rgb(255,255,255)')
        fig.write_image(f'{filename}', width=700, height=800)
        self.remove_image_header(filename)
        logger.info('TheoreticalUseOfVehicleChart image generated')

    def update_axes(self, fig):
        if self.orientation == 'h':
            fig.update_xaxes(showgrid=False)
            fig.update_xaxes(title_text='Tiempo (horas)')
        else:
            fig.update_yaxes(showgrid=False)
            fig.update_yaxes(title_text='Tiempo (horas)')


    def get_reserved_hours(self):
        hours = []
        objs = self.filter_by.get_data()
        for obj in objs:
            hours.append(self.get_reserved_hours_by(obj))
        return np.array(hours)

    def get_reserved_hours_by(self, obj):
        # Reservas de un mes, pero incluyendo las que comienzan antes del mes y terminan dentro del mes.
        # Y además, las que comienzan dentro del mes, pero terminan en el mes siguiente.
        # Luego, Excluimos las horas que no están dentro del mes.

        reservations = self.filter_by.filter(self.all_reservations, obj)
        hours = 0
        for reservation in reservations:
            hours += HoursCalculator.get_theoretical_hours_reservation(reservation, self.first_day, self.last_day)
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
        return np.array(self.reserved_hours, float), np.array(self.free_hours, float)
