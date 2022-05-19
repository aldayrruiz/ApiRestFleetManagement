import calendar

import datetime as dt
import numpy as np
import plotly.graph_objects as go

from dateutil.relativedelta import relativedelta
from applications.tenants.models import Tenant
from applications.users.services.search import get_admin
from applications.vehicles.services.queryset import get_vehicles_queryset
from utils.dates import from_naive_to_aware


class GenerateGraphImage:

    def __init__(self, tenant: Tenant, month: int, year: int):
        self.month = month
        self.year = year
        self.tenant = tenant
        self.admin = get_admin(self.tenant)
        self.WORK_HOURS_PER_MONTH = 8 * 22
        self.vehicles = get_vehicles_queryset(self.admin)
        self.vehicles_labels = self.get_vehicles_labels()
        self.reserved_hours = self.get_reserved_hours()
        self.free_hours = self.get_free_hours()
        self.reserved_hours_percentages = self.serialize_to_percentages(self.reserved_hours)
        self.free_hours_percentages = self.serialize_to_percentages(self.free_hours)
        self.month_title = ''

    def generate_image(self, filename):
        reserved_bar = self.get_reserved_hours_bar()
        free_bar = self.get_free_hours_bar()
        fig = go.Figure(data=[reserved_bar, free_bar])
        fig.update_xaxes(title_text='Vehículos')
        fig.update_yaxes(title_text='Horas')
        fig.update_layout(barmode='stack', title=f'Ocupación Vehículos {self.month_title}')
        fig.show()
        fig.write_image(f'images/{filename}')

    def get_vehicles_labels(self):
        vehicles = [f'{vehicle.number_plate}<br>{vehicle.model}' for vehicle in self.vehicles]
        vehicles = np.array(vehicles)
        return vehicles

    def get_reserved_hours(self):
        first, last = self.get_first_and_last_day_of(self.year, self.month)
        first, last = from_naive_to_aware(first), from_naive_to_aware(last)
        reserved_hours = [self.get_reserved_hours_for_vehicle(vehicle, first, last) for vehicle in self.vehicles]
        # reserved_hours = np.array([80, 120, 80, 50, 90])
        return np.array(reserved_hours)

    def get_reserved_hours_for_vehicle(self, vehicle, first_datetime, last_datetime):
        # Reservas de un mes, pero incluyendo las que comienzan antes del mes y terminan dentro del mes.
        # Y además, las que comienzan dentro del mes, pero terminan en el mes siguiente.
        # Luego, Excluimos las horas que no están dentro del mes.

        reservations = vehicle.reservations.filter(end__gt=first_datetime, start__lt=last_datetime)
        hours = 0
        for reservation in reservations:
            # Empieza antes del mes y termina dentro del mes.
            if reservation.start < first_datetime:
                hours += self.get_hours_from(first_datetime, reservation.end)
            # Empieza detro del mes y termina en el mes siguiente.
            elif reservation.end > last_datetime:
                hours += self.get_hours_from(reservation.start, last_datetime)
            # Empieza y termina dentro del mes.
            else:
                hours += self.get_hours_from(reservation.start, reservation.end)
        return hours

    def get_hours_from(self, start, end):
        duration = relativedelta(end, start)
        hours = duration.days * 24 + duration.minutes / 60 + duration.hours
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
            name='Horas reservado',
            x=self.vehicles_labels,
            y=self.reserved_hours,
            marker=dict(color='#a6bde3'),
            textposition='auto',
            text=self.reserved_hours_percentages
        )

    def get_free_hours_bar(self):
        return go.Bar(
            name='Horas disponibles',
            x=self.vehicles_labels,
            y=self.free_hours,
            marker=dict(color='white'),
            textposition='auto',
            text=self.free_hours_percentages
        )

    def get_first_and_last_day_of(self, year, month):
        (_, last_day) = calendar.monthrange(year, month)
        first_datetime = dt.datetime(year, month, 1, 0, 0, 0, 0)
        last_datetime = dt.datetime(year, month, last_day, 0, 0, 0, 0)
        return first_datetime, last_datetime


graph_image_generator = GenerateGraphImage(Tenant.objects.last(), 5, 2022)
graph_image_generator.generate_image('fig1.png')
