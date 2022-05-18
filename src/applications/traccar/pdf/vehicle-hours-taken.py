import numpy as np
import plotly.graph_objects as go

from applications.tenants.models import Tenant
from applications.users.services.search import get_admin
from applications.vehicles.services.queryset import get_vehicles_queryset


class GenerateGraphImage:

    def __init__(self, tenant: Tenant):
        self.tenant = tenant
        self.WORK_HOURS_PER_MONTH = 8 * 22
        self.vehicles = self.get_vehicles()
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

    def get_vehicles(self):
        vehicles = get_vehicles_queryset(get_admin(self.tenant))
        vehicles = [f'{vehicle.number_plate}<br>{vehicle.model}' for vehicle in vehicles]
        vehicles = np.array(vehicles)
        return vehicles

    def get_reserved_hours(self):
        # TODO: Get Reserved hours
        reserved_hours = np.array([80, 120, 80, 50, 90])
        return reserved_hours

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
            x=self.vehicles,
            y=self.reserved_hours,
            marker=dict(color='#a6bde3'),
            textposition='auto',
            text=self.reserved_hours_percentages
        )

    def get_free_hours_bar(self):
        return go.Bar(
            name='Horas disponibles',
            x=self.vehicles,
            y=self.free_hours,
            marker=dict(color='white'),
            textposition='auto',
            text=self.free_hours_percentages
        )


graph_image_generator = GenerateGraphImage(Tenant.objects.last())
graph_image_generator.generate_image('fig1.png')
