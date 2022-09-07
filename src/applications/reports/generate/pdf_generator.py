import calendar
import locale
import logging
import os

from PIL import Image
from dateutil.relativedelta import relativedelta
from fpdf import FPDF

from applications.reports.generate.charts.distance_max_average_speed import DistanceMaxAverageSpeedChart
from applications.reports.generate.charts.real_use_of_vehicle import RealUseOfVehicleChart
from applications.reports.generate.charts.theoretical_use_of_vehicle import TheoreticalUseOfVehicleChart
from applications.reports.generate.charts.use_without_reservation import UseWithoutReservationChart
from applications.reports.generate.charts.vehicle_punctuality import PunctualityChart
from applications.reports.models.distance_max_average import DistanceMaxAverageReport
from applications.reports.models.monthly import MonthlyReport
from applications.reports.models.punctuality import PunctualityReport
from applications.reports.models.use_of_vehicle import TheoreticalUseOfVehicleReport, RealUseOfVehicleReport
from applications.reports.models.use_without_reservation import UseWithoutReservation
from applications.tenants.models import Tenant
from fleet_management.settings.base import REPORTS_PATH
from utils.dates import get_now_utc

PDF_W = 210
PDF_H = 297

FONT_FAMILY = 'Arial'

HORIZONTAL_LEFT_MARGIN = 20
HORIZONTAL_RIGHT_MARGIN = HORIZONTAL_LEFT_MARGIN
HEADER_TOP_MARGIN = 8
WRITABLE_WIDTH = PDF_W - HORIZONTAL_LEFT_MARGIN - HORIZONTAL_RIGHT_MARGIN

LOGOS = {
    'Fundación Intras': f'{REPORTS_PATH}/assets/Intras.png',
    'SaCyL ZAMORA': f'{REPORTS_PATH}/assets/SACYL.png',
    'BLUE Drivers': f'{REPORTS_PATH}/assets/BLUEDrivers.png'
}

logger = logging.getLogger(__name__)


