import locale

import pytz
from django.template.loader import render_to_string
from fpdf import HTMLMixin

from applications.diets.models import Diet, PaymentType, DietPhoto
from applications.users.models import User, Role
from shared.pdf.builder import PdfBuilder
from shared.pdf.constants import HEADER_TOP_MARGIN, DEFAULT_FONT_FAMILY, WRITABLE_WIDTH, HORIZONTAL_LEFT_MARGIN

IMAGE_WIDTH_HEIGHT = 60


class DietMonthlyPdfReportGenerator(PdfBuilder, HTMLMixin):
    def __init__(self, tenant, month, year):
        super().__init__(tenant, month, year)
        self.diet_amount = 45
        self.diets = Diet.objects.filter(completed=True, tenant=self.tenant,
                                         last_modified__month=self.month, last_modified__year=self.year)

    def generate(self):
        self.add_page()
        title = 'Informe mensual de dietas y gastos imputados por los usuarios en ' \
                'BLUE Drivers'
        self.set_header(title)

        txt = 'Este informe tiene por objetivo mostrar las dietas, y sus gastos, asociados a los ' \
              'desplazamientos que se han realizado bajo la supervisión del servicio BLUE Drivers.'
        y = HEADER_TOP_MARGIN + 40
        self.set_description(txt, y)
        y += 15
        self.set_table_of_diets(y)
        self.add_page()
        self.set_diets_by_user()

    def set_table_of_diets(self, y: int):
        """
        Generate a table with the list of diets and payments by user.
        As previous to generate this table, the number of diets and payments is unknown,
        this table can be very long, so it is necessary to split it in several pages.

        :param y: y position of the table
        :return:
        """
        self.set_subtitle('Listado de dietas y gastos por usuario', y)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=6)
        self.set_text_color(0, 0, 0)  # negro
        first_page, rest_pages = self.get_data_table()
        table = render_to_string('diets_table.html', {'rows': first_page})
        table = table.replace('\n', '')
        self.set_y(y + 10)
        self.write_html(table, table_line_separators=True)
        for rows in rest_pages:
            self.add_page()
            table = render_to_string('diets_table.html', {'rows': rows})
            self.set_y(30)
            self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=6)
            self.write_html(table, table_line_separators=True)
        self.ln(5)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=8)
        self.set_x(HORIZONTAL_LEFT_MARGIN)
        self.multi_cell(WRITABLE_WIDTH, h=5, align='C', txt=f'(*) 1 dieta son {self.diet_amount}€')
        self.set_x(HORIZONTAL_LEFT_MARGIN)
        txt = f'Tabla 1: Listado de los usuarios que han imputado dietas y gastos en BLUE Drivers en el mes ' \
              f'{self.month_label} y año {self.year}.'
        self.multi_cell(WRITABLE_WIDTH, align='C', txt=txt)

    def set_diets_by_user(self):
        self.set_xy(HORIZONTAL_LEFT_MARGIN, HEADER_TOP_MARGIN + 20)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=12)
        self.set_text_color(46, 152, 209)  # azul
        txt = 'Evidencias de los gastos por usuario'
        w = self.get_string_width(txt)
        self.cell(w, h=5, align='L', txt=txt)
        users = User.objects.filter(tenant=self.tenant, role__in=[Role.USER, Role.ADMIN])
        for user in users:
            self.set_diets_of_user(user)

    def set_diets_of_user(self, user: User):
        self.ln(10)
        self.set_x(HORIZONTAL_LEFT_MARGIN)
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        self.set_font(family=DEFAULT_FONT_FAMILY, style='B', size=8)
        self.set_text_color(1, 41, 102)  # azul oscuro
        w = self.get_string_width(user.fullname)
        self.cell(w, h=5, align='L', txt=user.fullname)
        diets = self.diets.filter(owner=user)
        self.set_text_color(0, 0, 0)  # negro
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=8)
        for diet in diets:
            self.add_page_if_will_break(20)
            self.ln()
            self.set_date('Inicio', diet.start)
            self.ln()
            self.set_date('Fin', diet.end)
            self.ln()
            self.set_x(HORIZONTAL_LEFT_MARGIN + 10)
            self.cell(w=WRITABLE_WIDTH, h=5, align='L', txt='Gastos:')
            self.ln(10)
            i = 0  # En que columna va la imagen
            y = 0  # Para saber en qué "y" va la imagen de la columna 2
            for payment in diet.payments.all():
                for photo in payment.photos.all():
                    y = self.set_image(photo, y, i)
                    i += 1
                    break

    def set_date(self, title, date):
        self.set_x(HORIZONTAL_LEFT_MARGIN + 10)
        date = date.astimezone(tz=pytz.timezone('Europe/Madrid'))
        date = date.strftime('%d/%m/%Y, %H:%M')
        txt = f'{title}: {date}'
        w = self.get_string_width(title)
        self.cell(w, h=5, align='L', txt=txt)

    def set_image(self, photo: DietPhoto, y: int, i: int):
        if i % 2 == 0:  # Si es par, columna 1
            self.add_page_if_will_break(IMAGE_WIDTH_HEIGHT+5)
            x = HORIZONTAL_LEFT_MARGIN + 20
            y = self.get_y()
        else:  # Si es impar, se usará old y para la columna 2
            x = -(HORIZONTAL_LEFT_MARGIN + IMAGE_WIDTH_HEIGHT + 20)
            y = y
        self.set_xy(x, y)
        self.cell(w=IMAGE_WIDTH_HEIGHT, h=5, align='C', txt=photo.payment.get_type_display())
        self.set_xy(x, y+5)
        old_y = self.get_y() - 5
        self.image(photo.photo.path, w=IMAGE_WIDTH_HEIGHT, h=IMAGE_WIDTH_HEIGHT)
        self.ln(10)
        return old_y

    def get_data_table(self):
        rows = []

        for diet in self.diets:
            total_amount = 0
            payments = {
                PaymentType.Alojamiento: {'amount': 0, 'demand': False},
                PaymentType.Gasolina: {'amount': 0, 'demand': False},
                PaymentType.Peaje: {'amount': 0, 'demand': False},
                PaymentType.Parking: {'amount': 0, 'demand': False},
                PaymentType.Otros: {'amount': 0, 'demand': False},
            }
            for payment in diet.payments.all():
                payments[payment.type]['amount'] += payment.amount
                payments[payment.type]['demand'] += payment.demand
                if payment.demand:
                    total_amount += payment.amount

            total_amount += self.diet_amount * diet.number_of_diets

            row = {'diet': diet, 'payments': payments, 'total': total_amount}
            rows.append(row)

        n_rows_first_page = 70
        first_page = rows[:n_rows_first_page]
        rest_pages_rows = rows[n_rows_first_page:]
        default_n_rows = 80
        rest_pages = [rest_pages_rows[i:i + default_n_rows] for i in range(0, len(rest_pages_rows), default_n_rows)]
        return first_page, rest_pages

    def add_page_if_will_break(self, h):
        if self.will_page_break(h):
            self.add_page()
            self.set_y(HEADER_TOP_MARGIN + 20)
