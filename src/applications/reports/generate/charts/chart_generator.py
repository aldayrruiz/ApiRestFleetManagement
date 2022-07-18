import datetime
import locale

import numpy as np

from applications.tenants.models import Tenant
from applications.users.services.search import get_admins
from applications.vehicles.services.queryset import get_vehicles_queryset
from utils.dates import get_first_and_last_day_of, from_naive_to_aware


class ChartGenerator:
    def __init__(self, tenant: Tenant, month: int, year: int):
        self.month = month
        self.year = year
        self.tenant = tenant
        self.admin = get_admins(self.tenant).first()
        self.WORK_HOURS_PER_MONTH = 8 * 22
        self.vehicles = get_vehicles_queryset(self.admin).order_by('date_stored')
        self.vehicles_labels = self.get_vehicles_labels()
        self.first_day, self.last_day = get_first_and_last_day_of(self.year, self.month)
        self.first_day, self.last_day = from_naive_to_aware(self.first_day), from_naive_to_aware(self.last_day)
        self.month_title = self.get_month_title()

    def get_vehicles_labels(self):
        labels = []
        for vehicle in self.vehicles:
            label = f'{vehicle.number_plate}<br>{vehicle.model}'
            labels.append(label)
        return np.array(labels)

    def get_month_title(self):
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        date = datetime.date(self.year, self.month, 1)
        return datetime.datetime.strftime(date, '%b-%Y')
