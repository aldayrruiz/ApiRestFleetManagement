import logging

import cv2
import numpy as np
import plotly.graph_objects as go

from applications.reports.generate.charts.chart_generator import ChartGenerator
from applications.reports.generate.charts.theoretical_use_of_vehicle import TheoreticalUseOfVehicleChart
from applications.reports.generate.charts.vehicle_punctuality import PunctualityChart
from applications.tenants.models import Tenant

logger = logging.getLogger(__name__)


class RealUseOfVehicleChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int,
                 hours_taken_chart: TheoreticalUseOfVehicleChart, punctuality_chart: PunctualityChart):
        super().__init__(tenant, month, year)
        self.punctuality_chart = punctuality_chart
        self.hours_taken_chart = hours_taken_chart
        self.reserved_hours = self.get_reserved_hours()
        self.free_hours = self.get_free_hours()
        self.reserved_hours_percentages = self.serialize_to_percentages(self.reserved_hours)
        self.free_hours_percentages = self.serialize_to_percentages(self.free_hours)

    def generate_image(self, filename):
        reserved_bar = self.get_reserved_hours_bar()
        free_bar = self.get_free_hours_bar()
        fig = go.Figure(data=[reserved_bar, free_bar])
        fig.update_yaxes(showgrid=False)
        fig.update_yaxes(title_text='Tiempo (horas)')
        fig.update_layout(barmode='stack')
        fig.write_image(f'{filename}', width=700, height=800)
        img = cv2.imread(f'{filename}')
        cropped = img[80:-20, :]
        cv2.imwrite(f'{filename}', cropped)
        logger.info('RealUseOfVehicleChart image generated')

    def get_reserved_hours(self):
        reserved_hours, _ = self.hours_taken_chart.get_stats()
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

    def get_reserved_hours_bar(self):
        return go.Bar(
            name='Tiempo reservado',
            x=self.vehicles_labels,
            y=self.reserved_hours,
            marker=dict(color='#a6bde3'),
            textposition='auto',
            text=self.reserved_hours_percentages
        )

    def get_free_hours_bar(self):
        return go.Bar(
            name='Tiempo disponible',
            x=self.vehicles_labels,
            y=self.free_hours,
            marker=dict(color='white'),
            textposition='auto',
            text=self.free_hours_percentages
        )

    def get_stats(self):
        return np.array(self.reserved_hours, np.float), \
               np.array(self.free_hours, np.float)
