import time

import numpy as np
import pandas as pd
import plotly.express as px

from applications.tenants.models import Tenant
from applications.traccar.pdf.chart_generator import ChartGenerator
from applications.traccar.views import send_get_to_traccar


class VehicleOutOfReservedHours(ChartGenerator):
    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.hours = self.get_hours()
        df_dict = {'vehicles': self.vehicles_labels, 'hours': self.hours}
        self.df = pd.DataFrame(df_dict)

    def generate_image(self, filename):
        fig = self.get_histogram()
        fig.update_xaxes(title_text='Vehículos')
        fig.update_yaxes(title_text='Horas')
        fig.show()
        fig.write_image(f'images/{filename}')

    def get_hours(self):
        hours = []
        for vehicle in self.vehicles:
            print(vehicle.model)
            reservations = vehicle.reservations.filter(end__gt=self.first_day, start__lt=self.last_day).reverse()
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
                    date = {'from': reservations[index-1].end, 'to': reservation.start}
                dates.append(date)

            total_duration = 0
            for date in dates:
                time.sleep(0.2)
                response = send_get_to_traccar(vehicle.gps_device.id, date['from'], date['to'], 'reports/trips')
                if not response.ok:
                    print('Something has failed')
                trips = response.json()
                durations = list(map(lambda trip: trip['duration'], trips))
                total_duration = total_duration + np.sum(np.array(durations))
            duration_into_hours = ((total_duration / (1000 * 60 * 60)) % 24)
            hours.append(duration_into_hours)
        return hours

    def get_histogram(self):
        return px.histogram(
            self.df,
            title=f'Uso de Vehículos {self.month_title}',
            x='vehicles',
            y='hours',
            range_y=[0, 60],
            labels=dict(category='Leyenda')
        )


VehicleOutOfReservedHours(Tenant.objects.get(name__exact='Valladolid'), 3, 2022).generate_image('fig2.png')
