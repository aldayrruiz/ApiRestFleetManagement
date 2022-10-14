import logging
import os

from PIL import Image
from dateutil.relativedelta import relativedelta

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
from shared.pdf.builder import PdfBuilder
from shared.pdf.constants import HEADER_TOP_MARGIN, PDF_W, HORIZONTAL_LEFT_MARGIN, PDF_H, WRITABLE_WIDTH, DEFAULT_FONT_FAMILY

from applications.reports.generate.reports import ReportsPdfPath
from utils.dates import get_now_utc

LOGOS = {
    'Intras': ReportsPdfPath.get_logo('Intras.png'),
    'SaCyL': ReportsPdfPath.get_logo('SACYL.png'),
    'BLUE Drivers': ReportsPdfPath.get_logo('BLUEDrivers.png')
}

logger = logging.getLogger(__name__)


class MonthlyReportPdf(PdfBuilder):
    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__(tenant, month, year)

    def generate(self):
        self.add_first_page()
        self.add_second_page()

    def add_first_page(self):
        # First page
        self.add_page()
        self.set_header('Informe BLUE Drivers')

        txt = 'Este informe tiene por objetivo extraer información relativa al ' \
              'uso de los vehículos gestionados por BLUE Drivers.'
        self.set_description(txt, HEADER_TOP_MARGIN + 28)

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

    def set_graph(self, title, description, filename, y):
        image_path = ReportsPdfPath.get_graph(self.tenant, filename)
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

    def set_double_graph(self, title, description, filename1, filename2, y):
        image_path1 = ReportsPdfPath.get_graph(self.tenant, filename1)
        image_path2 = ReportsPdfPath.get_graph(self.tenant, filename2)
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

    def set_foot_page(self):
        txt1 = '[1] La velocidad máxima representa la máxima velocidad alcanzada por el vehículo en todos ' \
               'los trayectos del mes. La velocidad media representa la media de las velocidades medias ' \
               'en todos los trayectos del mes.'
        txt2 = '[2] Suponemos un máximo teórico de 176 horas/mes (8 horas/día, 22 días laborales/mes).'
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - 42

        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=8)
        self.set_text_color(0, 0, 0)  # negro
        self.set_xy(x, y)
        self.multi_cell(w=WRITABLE_WIDTH, h=5, align='L', txt=txt1)
        self.set_xy(x, y + 10)
        self.multi_cell(w=WRITABLE_WIDTH, h=5, align='L', txt=txt2)


# Main
now = get_now_utc()
previous_month = now - relativedelta(months=1)
month = previous_month.month
year = previous_month.year

tenants = Tenant.objects.exclude(name__in=['Local Pruebas', 'Pruebas BLUE'])

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

    if not os.path.exists(ReportsPdfPath.get_tenant(tenant)):
        os.mkdir(ReportsPdfPath.get_tenant(tenant))
        os.mkdir(ReportsPdfPath.get_graphs(tenant))

    chart1.generate_image(ReportsPdfPath.get_graph(tenant, '1.png'))
    chart2.generate_image(ReportsPdfPath.get_graph(tenant, '2.png'))
    chart3.generate_image(ReportsPdfPath.get_graph(tenant, '3.png'))
    chart4.generate_image(ReportsPdfPath.get_graph(tenant, '4.png'))
    chart5.generate_image(ReportsPdfPath.get_graph(tenant, '5.png'))

    pdf = MonthlyReportPdf(tenant, month, year)
    pdf.generate()
    path = ReportsPdfPath.get_pdf(tenant, month, year)
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
