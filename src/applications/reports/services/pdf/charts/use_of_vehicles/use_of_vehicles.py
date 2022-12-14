import logging

import numpy as np
import plotly.graph_objects as go

from applications.reports.services.pdf.charts.chart_generator import ChartGenerator
from applications.reports.services.pdf.charts.use_of_vehicles.real_use_of_vehicle import RealUseOfVehicleChart
from applications.reports.services.pdf.charts.use_of_vehicles.theoretical_use_of_vehicle import \
    TheoreticalUseOfVehicleChart
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.reports.services.pdf.utils.hours_calculator import HoursCalculator
from applications.tenants.models import Tenant
from utils.dates import from_date_to_utc

logger = logging.getLogger(__name__)


class UseOfVehicleChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int,
                 theoretical: TheoreticalUseOfVehicleChart, real: RealUseOfVehicleChart,
                 hour_config: HoursChartConfiguration = None,
                 by: str = 'vehicle',
                 n_values: int = 25,
                 orientation: str = 'h'):
        super().__init__(tenant, month, year, hour_config, by, n_values, orientation)
        self.theoretical = theoretical
        self.real = real
        self.movement = self.get_movement_hours()
        self.movement_percentages = self.serialize_to_percentages(self.movement)
        self.bars = self.get_bars()
        self.labels = self.mark_labels_which_exceed_end_hours()

    def generate_image(self, filename, start, end, i):
        theoretical_bar = self.get_reserved_theoretical_hours_bar(start, end)
        real_bar = self.get_reserved_real_hours_bar(start, end)
        free_bar = self.get_free_hours_bar(start, end)
        movement_bar = self.get_movement_hours_bar(start, end)
        fig = go.Figure(data=[movement_bar, real_bar, theoretical_bar, free_bar])
        fig.update_traces(textposition='inside', textfont_size=12, textfont_color='black')
        self.update_axes(fig)
        fig.update_layout(barmode='stack')
        fig.update_layout(plot_bgcolor='rgb(255,255,255)')
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
        fig.update_layout(legend=dict(xanchor="center", x=0.45, yanchor="bottom", y=-0.12))
        fig.write_image(f'{filename}{i}.png', width=900, height=1350)
        self.remove_image_header(f'{filename}{i}.png', bottom=-1)
        self.images.append(f'{filename}{i}.png')
        logger.info('UseOfVehicleChart image generated')

    def update_axes(self, fig):
        if self.orientation == 'h':
            fig.update_xaxes(showgrid=False)
            fig.update_xaxes(title_text='Tiempo (horas)')
        else:
            fig.update_yaxes(showgrid=False)
            fig.update_yaxes(title_text='Tiempo (horas)')

    def get_movement_hours(self):
        hours = []
        objs = self.filter_by.get_data()
        for obj in objs:
            hours.append(self.get_movement_hours_by(obj))
        return np.array(hours)

    def get_movement_hours_by(self, obj):
        reservations = self.filter_by.filter(self.all_reservations, obj)
        hours = 0
        for reservation in reservations:
            hours += HoursCalculator.get_movement_hours(reservation)
        return hours

    def get_bars(self):
        theoretical_hours = self.theoretical.get_stats()[0]
        real_bar = self.real.get_stats()[0]
        theoretical_bar = theoretical_hours - real_bar
        real_bar = real_bar - self.movement
        free_bar = np.array(self.WORK_HOURS_PER_MONTH - theoretical_bar - real_bar - self.movement)
        return {'theoretical_bar': theoretical_bar, 'real_bar': real_bar,
                'free_bar': free_bar, 'movement_bar': self.movement}

    def serialize_to_percentages(self, hours):
        percentages = np.around(hours / self.WORK_HOURS_PER_MONTH * 100, decimals=2)
        percentages = np.array([f'{percentage} %' for percentage in percentages])
        return percentages

    def mark_labels_which_exceed_end_hours(self):
        labels = self.labels
        mark = '*'
        objs = self.filter_by.get_data()
        for i, obj in enumerate(objs):
            reservations = self.filter_by.filter(self.all_reservations, obj)
            reservation = reservations.order_by('end').last()
            if reservation and self.config:
                end = reservation.end
                limit = from_date_to_utc(end.year, end.month, end.day, self.config.end_hour)
                if end.time() > limit.time():
                    labels[i] += mark
        return labels

    def get_reserved_theoretical_hours_bar(self, start, end):
        x, y = self.get_xy(self.bars['theoretical_bar'])
        return go.Bar(
            name='Tiempo reservado',
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='#a6bde3'),
            text=self.theoretical.reserved_hours_percentages[start:end],
            orientation=self.orientation
        )

    def get_reserved_real_hours_bar(self, start, end):
        x, y = self.get_xy(self.bars['real_bar'])
        return go.Bar(
            name='Tiempo ocupado',
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='#4280E3'),
            text=self.real.reserved_hours_percentages[start:end],
            orientation=self.orientation
        )

    def get_free_hours_bar(self, start, end):
        x, y = self.get_xy(self.bars['free_bar'])
        return go.Bar(
            name='Tiempo disponible',
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='white'),
            text=self.theoretical.free_hours_percentages[start:end],
            orientation=self.orientation
        )

    def get_movement_hours_bar(self, start, end):
        x, y = self.get_xy(self.bars['movement_bar'])
        return go.Bar(
            name='Tiempo en movimiento',
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='red'),
            text=self.movement_percentages[start:end],
            orientation=self.orientation
        )
