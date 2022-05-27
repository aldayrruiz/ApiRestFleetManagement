import numpy as np
import plotly.graph_objects as go


from applications.tenants.models import Tenant
from applications.traccar.pdf.chart_generator import ChartGenerator
from utils.dates import get_hours_duration


class VehicleHoursTakenChartGenerator(ChartGenerator):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.reserved_hours = self.get_reserved_hours()
        self.free_hours = self.get_free_hours()
        self.reserved_hours_percentages = self.serialize_to_percentages(self.reserved_hours)
        self.free_hours_percentages = self.serialize_to_percentages(self.free_hours)

    def generate_image(self, filename):
        reserved_bar = self.get_reserved_hours_bar()
        free_bar = self.get_free_hours_bar()
        fig = go.Figure(data=[reserved_bar, free_bar])
        fig.update_xaxes(title_text='Vehículos')
        fig.update_yaxes(title_text='Horas')
        fig.update_layout(barmode='stack', title=f'Ocupación Vehículos {self.month_title}')
        fig.show()
        fig.write_image(f'images/{filename}')

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


graph_image_generator = VehicleHoursTakenChartGenerator(Tenant.objects.last(), 5, 2022)
graph_image_generator.generate_image('fig1.png')
