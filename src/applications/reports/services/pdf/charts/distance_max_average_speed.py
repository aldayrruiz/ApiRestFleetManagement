import logging
import time

import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from applications.reports.services.measure import from_meters_to_kilometers, from_knots_to_kph
from applications.reports.services.pdf.charts.chart_generator import ChartGenerator
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.tenants.models import Tenant
from applications.traccar.services.api import TraccarAPI
from applications.traccar.utils import report_units_converter

logger = logging.getLogger(__name__)


class DistanceMaxAverageSpeedChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int, hour_config: HoursChartConfiguration = None,
                 by: str = 'vehicle',
                 n_values: int = 25,
                 orientation: str = 'h'):
        super().__init__(tenant, month, year, hour_config, by, n_values, orientation)
        self.distances, self.max_speeds, self.average_speeds = self.get_reports()

    def generate_image(self, filename, start, end, i):
        # This chart cannot be horizontal
        bar = self.get_distance_bar(start, end)
        scatter1 = self.get_max_speed_scatter(start, end)
        scatter2 = self.get_average_speed_scatter(start, end)
        traces = [bar, scatter1, scatter2]
        secondary_ys = [False, True, True]
        fig = make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_traces(traces, secondary_ys=secondary_ys)
        fig.update_layout(title_text='Distancia y velocidad de vehículos')
        fig.update_layout(plot_bgcolor='rgb(255,255,255)')
        fig.update_yaxes(showgrid=False)
        fig.update_yaxes(title_text='Distancia (km)', secondary_y=False)
        fig.update_yaxes(title_text='Velocidad (km/h)', secondary_y=True)
        fig.write_image(f'{filename}{i}.png')
        self.remove_image_header(f'{filename}{i}.png')
        self.images.append(f'{filename}{i}.png')

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
        reservations = self.all_reservations.filter(vehicle=vehicle)
        for reservation in reservations:
            device_id = reservation.vehicle.gps_device_id

            reports = TraccarAPI.get(device_id, reservation.start, reservation.end, 'reports/summary').json()
            time.sleep(0.2)
            route = TraccarAPI.get(device_id, reservation.start, reservation.end, 'reports/route').json()

            speeds = np.array(list(map(lambda position: position['speed'], route)))
            speeds = speeds[speeds != 0]

            # Calculate average speed
            if speeds.any():
                average_speed = np.mean(speeds)
                average_speeds.append(from_knots_to_kph(float(average_speed)))

            # Calculate distance (Invalid positions with odometer corrupt summary calculation - Traccar)
            pos_distances = np.array(list(map(lambda position: position['attributes']['distance'], route)))
            distance = from_meters_to_kilometers(float(np.sum(pos_distances)))

            # Convert units
            report = report_units_converter(reports[0])
            distances.append(distance)
            max_speeds.append(report['maxSpeed'])

        total_distance = math.floor(np.sum(np.array(distances)))
        total_max_speed = math.floor(np.max(np.array(max_speeds)))
        total_average_speed = math.floor(np.mean(np.array(average_speeds)))
        return total_distance, total_max_speed, total_average_speed

    def get_distance_bar(self, start, end):
        x, y = self.get_xy(self.distances)
        return go.Bar(
            x=x[start:end],
            y=y[start:end],
            marker=dict(color='#a6bde3'),
            name='Distancia (km)',
            text=self.distances[start:end],
            textposition='auto',
            orientation=self.orientation
        )

    def get_max_speed_scatter(self, start, end):
        x, y = self.get_xy(self.max_speeds)
        return go.Scatter(
            x=x[start:end],
            y=y[start:end],
            name='Vel. Max (km/h)',
            mode='lines+markers+text',
            text=self.max_speeds[start:end],
            textposition='bottom center',
            textfont=dict(color='red'),
            marker=dict(symbol='triangle-up', size=10, color='red'),
            orientation=self.orientation
        )

    def get_average_speed_scatter(self, start, end):
        x, y = self.get_xy(self.average_speeds)
        return go.Scatter(
            x=x[start:end],
            y=y[start:end],
            name='Vel. Med (km/h)',
            mode='lines+markers+text',
            text=self.average_speeds[start:end],
            textposition='bottom center',
            marker=dict(symbol='square', size=10, color='grey'),
            orientation=self.orientation
        )

    def get_stats(self):
        return np.array(self.distances, np.float), \
               np.array(self.max_speeds, np.float), \
               np.array(self.average_speeds, np.float)