class MonthlyReportPdf(FPDF):
    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__()
        self.tenant = tenant
        self.month = month
        self.year = year
        self.logo_tenant = LOGOS[tenant.name]

    def add_first_page(self):
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        month_label = calendar.month_name[self.month]

        # First page
        self.add_page()
        self.set_header(month_label, self.year)
        self.set_description()
        title = 'Distancia recorrida, y velocidades máxima y media, alcanzadas en un mes'
        desc = 'Fig. 1: El presente gráfico muestra los datos básicos [1] de uso de cada vehículo a lo largo del mes.'
        self.set_graph(title, desc, f'1.png', y=50)

        title = 'Grado de uso de los vehículos'
        desc = 'Fig. 2: Los presentes gráficos muestran el número de horas teórico, en base al tiempo de ' \
               'reserva (izquierda), y real, en base el movimiento del vehículo (derecha) que cada vehículo ' \
               'ha sido ocupado durante un mes sobre un máximo teórico [2].'
        self.set_double_graph(title, desc, f'2.png', f'3.png', y=145)
        self.set_foot_page()

    def add_second_page(self):
        self.add_page()
        title = 'Puntualidad recogiendo y liberando el vehículo según las reservas realizadas'
        desc = 'Fig. 3: El presente gráfico muestra la puntualidad de los usuarios iniciando y finalizando el ' \
               'servicio con el vehículo según las reservas realizadas.'
        self.set_graph(title, desc, f'4.png', y=HEADER_TOP_MARGIN + 20)

        title = 'Uso del vehículo sin reserva previa'
        desc = 'Fig. 4: El presente gráfico muestra el número total de horas que el vehículo se ha utilizado ' \
               'fuera de las horas reservadas por BLUE Drivers.'
        self.set_graph(title, desc, f'5.png', y=150)

    def header(self):
        # LOGO TENANT (IZQUIERDA)
        # Aquí la X del logo es + 1. No sé por qué, pero así está alineado con el resto del pdf.
        x = HORIZONTAL_LEFT_MARGIN + 1
        y = HEADER_TOP_MARGIN
        h = 12  # La altura debe ser definida. Sin embargo, el ancho NO, porque varía según el tenant.
        self.image(self.logo_tenant, x, y, h=h)

        # LOGO BLUE DRIVERS (DERECHA)
        x = PDF_W - HORIZONTAL_LEFT_MARGIN - h
        self.image(LOGOS['BLUE Drivers'], x, y, h=h)

    def set_header(self, month: str, year: int):
        self.set_xy(HORIZONTAL_LEFT_MARGIN, HEADER_TOP_MARGIN + 20)
        self.set_font(family=FONT_FAMILY, size=16)
        self.set_text_color(46, 152, 209)  # azul

        title = f'Informe BLUE Drivers - [{month} - {year}]'
        w = self.get_string_width(title)
        self.cell(w, h=5, align='L', txt=title)

    def set_description(self):
        # Texto descriptivo
        txt = 'Este informe tiene por objetivo extraer información relativa al ' \
              'uso de los vehículos gestionados por BLUE Drivers.'

        # Definir posiciones
        h = 5  # Altura de celda. Mientras más altura más separación entre las líneas.
        x = HORIZONTAL_LEFT_MARGIN
        y = HEADER_TOP_MARGIN + 28

        self.set_xy(x, y)
        self.set_font(family=FONT_FAMILY, style='', size=10)
        self.set_text_color(0, 0, 0)  # negro
        self.multi_cell(WRITABLE_WIDTH, h, txt)

    def set_graph(self, title, description, name, y):
        image_path = f'{REPORTS_PATH}/{self.tenant.name}/images/{name}'
        self.set_subtitle(title, y)
        # Colocar la imagen en el pdf. Estará centrada y con una anchura 4/6 del pdf.
        x = (1 / 6) * PDF_W
        y = y + 5

        image = Image.open(image_path)
        width, height = image.size
        w = (4 / 6) * PDF_W
        h = height * w / width

        self.set_xy(x, y)
        self.image(image_path, x, y, w, h)

        # Colocar la descripción de la imagen en el pdf.
        y_text = y + h
        self.set_fig_caption(description, y_text)

    def set_double_graph(self, title, description, name1, name2, y):
        image_path1 = f'{REPORTS_PATH}/{self.tenant.name}/images/{name1}'
        image_path2 = f'{REPORTS_PATH}/{self.tenant.name}/images/{name2}'
        self.set_subtitle(title, y)
        # Colocar la imagen en el pdf. Estará centrada y con una anchura 4/6 del pdf.
        x = HORIZONTAL_LEFT_MARGIN
        y = y + 5

        image1 = Image.open(image_path1)
        image2 = Image.open(image_path2)
        width1, height1 = image1.size
        width2, height2 = image2.size

        if width1 != width2 or height1 != height2 or width1 != height2:
            logger.error(f'Tamaño de la primera imagen: {width1}x{height1}')
            logger.error(f'Tamaño de la segunda imagen: {width2}x{height2}')
            logger.error('La altura y anchura debe ser igual. Las imágenes deben tener el mismo tamaño')

        horizontal_sep_images = 1
        w = (WRITABLE_WIDTH - horizontal_sep_images) / 2
        h = height1 * w / width1

        self.set_xy(x, y)
        self.image(image_path1, x, y, w, h)
        x = x + w + horizontal_sep_images
        self.image(image_path2, x, y, w, h)

        # Colocar la descripción de la imagen en el pdf.
        y_text = y + h
        self.set_fig_caption(description, y_text)

    def set_subtitle(self, txt, y):
        # Colocar el título en el pdf
        self.set_xy(HORIZONTAL_LEFT_MARGIN, y)
        self.set_font(family=FONT_FAMILY, style='', size=12)
        self.set_text_color(46, 152, 209)  # azul
        w = self.get_string_width(txt)
        self.cell(w, h=5, align='L', txt=txt)

    def set_fig_caption(self, txt, y):
        # Colocar la descripción de la imagen en el pdf.
        x = HORIZONTAL_LEFT_MARGIN
        self.set_xy(x, y)
        self.set_font(family=FONT_FAMILY, style='', size=10)
        self.set_text_color(0, 0, 0)  # negro
        self.multi_cell(WRITABLE_WIDTH, 5, txt, align='C')

    def set_foot_page(self):
        txt1 = '[1] La velocidad máxima representa la máxima velocidad alcanzada por el vehículo en todos ' \
               'los trayectos del mes. La velocidad media representa la media de las velocidades medias ' \
               'en todos los trayectos del mes.'
        txt2 = '[2] Suponemos un máximo teórico de 176 horas/mes (8 horas/día, 22 días laborales/mes).'
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - 42

        self.set_font(family=FONT_FAMILY, style='', size=8)
        self.set_text_color(0, 0, 0)  # negro
        self.set_xy(x, y)
        self.multi_cell(w=WRITABLE_WIDTH, h=5, align='L', txt=txt1)
        self.set_xy(x, y + 10)
        self.multi_cell(w=WRITABLE_WIDTH, h=5, align='L', txt=txt2)

    def footer(self) -> None:
        h = 12  # Logo
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - h - HEADER_TOP_MARGIN + 2
        self.set_font(family=FONT_FAMILY, style='', size=8)
        self.set_text_color(0, 0, 0)  # negro

        txt1 = 'drivers.bluece.eu'
        txt2 = 'drivers.app.bluece.eu'
        w1 = self.get_string_width(txt1)
        w2 = self.get_string_width(txt2)
        self.set_xy(x, y)
        self.cell(w1, h=5, align='L', txt=txt1)
        self.set_xy(x, y + 5)
        self.cell(w2, h=5, align='L', txt=txt2)

        # LOGO BLUE DRIVERS (DERECHA)
        x = PDF_W - HORIZONTAL_LEFT_MARGIN - h
        self.image(LOGOS['BLUE Drivers'], x, y, h=h)


