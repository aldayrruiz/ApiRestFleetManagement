import logging

import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from applications.tenants.models import Tenant
from applications.traccar.pdf.chart_generator import ChartGenerator
from applications.traccar.utils import report_units_converter
from applications.traccar.views import send_get_to_traccar


logger = logging.getLogger(__name__)


class UseOfVehicleChartGenerator(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.distances, self.max_speeds, self.average_speeds = self.get_reports()
        # distance = np.array([1965, 2345, 1900, 2568, 3467]) # Distance (km)
        # max_speed = np.array([115, 112, 125, 145, 126]) # Max Speed (km/h)
        # average_speed = np.array([50, 45, 60, 75, 70]) # Average Speed (km/h)

    def generate_image(self, filename):
        bar = self.get_distance_bar()
        scatter1 = self.get_max_speed_scatter()
        scatter2 = self.get_average_speed_scatter()
        traces = [bar, scatter1, scatter2]
        secondary_ys = [False, True, True]
        fig = make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_traces(traces, secondary_ys=secondary_ys)
        fig.update_layout(title_text='Distancia y velocidad de vehículos')
        fig.update_yaxes(title_text='Distancia', secondary_y=False)
        fig.update_yaxes(title_text='Velocidad', secondary_y=True)
        fig.show()
        fig.write_image(f'images/{filename}')

    def get_reports(self):
        distances, max_speeds, average_speeds = [], [], []
        for vehicle in self.vehicles:
            total_distance, total_max_speed, total_average_speed = self.get_monthly_report(vehicle)
            distances.append(total_distance)
            max_speeds.append(total_max_speed)
            average_speeds.append(total_average_speed)
        return distances, max_speeds, average_speeds

    def get_monthly_report(self, vehicle):
        distances, max_speeds, average_speeds = [], [], []
        for reservation in vehicle.reservations:
            device_id = reservation.vehicle.gps_device.id

            # Empieza antes del mes y termina dentro del mes.
            if reservation.start < self.first_day:
                response = send_get_to_traccar(device_id, self.first_day, reservation.end, 'reports/route')
            # Empieza detro del mes y termina en el mes siguiente.
            elif reservation.end > self.last_day:
                response = send_get_to_traccar(device_id, reservation.start, self.last_day, 'reports/route')
            # Empieza y termina dentro del mes.
            else:
                response = send_get_to_traccar(device_id, reservation.start, reservation.end, 'reports/route')

            if not response.ok:
                logger.error(f'Could generate report for {vehicle.brand} {vehicle.model} at {reservation.start}')
                continue
            report = response.json()

            # Convert units
            report = report_units_converter(report)
            distances.append(report['distance'])
            max_speeds.append(report['maxSpeed'])
            average_speeds.append(report['averageSpeed'])

        total_distance = np.sum(np.array(distances))
        total_max_speed = np.max(np.array(max_speeds))
        total_average_speed = np.mean(np.array(average_speeds))
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

# if not os.path.exists('images'):
#     os.mkdir('images')
#
# fig.write_image('images/fig3.png')
