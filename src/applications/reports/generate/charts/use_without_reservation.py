import logging
import time

import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from applications.reports.generate.charts.chart_generator import ChartGenerator
from applications.tenants.models import Tenant
from applications.traccar.services.api import TraccarAPI

logger = logging.getLogger(__name__)


class UseWithoutReservationChart(ChartGenerator):
    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.hours = self.get_hours()
        df_dict = {'vehicles': self.vehicles_labels, 'hours': self.hours}
        self.df = pd.DataFrame(df_dict)

    def generate_image(self, filename):
        histogram = self.get_histogram()
        fig = make_subplots()
        fig.add_trace(histogram)
        fig.update_layout()
        fig.update_yaxes(title_text='Tiempo (horas)', range=[0, 60])
        fig.write_image(f'{filename}')
        img = cv2.imread(f'{filename}')
        cropped = img[80:-20, :]
        cv2.imwrite(f'{filename}', cropped)
        logger.info('UseWithoutReservationChart image generated')

    def get_hours(self):
        hours = []
        for vehicle in self.vehicles:
            reservations = vehicle.reservations.filter(end__gt=self.first_day, start__lt=self.last_day).reverse()
            if not reservations:
                hours.append(0)
                continue
            first_reservation = reservations.first()
            last_reservation = reservations.last()
            first_day = self.first_day
            last_day = self.last_day

            # Si empieza antes del mes y termina dentro del mes.
            if first_reservation.start < self.first_day:
                first_day = first_reservation.end
                reservations = reservations.exclude(id=first_reservation.id)
            # Si empieza detro del mes y termina en el mes siguiente.
            if last_reservation.end > self.last_day:
                last_day = last_reservation.start
                reservations = reservations.exclude(id=last_reservation.id)

            # Obtener las fechas de comienzo y fin para generar un reporte de viajes fuera de las horas de reserva.
            dates = []
            for index, reservation in enumerate(reservations):
                if index == 0:
                    date = {'from': first_day, 'to': reservation.start}
                elif index == len(reservations) - 1:
                    date = {'from': reservation.end, 'to': last_day}
                else:
                    date = {'from': reservations[index - 1].end, 'to': reservation.start}
                dates.append(date)

            total_duration = 0
            for date in dates:
                time.sleep(0.1)
                trips = TraccarAPI.trips(vehicle.gps_device.id, date['from'], date['to'])
                durations = list(map(lambda trip: trip['duration'], trips))
                total_duration = total_duration + np.sum(np.array(durations))
            duration_into_hours = ((total_duration / (1000 * 60 * 60)) % 24)
            hours.append(duration_into_hours)
        return hours

    def get_histogram(self):
        return go.Bar(
            x=self.df['vehicles'],
            y=self.df['hours'],
            marker=dict(color='#a6bde3'),
        )

    def get_stats(self):
        return np.array(self.df['hours'], np.float)
