import logging

import cv2
import numpy as np
import plotly.graph_objects as go

from applications.reports.generate.charts.chart_generator import ChartGenerator
from applications.tenants.models import Tenant
from utils.dates import get_hours_duration

logger = logging.getLogger(__name__)


class TheoreticalUseOfVehicleChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.reserved_hours = np.array(self.get_reserved_hours())
        self.free_hours = np.array(self.get_free_hours())
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
        logger.info('TheoreticalUseOfVehicleChart image generated')

    def get_reserved_hours(self):
        hours = []
        for vehicle in self.vehicles:
            hours.append(self.get_reserved_hours_for_vehicle(vehicle))
        return np.array(hours)

    def get_reserved_hours_for_vehicle(self, vehicle):
        # Reservas de un mes, pero incluyendo las que comienzan antes del mes y terminan dentro del mes.
        # Y además, las que comienzan dentro del mes, pero terminan en el mes siguiente.
        # Luego, Excluimos las horas que no están dentro del mes.

        reservations = vehicle.reservations.filter(end__gt=self.first_day, start__lt=self.last_day)
        hours = 0
        for reservation in reservations:
            # Empieza antes del mes y termina dentro del mes.
            if reservation.start < self.first_day:
                hours += get_hours_duration(self.first_day, reservation.end)
            # Empieza detro del mes y termina en el mes siguiente.
            elif reservation.end > self.last_day:
                hours += get_hours_duration(reservation.start, self.last_day)
            # Empieza y termina dentro del mes.
            else:
                hours += get_hours_duration(reservation.start, reservation.end)
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
        return np.array(self.reserved_hours, np.float), np.array(self.free_hours, np.float)
