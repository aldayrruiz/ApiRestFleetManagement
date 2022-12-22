import logging
import time

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from applications.reports.services.pdf.charts.chart_generator import ChartGenerator
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.tenants.models import Tenant
from applications.traccar.services.api import TraccarAPI

logger = logging.getLogger(__name__)


class UseWithoutReservationChart(ChartGenerator):
    def __init__(self, tenant: Tenant, month: int, year: int, hour_config: HoursChartConfiguration = None,
                 by: str = 'vehicle',
                 n_values: int = 25,
                 orientation: str = 'h'):
        super().__init__(tenant, month, year, hour_config, by, n_values, orientation)
        self.hours = self.get_hours()

    def generate_image(self, filename, start, end, i):
        histogram = self.get_histogram(start, end)
        fig = make_subplots()
        fig.add_trace(histogram)
        fig.update_layout(plot_bgcolor='rgb(255,255,255)')
        fig.update_yaxes(title_text='Tiempo (horas)')
        self.update_axes(fig)
        fig.write_image(f'{filename}{i}.png')
        self.remove_image_header(f'{filename}{i}.png')
        self.images.append(f'{filename}{i}.png')
        logger.info('UseWithoutReservationChart image generated')

    def update_axes(self, fig):
        if self.orientation == 'h':
            fig.update_xaxes(title_text='Tiempo (horas)')
        else:
            fig.update_yaxes(title_text='Tiempo (horas)')

    def get_hours(self):
        hours = []
        for vehicle in self.vehicles:
            reservations = self.all_reservations.filter(vehicle=vehicle)
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

    def get_text_hours(self):
        return list(map(lambda hour: f'{hour:.2f}h', self.hours))

    def get_histogram(self, start, end):
        x, y = self.get_xy(self.hours)
        text = self.get_text_hours()
        return go.Bar(
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='#023E7D'),
            text=text[start:end],
            orientation=self.orientation,
        )

    def get_stats(self):
        return np.array(self.hours, np.float)
