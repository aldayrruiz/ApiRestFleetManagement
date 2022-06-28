import logging
import math
import time

import cv2
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from applications.reports.generate.charts.chart_generator import ChartGenerator
from applications.tenants.models import Tenant
from applications.traccar.utils import report_units_converter
from applications.traccar.services.api import TraccarAPI

logger = logging.getLogger(__name__)


class DistanceMaxAverageSpeedChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.distances, self.max_speeds, self.average_speeds = self.get_reports()

    def generate_image(self, filename):
        bar = self.get_distance_bar()
        scatter1 = self.get_max_speed_scatter()
        scatter2 = self.get_average_speed_scatter()
        traces = [bar, scatter1, scatter2]
        secondary_ys = [False, True, True]
        fig = make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_traces(traces, secondary_ys=secondary_ys)
        fig.update_layout(title_text='Distancia y velocidad de vehículos')
        fig.update_yaxes(showgrid=False)
        fig.update_yaxes(title_text='Distancia (km)', secondary_y=False)
        fig.update_yaxes(title_text='Velocidad (km/h)', secondary_y=True)
        fig.write_image(f'{filename}')
        img = cv2.imread(f'{filename}')
        cropped = img[80:-20, :]
        cv2.imwrite(f'{filename}', cropped)
        logger.info('DistanceMaxAverageSpeedChart image generated')

    def get_reports(self):
        distances, max_speeds, average_speeds = [], [], []
        for vehicle in self.vehicles:
            total_distance, total_max_speed, total_average_speed = self.get_monthly_report(vehicle)
            distances.append(total_distance)
            max_speeds.append(total_max_speed)
            average_speeds.append(total_average_speed)
        return distances, max_speeds, average_speeds

    def get_monthly_report(self, vehicle):
        distances, max_speeds, average_speeds = [0], [0], [0]
        reservations = vehicle.reservations.filter(end__gt=self.first_day, start__lt=self.last_day)
        for reservation in reservations.reverse():
            device_id = reservation.vehicle.gps_device_id

            if reservation.start < self.first_day:
                response = TraccarAPI.get(device_id, self.first_day, reservation.end, 'reports/summary')
            # Empieza detro del mes y termina en el mes siguiente.
            elif reservation.end > self.last_day:
                response = TraccarAPI.get(device_id, reservation.start, self.last_day, 'reports/summary')
            # Empieza y termina dentro del mes.
            else:
                response = TraccarAPI.get(device_id, reservation.start, reservation.end, 'reports/summary')

            if not response.ok:
                logger.error(f'Could generate report for {vehicle.brand} {vehicle.model} at {reservation.start}')
                continue

            reports = response.json()

            if not reports:
                logger.error(f'Report received but empty [] for {vehicle.brand} {vehicle.model} at {reservation.start}')
                continue

            time.sleep(0.5)
            if reservation.start < self.first_day:
                response = TraccarAPI.get(device_id, self.first_day, reservation.end, 'reports/route')
            # Empieza detro del mes y termina en el mes siguiente.
            elif reservation.end > self.last_day:
                response = TraccarAPI.get(device_id, reservation.start, self.last_day, 'reports/route')
            # Empieza y termina dentro del mes.
            else:
                response = TraccarAPI.get(device_id, reservation.start, reservation.end, 'reports/route')

            if not response.ok:
                logger.error(f'Could generate report for {vehicle.brand} {vehicle.model} at {reservation.start}')
                continue

            route = response.json()

            if not reports:
                logger.error(f'Report received but empty [] for {vehicle.brand} {vehicle.model} at {reservation.start}')
                continue

            speeds = np.array(list(map(lambda position: position['speed'], route)))
            speeds = speeds[speeds != 0]

            if speeds.any():
                average_speed = np.mean(speeds)
                average_speeds.append(average_speed)

            # Convert units
            report = report_units_converter(reports[0])
            distances.append(report['distance'])
            max_speeds.append(report['maxSpeed'])

        total_distance = math.floor(np.sum(np.array(distances)))
        total_max_speed = math.floor(np.max(np.array(max_speeds)))
        total_average_speed = math.floor(np.mean(np.array(average_speeds)))
        return total_distance, total_max_speed, total_average_speed

    def get_distance_bar(self):
        return go.Bar(
            x=self.vehicles_labels,
            y=self.distances,
            name='Distancia (km)',
            opacity=0.4,
            text=self.distances,
            textposition='auto'
        )

    def get_max_speed_scatter(self):
        return go.Scatter(
            x=self.vehicles_labels,
            y=self.max_speeds,
            name='Vel. Max (km/h)',
            mode='lines+markers+text',
            text=self.max_speeds,
            textposition='bottom center',
            textfont=dict(color='red'),
            marker=dict(symbol='triangle-up', size=10, color='red')
        )

    def get_average_speed_scatter(self):
        return go.Scatter(
            x=self.vehicles_labels,
            y=self.average_speeds,
            name='Vel. Med (km/h)',
            mode='lines+markers+text',
            text=self.average_speeds,
            textposition='bottom center',
            marker=dict(symbol='square', size=10, color='grey')
        )

    def get_stats(self):
        return np.array(self.distances, np.float), \
               np.array(self.max_speeds, np.float), \
               np.array(self.average_speeds, np.float)
