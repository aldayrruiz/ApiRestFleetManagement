import datetime
from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string
from fpdf import HTMLMixin

from applications.tenants.models import Tenant
from applications.users.models import ActionType
from shared.pdf.builder import PdfBuilder
from shared.pdf.constants import HEADER_TOP_MARGIN, DEFAULT_FONT_FAMILY
from utils.dates import get_number_of_days_in_month


class TenantBillingMonthlyPdfReportGenerator(PdfBuilder, HTMLMixin):

    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)
        self.total_days = get_number_of_days_in_month(self.month, self.year)
        self.first_day_of_this_month = datetime.date(self.year, self.month, 1)
        self.first_day_of_next_month = self.first_day_of_this_month + relativedelta(months=1)
        self.users = tenant.users.exclude(date_joined__gt=self.first_day_of_next_month)
        self.vehicles = tenant.vehicles.all()

    def generate(self):
        self.add_page()
        title = 'Informe mensual de usuarios y vehículos en BLUE Drivers'
        self.set_header(title)

        txt = 'Este informe tiene por objetivo indicar qué usuarios y vehículos han estado dados de alta en la ' \
              'plataforma BLUE Drivers. Asimismo, se indica qué número de días han estado dados de alta y qué días ' \
              'del mes.'
        y = HEADER_TOP_MARGIN + 40
        self.set_description(txt, y)
        y += 15
        self.set_table_of_users(y)
        self.add_page()
        self.set_table_of_vehicles(HEADER_TOP_MARGIN + 20)

    def set_table_of_users(self, y: int):
        """
        Generate a table with the list of users and their billing information.

        :param y: y position of the table
        :return:
        """
        self.set_subtitle('Listado de usuarios', y)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=6)
        self.set_text_color(0, 0, 0)  # negro
        # Get Data table: Pages: [70 rows, 80 rows, 80 rows, ...]
        pages, total = self.get_user_data_table()
        n_pages = len(pages)
        table = render_to_string('billing/users_table.html',
                                 {'data': pages[0],
                                  'total': total,
                                  'last_page': 1 == n_pages})
        table = table.replace('\n', '')
        self.set_y(y + 10)
        self.write_html(table, table_line_separators=True)

        for i, data in enumerate(pages[1:], 1):
            self.add_page()
            table = render_to_string('billing/users_table.html',
                                     {'data': data,
                                      'total': total,
                                      'last_page': i == n_pages - 1})
            self.set_y(30)
            self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=6)
            self.write_html(table, table_line_separators=True)

    def get_user_data_table(self):
        rows = []
        total_bill = 0
        for user in self.users:
            number_of_days = self.get_number_of_days_registered(user)
            units_to_bill = number_of_days / self.total_days
            total_bill += units_to_bill
            row = {'user': user, 'number_of_days': number_of_days, 'units_to_bill': units_to_bill}
            rows.append(row)
        pages = self.divide_into_pages(rows, 70, 80)
        return pages, total_bill

    def set_table_of_vehicles(self, y: int):
        """
        Generate a table with the list of vehicles and their billing information.

        :param y: y position of the table
        :return:
        """
        self.set_subtitle('Listado de vehículos', y)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=6)
        self.set_text_color(0, 0, 0)  # negro
        # Get Data table: Pages: [70 rows, 80 rows, 80 rows, ...]
        pages, total = self.get_vehicle_data_table()
        n_pages = len(pages)
        table = render_to_string('billing/vehicles_table.html', {'data': pages[0], 'total': total, 'last_page': 1 == n_pages})
        table = table.replace('\n', '')
        self.set_y(y + 10)
        self.write_html(table, table_line_separators=True)

        for i, data in enumerate(pages[1:], 1):
            self.add_page()
            table = render_to_string('billing/vehicles_table.html', {'data': data, 'total': total, 'last_page': i == n_pages - 1})
            self.set_y(30)
            self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=6)
            self.write_html(table, table_line_separators=True)

    def get_vehicle_data_table(self):
        rows = []
        total_bill = 0
        for vehicle in self.vehicles:
            number_of_days = self.get_number_of_days_registered(vehicle)
            units_to_bill = number_of_days / self.total_days
            total_bill += units_to_bill
            row = {'vehicle': vehicle, 'number_of_days': number_of_days, 'units_to_bill': units_to_bill}
            rows.append(row)
        pages = self.divide_into_pages(rows, 70, 80)
        return pages, total_bill

    def divide_into_pages(self, rows, first, default):
        """
        Divide an array of rows into an array of pages, where each page has a maximum number of rows.
        The first array will have a different number of rows than the rest of the arrays.

        :param rows: Rows to divide
        :param first: Number of rows to first array
        :param default: Number of rows to default array
        :return: Return a list of arrays [first, default, default, ...]
        """
        first_page = rows[:first]
        rest_pages_rows = rows[first:]
        rest_pages = [rest_pages_rows[i:i + default] for i in range(0, len(rest_pages_rows), default)]
        pages = [first_page]
        pages.extend(rest_pages)
        return pages

    def get_number_of_days_registered(self, obj):
        history = obj.registration_history.exclude(date__gt=self.first_day_of_next_month).order_by('-date').all()
        last_registry = history.first()

        # Error: No hay registro de alta
        if not last_registry:
            raise Exception(f'No hay registro de alta para {obj}')

        # Si el último registro que se tiene es de meses anteriores.
        if last_registry.date < datetime.datetime(self.year, self.month, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc):
            # Y este mismo ha sido borrado en meses anteriores.
            if last_registry.action == ActionType.DELETED:
                number_of_days = 0
                return number_of_days
            # Y este mismo ha sido creado en meses anteriores.
            else:
                number_of_days = self.total_days
                return number_of_days

        # Si, por el contrario, se ha registrado o eliminado este mes (varias veces)...
        history_this_month = history.filter(date__month=self.month, date__year=self.year)
        created_this_month = history_this_month.filter(action=ActionType.CREATED)
        deleted_this_month = history_this_month.filter(action=ActionType.DELETED)

        # Si solo se ha creado este mes.
        if created_this_month.count() == 1 and deleted_this_month.count() == 0:
            number_of_days = self.total_days - created_this_month.first().date.day
            return number_of_days

        # Si solo se ha eliminado este mes.
        if created_this_month.count() == 0 and deleted_this_month.count() == 1:
            number_of_days = deleted_this_month.first().date.day
            return number_of_days

        # Si se ha creado y eliminado este mes (varias veces).
        number_of_days = datetime.timedelta(0)
        for entry in history_this_month.all():
            if entry.action == ActionType.CREATED:
                number_of_days -= datetime.timedelta(entry.date.day)
            else:
                number_of_days += datetime.timedelta(entry.date.day)

        if created_this_month.count() > deleted_this_month.count():
            number_of_days += datetime.timedelta(self.total_days)

        return number_of_days.days