# Main
now = get_now_utc()
previous_month = now - relativedelta(months=1)
month = previous_month.month
year = previous_month.year

tenants = Tenant.objects.all()

for tenant in tenants:
    logger.info('Generating image: DistanceMaxAverageSpeedChart')
    chart1 = DistanceMaxAverageSpeedChart(tenant, month, year)
    logger.info('Generating image: TheoreticalUseOfVehicleChart')
    chart2 = TheoreticalUseOfVehicleChart(tenant, month, year)
    logger.info('Generating image: PunctualityChart')
    chart4 = PunctualityChart(tenant, month, year)
    logger.info('Generating image: UseWithoutReservationChart')
    chart5 = UseWithoutReservationChart(tenant, month, year)
    logger.info('Generating image: RealUseOfVehicleChart')
    chart3 = RealUseOfVehicleChart(tenant, month, year, chart2, chart4)

    if not os.path.exists(f'{REPORTS_PATH}/{tenant.name}'):
        os.mkdir(f'{REPORTS_PATH}/{tenant.name}')
        os.mkdir(f'{REPORTS_PATH}/{tenant.name}/images')

    chart1.generate_image(f'{REPORTS_PATH}/{tenant.name}/images/1.png')
    chart2.generate_image(f'{REPORTS_PATH}/{tenant.name}/images/2.png')
    chart3.generate_image(f'{REPORTS_PATH}/{tenant.name}/images/3.png')
    chart4.generate_image(f'{REPORTS_PATH}/{tenant.name}/images/4.png')
    chart5.generate_image(f'{REPORTS_PATH}/{tenant.name}/images/5.png')

    pdf = MonthlyReportPdf(tenant, month, year)
    pdf.add_first_page()
    pdf.add_second_page()
    path = f'{REPORTS_PATH}/{tenant.name}_{month}_{year}.pdf'
    pdf.output(path)

    # Guardar información sobre el pdf (localización y mes)
    report = MonthlyReport(pdf=path, month=month, year=year, tenant=tenant)
    report.save()

    # Guardar información sobre las estadísticas del mes para luego obtener la del año.
    distances, max_speeds, average_speeds = chart1.get_stats()
    th_reserved_hours, th_free_hours = chart2.get_stats()
    re_reserved_hours, re_free_hours = chart3.get_stats()
    takes_out, takes_in, not_taken, frees_out, frees_in = chart4.get_stats()
    hours = chart5.get_stats()

    vehicles = chart1.vehicles
    for i, vehicle in enumerate(vehicles):
        rep1 = DistanceMaxAverageReport(
            distance=distances[i],
            max_speed=max_speeds[i],
            average_speed=average_speeds[i],
            monthly_report=report,
            vehicle=vehicle,
            tenant=tenant
        )

        rep2 = TheoreticalUseOfVehicleReport(
            hours=th_reserved_hours[i],
            monthly_report=report,
            vehicle=vehicle,
            tenant=tenant
        )

        rep4 = PunctualityReport(
            take_out=takes_out[i],
            take_in=takes_in[i],
            free_in=frees_in[i],
            free_out=frees_out[i],
            not_taken=not_taken[i],
            monthly_report=report,
            vehicle=vehicle,
            tenant=tenant
        )

        rep3 = RealUseOfVehicleReport(
            hours=re_reserved_hours[i],
            monthly_report=report,
            vehicle=vehicle,
            tenant=tenant
        )

        rep5 = UseWithoutReservation(
            hours=hours[i],
            monthly_report=report,
            vehicle=vehicle,
            tenant=tenant
        )
        
        rep1.save()
        rep2.save()
        rep3.save()
        rep4.save()
        rep5.save()

    logger.info('Pdf generated')
