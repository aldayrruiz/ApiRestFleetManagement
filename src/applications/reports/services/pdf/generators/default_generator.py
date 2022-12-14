import logging

from applications.tenants.models import Tenant
from shared.pdf.builder import PdfBuilder
from shared.pdf.constants import HEADER_TOP_MARGIN, HORIZONTAL_LEFT_MARGIN, PDF_H, WRITABLE_WIDTH, DEFAULT_FONT_FAMILY

logger = logging.getLogger(__name__)


class DefaultChartImages:
    def __init__(self,
                 distance_max_average_speed_images,
                 fuel_consumed_images,
                 punctuality_images,
                 use_of_vehicles_without_reservation_images,
                 use_of_vehicles_by_vehicles_images,
                 ):
        self.distance_max_average_speed_images = distance_max_average_speed_images
        self.fuel_consumed_images = fuel_consumed_images
        self.punctuality_images = punctuality_images
        self.use_of_vehicles_without_reservation_images = use_of_vehicles_without_reservation_images
        self.use_of_vehicles_by_vehicles_images = use_of_vehicles_by_vehicles_images


class DefaultUseOfVehiclesReportPdf(PdfBuilder):
    def __init__(self, tenant: Tenant, month: int, year: int, chart_images: DefaultChartImages):
        super().__init__(tenant, month, year)
        self.chart_images = chart_images

    def generate(self):
        self.add_first_page()
        self.add_use_of_vehicles_by_vehicles_pages()
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
        image = self.chart_images.distance_max_average_speed_images[0]
        self.set_graph(title, desc, image, y=50)

        title = 'Consumo acumulado por vehículo'
        desc = 'Fig. 2: El presente gráfico muestra el consumo de combustible acumulado por vehículo a lo largo ' \
               'del mes.'
        image = self.chart_images.fuel_consumed_images[0]
        self.set_graph(title, desc, image, y=145)

        data = (
            ('Diesel', 'Eléctrico', 'Gasolina'),
            ('1,8 €/litro', '0,55 €/kWh', '1,7 €/litro'),
            ('8 litros/100km', '18kWh/100km', '6 litros/100km')
        )

        col_width = self.epw / 3

        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=10)
        self.set_text_color(0, 0, 0)  # negro
        self.ln()

        for row in data:
            for datum in row:
                self.multi_cell(col_width, h=7, txt=datum, border=1, align='C',
                                new_x="RIGHT", new_y="TOP", max_line_height=self.font_size)
            self.ln()
        self.set_foot_page_1()

    def add_use_of_vehicles_by_vehicles_pages(self):
        title = 'Grado de uso de los vehículos'
        desc = 'Fig. 3: Los presentes gráficos muestran el número de horas teórico, en base al tiempo de ' \
               'reserva (izquierda), y real, en base el movimiento del vehículo (derecha) que cada vehículo ' \
               'ha sido ocupado durante un mes sobre un máximo teórico [2].'
        for image in self.chart_images.use_of_vehicles_by_vehicles_images:
            self.add_page()
            self.set_graph(title, desc, image, y=30)
            self.set_foot_page_2()

    def add_second_page(self):
        self.add_page()
        title = 'Puntualidad recogiendo y liberando el vehículo según las reservas realizadas'
        desc = 'Fig. 4: El presente gráfico muestra la puntualidad de los usuarios iniciando y finalizando el ' \
               'servicio con el vehículo según las reservas realizadas.'
        image = self.chart_images.punctuality_images[0]
        self.set_graph(title, desc, image, y=HEADER_TOP_MARGIN + 20)

        title = 'Uso del vehículo sin reserva previa'
        desc = 'Fig. 5: El presente gráfico muestra el número total de horas que el vehículo se ha utilizado ' \
               'fuera de las horas reservadas por BLUE Drivers.'
        image = self.chart_images.use_of_vehicles_without_reservation_images[0]
        self.set_graph(title, desc, image, y=150)

    def set_foot_page_1(self):
        txt = '[1] La velocidad máxima representa la máxima velocidad alcanzada por el vehículo en todos ' \
               'los trayectos del mes. La velocidad media representa la media de las velocidades medias ' \
               'en todos los trayectos del mes.'
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - 32
        self.set_foot_page(txt, x, y)

    def set_foot_page_2(self):
        txt = '[2] Suponemos un máximo teórico de 176 horas/mes (8 horas/día, 22 días laborales/mes).'
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - 32
        self.set_foot_page(txt, x, y)

    def set_foot_page(self, txt, x, y):
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=8)
        self.set_text_color(0, 0, 0)
        self.set_xy(x, y)
        self.multi_cell(w=WRITABLE_WIDTH, h=5, align='L', txt=txt)
