import logging
import time

import cv2
import numpy as np
import plotly.graph_objects as go
from dateutil import parser
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots

from applications.reports.generate.charts.chart_generator import ChartGenerator
from applications.tenants.models import Tenant
from applications.traccar.views import send_get_to_traccar
from utils.dates import get_hours_duration

logger = logging.getLogger(__name__)


class PunctualityChart(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.takes_out, self.takes_in, self.not_taken, self.frees_out, self.frees_in = self.get_hours()

    def generate_image(self, filename):
        fig = make_subplots()
        takes_out_scatter = self.get_takes_out_scatter()
        takes_in_scatter = self.get_takes_in_scatter()
        frees_out_scatter = self.get_frees_out_scatter()
        frees_in_scatter = self.get_frees_in_scatter()
        not_taken_scatter = self.get_not_taken_scatter()
        traces = [takes_out_scatter, takes_in_scatter, not_taken_scatter, frees_out_scatter, frees_in_scatter]
        fig.add_traces(traces)
        fig.update_layout(legend=dict(y=-0.3, yanchor="bottom", xanchor="center", x=0.5))
        fig.update_yaxes(title_text='Tiempo (horas)')
        fig.write_image(f'{filename}', width=1000, height=800)
        img = cv2.imread(f'{filename}')
        cropped = img[80:-10, :]
        cv2.imwrite(f'{filename}', cropped)
        logger.info('PunctualityChart image generated')

    def get_hours(self):
        takes_out, takes_in = [], []  # Tomar el vehículo FUERA y DENTRO de la hora de la reserva.
        frees_out, frees_in = [], []  # Liberar el vehículo FUERA y DENTRO de la hora de la reserva.
        not_taken = []

        for vehicle in self.vehicles:
            reservations = vehicle.reservations.filter(end__gt=self.first_day, start__lt=self.last_day)
            punctualities = self.get_punctuality_from_reservations(reservations)
            takes_out.append(punctualities[0])
            takes_in.append(punctualities[1])
            frees_out.append(punctualities[2])
            frees_in.append(punctualities[3])
            not_taken.append(punctualities[4])
        return np.array(takes_out), np.array(takes_in), np.array(not_taken), np.array(frees_out), np.array(frees_in)

    def get_punctuality_from_reservations(self, reservations):
        takes_out, takes_in = 0, 0
        frees_out, frees_in = 0, 0
        not_taken = 0
        for reservation in reservations:
            [t_hours_out, t_hours_in, t_not_taken] = self.get_takes_punctuality_from_a_reservation(reservation)
            [f_hours_out, f_hours_in] = self.get_frees_punctuality_from_a_reservation(reservation)
            takes_out += t_hours_out
            takes_in += t_hours_in
            frees_out += f_hours_out
            frees_in += f_hours_in
            not_taken += t_not_taken
        return [takes_out, takes_in, frees_out, frees_in, not_taken]

    def get_takes_punctuality_from_a_reservation(self, reservation):
        device_id = reservation.vehicle.gps_device.id
        start = reservation.start
        end = reservation.end

        initial_limit = reservation.start - relativedelta(days=7)
        last_limit = reservation.end + relativedelta(days=7)
        reservation_duration = self.get_hours_difference(reservation.end, reservation.start)

        # Si durante la reserva no ha habido movimiento, contar toda la reserva como impuntualidad al recoger.
        summary = send_get_to_traccar(device_id, start, end, 'reports/summary').json()
        if summary[0]['distance'] == 0:
            logger.error('El vehículo no se ha movido, ergo NO HA OCURRIDO')
            return [0, 0, reservation_duration]

        time.sleep(0.1)

        # Obtener los stops y viajes para saber si el vehículo estaba en movimiento al inicio de la reserva.
        stops = send_get_to_traccar(device_id, initial_limit, last_limit, 'reports/stops').json()
        time.sleep(0.1)
        trips = send_get_to_traccar(device_id, initial_limit, last_limit, 'reports/trips').json()
        stopped_at_start = self.stopped_at_reservation_start(reservation, stops)
        trip_at_start = self.get_trip_at(reservation.start, trips)

        # Si no se ha encontrado ni que este inmóvil ni en movimiento durante el inicio de la reserva.
        # Considerar que estaba inmóvil desde más allá del límite de inicio.
        if not stopped_at_start and not trip_at_start:
            stopped_at_start = True

        # Si ocurre un stop durante el inicio de la reserva, solo contar la puntualidad dentro de la reserva.
        if stopped_at_start:
            # Tomar el primer viaje dentro de la reserva como la puntualidad DENTRO de la reserva.
            trips = send_get_to_traccar(device_id, start, last_limit, 'reports/trips').json()
            if not trips:
                logger.error(f'El vehículo se ha movido, pero no tiene ningún viaje dentro de la reserva')
                return [0, 0, reservation_duration]
            hours_in = self.get_takes_hours_from_trips(trips, reservation)
            return [0, hours_in, 0]
        # Si NO ocurre un stop durante el inicio de la reserva, solo contar la puntualidad fuera de la reserva.
        else:
            trip_start = parser.parse(trip_at_start['startTime'])
            diff = reservation.start - trip_start
            hours_out = diff.total_seconds() / 3600
            return [hours_out, 0, 0]

    def get_frees_punctuality_from_a_reservation(self, reservation):
        start = reservation.start
        end = reservation.end
        device_id = reservation.vehicle.gps_device.id

        # Obtener los viajes desde el inicio de la reserva hasta una hora después.
        one_hour_after_reservation = reservation.end + relativedelta(hours=1)

        # Obtener los stops desde una hora antes, hasta terminar la reserva.
        summary = send_get_to_traccar(device_id, start, end, 'reports/summary').json()
        if summary[0]['distance'] == 0:
            logger.error('El vehículo no se ha movido, ergo NO HA OCURRIDO')
            return [0, 0]

        time.sleep(0.1)
        trips = send_get_to_traccar(device_id, reservation.start, one_hour_after_reservation, 'reports/trips').json()
        if not trips:
            logger.error('No ha ocurrido ningún TRIP durante toda la reserva. No se ha tomado el vehículo')
            return [0, 0]

        time.sleep(0.1)
        trip_at_end = self.get_trip_at(reservation.end, trips)
        # Si NO ocurre un viaje durante el final de la reserva, solo contar la puntualidad dentro de la reserva.
        if not trip_at_end:
            trips = send_get_to_traccar(device_id, reservation.start, reservation.end, 'reports/trips').json()
            if not trips:
                logger.error('No ha ocurrido ningún TRIP durante la reserva. No se ha tomado el vehículo')
                return [0, 0]
            hours_in = self.get_frees_hours_from_trips(trips, reservation)
            return [0, hours_in]
        # Si está ocurriendo un viaje al final de la reserva, solo contar la puntualidad fuera de la reserva.
        else:
            trip_end = parser.parse(trip_at_end['endTime'])
            hours_out = get_hours_duration(reservation.end, trip_end)
            return [hours_out, 0]

    def stopped_at_reservation_start(self, reservation, stops):
        for stop in stops:
            stop_start, stop_end = parser.parse(stop['startTime']), parser.parse(stop['endTime'])
            if stop_start < reservation.start < stop_end:
                return True
        return False

    def get_trip_at(self, datetime, trips):
        for trip in trips:
            start, end = parser.parse(trip['startTime']), parser.parse(trip['endTime'])
            if start < datetime < end:
                return trip
        return None

    def get_takes_hours_from_trips(self, trips, reservation):
        if not trips:
            return 0

        first_trip = trips[0]
        first_move = parser.parse(first_trip['startTime'])
        if first_move > reservation.end:
            # El primer movimiento está fuera de la reserva.
            hours = self.get_hours_difference(reservation.end, reservation.start)
            return hours
        # Por el contrario, el primer movimiento está dentro de la reserva
        hours = self.get_hours_difference(first_move, reservation.start)
        return hours

    def get_frees_hours_from_trips(self, trips, reservation):
        if not trips:
            return 0
        last_trip = trips[-1]
        last_trip = parser.parse(last_trip['endTime'])
        hours = self.get_hours_difference(reservation.end, last_trip)
        return hours

    def get_hours_difference(self, last, first):
        diff = last - first
        hours = diff.total_seconds() / 3600
        return hours

    def get_takes_in_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.takes_in,
                          name='Inicio del servicio después del tiempo de reserva',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='green'))

    def get_takes_out_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.takes_out,
                          name='Inicio del servicio antes del tiempo de reserva',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='red'))

    def get_frees_in_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.frees_in,
                          name='Fin del servicio antes del tiempo de reserva',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='blue'))

    def get_frees_out_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.frees_out,
                          name='Fin del servicio después del tiempo de reserva',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='orange'))

    def get_not_taken_scatter(self):
        return go.Scatter(x=self.vehicles_labels,
                          y=self.not_taken,
                          name='Sin servicio en tiempo de reserva',
                          mode='lines+markers',
                          marker=dict(symbol='circle', size=10, color='black'))

    def get_stats(self):
        return np.array(self.takes_out, np.float), \
               np.array(self.takes_in, np.float), \
               np.array(self.not_taken, np.float), \
               np.array(self.frees_out, np.float), \
               np.array(self.frees_in, np.float)
