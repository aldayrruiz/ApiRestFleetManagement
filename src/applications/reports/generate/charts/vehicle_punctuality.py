import logging
import time

import cv2
import numpy as np
import plotly.graph_objects as go
from dateutil import parser
from plotly.subplots import make_subplots

from applications.reports.generate.charts.chart_generator import ChartGenerator
from applications.reports.services.punctuality import PunctualityHelpers
from applications.tenants.models import Tenant
from applications.traccar.services.api import TraccarAPI
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
            reservations_ordered_by_start = reservations.order_by('start')
            punctualities = self.get_punctuality_from_reservations(reservations_ordered_by_start)
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
        for i, reservation in enumerate(reservations):
            previous_reservation, next_reservation = PunctualityHelpers.get_closer_reservations(reservations, i)
            [t_hours_out, t_hours_in, t_not_taken] = self.get_takes_punctuality(previous_reservation, reservation,
                                                                                next_reservation)
            [f_hours_out, f_hours_in] = self.get_frees_punctuality(previous_reservation, reservation, next_reservation)
            takes_out += t_hours_out
            takes_in += t_hours_in
            frees_out += f_hours_out
            frees_in += f_hours_in
            not_taken += t_not_taken
        return [takes_out, takes_in, frees_out, frees_in, not_taken]

    @staticmethod
    def get_takes_punctuality(previous_reservation, reservation, next_reservation):
        device_id = reservation.vehicle.gps_device.id
        start = reservation.start

        # Calcular la puntualidad fuera de la reserva (antes o posteriormente), solo tener en cuenta un error de 1 hora.
        # Por ejemplo, no se estima que un empleado recoja el vehículo dos horas antes de lo previsto.
        start_limit, end_limit = PunctualityHelpers.get_reservation_bounds(previous_reservation, reservation,
                                                                           next_reservation)
        reservation_duration = PunctualityHelpers.get_hours_difference(reservation.end, reservation.start)

        # Si durante la reserva no ha habido movimiento, contar toda la reserva como impuntualidad al recoger.
        if not PunctualityHelpers.vehicle_moved_during_reservation(reservation):
            return [0, 0, reservation_duration]

        time.sleep(0.1)

        # Obtener los stops y viajes para saber si el vehículo estaba en movimiento al inicio de la reserva.
        stops = TraccarAPI.stops(device_id, start_limit, end_limit)
        time.sleep(0.1)
        trips = TraccarAPI.trips(device_id, start_limit, end_limit)
        stopped_at_start = PunctualityHelpers.stopped_at_reservation_start(reservation, stops)
        trip_at_start = PunctualityHelpers.get_trip_at(start, trips)

        # Si no se ha encontrado ni que este inmóvil ni en movimiento durante el inicio de la reserva.
        # Considerar que estaba inmóvil desde más allá del límite de inicio.
        if not stopped_at_start and not trip_at_start:
            stopped_at_start = True

        # Si ocurre un stop durante el inicio de la reserva, solo contar la puntualidad dentro de la reserva.
        if stopped_at_start:
            # Tomar el primer viaje dentro de la reserva como la puntualidad DENTRO de la reserva.
            trips = TraccarAPI.trips(device_id, start, end_limit)
            if not trips:
                logger.error(f'El vehículo se ha movido, pero no tiene ningún viaje dentro de la reserva')
                return [0, 0, reservation_duration]
            hours_in = PunctualityHelpers.get_takes_hours_from_trips(trips, reservation)
            return [0, hours_in, 0]
        # Si NO ocurre un stop durante el inicio de la reserva, solo contar la puntualidad fuera de la reserva.
        else:
            trip_start = parser.parse(trip_at_start['startTime'])
            diff = start - trip_start
            hours_out = diff.total_seconds() / 3600
            return [hours_out, 0, 0]

    @staticmethod
    def get_frees_punctuality(previous_reservation, reservation, next_reservation):
        device_id = reservation.vehicle.gps_device.id
        start = reservation.start
        end = reservation.end

        # Calcular la puntualidad fuera de la reserva (antes o posteriormente), solo tener en cuenta un error de 1 hora.
        # Por ejemplo, no se estima que un empleado devuelva el vehículo dos horas después de lo previsto.
        initial_limit, last_limit = PunctualityHelpers.get_reservation_bounds(previous_reservation, reservation,
                                                                              next_reservation)

        # Si no ha ocurrido movimiento durante la reserva no considerar nada.
        if not PunctualityHelpers.vehicle_moved_during_reservation(reservation):
            return [0, 0]

        time.sleep(0.1)

        trips = TraccarAPI.trips(device_id, initial_limit, last_limit)
        if not trips:
            logger.error('No ha ocurrido ningún TRIP durante toda la reserva. No se ha tomado el vehículo')
            return [0, 0]

        time.sleep(0.1)
        trip_at_end = PunctualityHelpers.get_trip_at(end, trips)
        # Si NO ocurre un viaje durante el final de la reserva, solo contar la puntualidad dentro de la reserva.
        if not trip_at_end:
            # Consideramos los viajes que comiencen un poco antes de la reserva. Por si, el viaje empezaba antes.
            # Y ponemos como límite el final, dado que no ocurre un viaje al final.
            trips = TraccarAPI.trips(device_id, initial_limit, end)
            if not trips:
                logger.error('No ha ocurrido ningún TRIP durante la reserva. No se ha tomado el vehículo')
                return [0, 0]
            hours_in = PunctualityHelpers.get_frees_hours_from_trips(trips, reservation)
            return [0, hours_in]
        # Si está ocurriendo un viaje al final de la reserva, solo contar la puntualidad fuera de la reserva.
        else:
            trip_end = parser.parse(trip_at_end['endTime'])
            hours_out = get_hours_duration(end, trip_end)
            return [hours_out, 0]

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
