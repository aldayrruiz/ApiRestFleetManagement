import logging

from applications.tenants.models import Tenant
from shared.pdf.builder import PdfBuilder
from shared.pdf.constants import HEADER_TOP_MARGIN, HORIZONTAL_LEFT_MARGIN, PDF_H, WRITABLE_WIDTH, DEFAULT_FONT_FAMILY

logger = logging.getLogger(__name__)


class IntrasChartImages:
    def __init__(self,
                 distance_max_average_speed_images,
                 fuel_consumed_images,
                 punctuality_images,
                 use_of_vehicles_without_reservation_images,
                 use_of_vehicles_by_vehicle_morning_images,
                 use_of_vehicles_by_vehicle_afternoon_images,
                 use_of_vehicles_by_user_images,
                 ):
        self.distance_max_average_speed_images = distance_max_average_speed_images
        self.fuel_consumed_images = fuel_consumed_images
        self.punctuality_images = punctuality_images
        self.use_of_vehicles_without_reservation_images = use_of_vehicles_without_reservation_images
        self.use_of_vehicles_by_vehicle_morning_images = use_of_vehicles_by_vehicle_morning_images
        self.use_of_vehicles_by_vehicle_afternoon_images = use_of_vehicles_by_vehicle_afternoon_images
        self.use_of_vehicles_by_user_images = use_of_vehicles_by_user_images


class IntrasUseOfVehiclesReportPdf(PdfBuilder):
    def __init__(self, tenant: Tenant, month: int, year: int, chart_images: IntrasChartImages):
        super().__init__(tenant, month, year)
        self.chart_images = chart_images

    def generate(self):
        self.add_first_page()
        self.add_use_of_vehicles_by_vehicles_morning_pages()
        self.add_use_of_vehicles_by_vehicles_afternoon_pages()
        self.add_third_page()
        self.add_use_of_vehicles_by_users_pages()

    def add_first_page(self):
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

    def add_use_of_vehicles_by_vehicles_morning_pages(self):
        title = 'Grado de uso de los vehículos (mañana)'
        desc = 'Fig. 3: Los presentes gráficos muestran de forma acumulada en el mes, y en horario de mañana, ' \
               'de 8h a 15h, (a) el número de horas que el vehículo ha sido reservado, (b) el número de horas ' \
               'que el vehículo ha estado ocupado y (c) el número de horas que el vehículo ha estado en ' \
               'movimiento. Los porcentajes se han calculado sobre un límite máximo teórico: 30 días/mes y ' \
               '7h/día en horario de mañana.'
        for image in self.chart_images.use_of_vehicles_by_vehicle_morning_images:
            self.add_page()
            self.set_graph(title, desc, image, y=30)
            self.set_foot_page_2()

    def add_use_of_vehicles_by_vehicles_afternoon_pages(self):
        title = 'Grado de uso de los vehículos (tarde)'
        desc = 'Fig. 4: Los presentes gráficos muestran de forma acumulada en el mes, y en horario de tarde, de ' \
               '15h a 22h, (a) el número de horas que el vehículo ha sido reservado, (b) el número de horas que ' \
               'el vehículo ha estado ocupado y (c) el número de horas que el vehículo ha estado en movimiento. ' \
               'Los porcentajes se han calculado sobre un límite máximo teórico: 30 días/mes y 7h/día en horario ' \
               'de tarde.'
        for image in self.chart_images.use_of_vehicles_by_vehicle_afternoon_images:
            self.add_page()
            self.set_graph(title, desc, image, y=30)
            self.set_foot_page_2()

    def add_third_page(self):
        self.add_page()
        title = 'Puntualidad recogiendo y liberando el vehículo según las reservas realizadas'
        desc = 'Fig. 5: El presente gráfico muestra la puntualidad de los usuarios iniciando y finalizando el ' \
               'servicio con el vehículo según las reservas realizadas.'
        image = self.chart_images.punctuality_images[0]
        self.set_graph(title, desc, image, y=HEADER_TOP_MARGIN + 20)

        title = 'Uso del vehículo sin reserva previa'
        desc = 'Fig. 6: El presente gráfico muestra el número total de horas que el vehículo se ha utilizado ' \
               'fuera de las horas reservadas por BLUE Drivers.'
        image = self.chart_images.use_of_vehicles_without_reservation_images[0]
        self.set_graph(title, desc, image, y=150)

    def add_use_of_vehicles_by_users_pages(self):
        title = 'Grado de uso de los vehículos por usuarios'
        desc = 'Fig. 7: Los presentes gráficos muestran de forma acumulada en el mes, el número de horas que ' \
               'cada usuario ha utilizado cada vehículo.'
        for image in self.chart_images.use_of_vehicles_by_user_images:
            self.add_page()
            self.set_graph(title, desc, image, y=30)
            self.set_foot_page_2()

    def set_foot_page_1(self):
        txt = '[1] La velocidad máxima representa la máxima velocidad alcanzada por el vehículo en todos ' \
              'los trayectos del mes. La velocidad media representa la media de las velocidades medias ' \
              'en todos los trayectos del mes.'
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - 32
        self.set_foot_page(txt, x, y)

    def set_foot_page_2(self):
        txt = '(*) Este vehículo ha tenido al menos una reserva que se ha extendido más allá de las 15h si ' \
              'se trata de un vehículo de mañana, o más allá de las 22h si se trata de un vehículo de tarde.'
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - 32
        self.set_foot_page(txt, x, y)

    def set_foot_page(self, txt, x, y):
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=8)
        self.set_text_color(0, 0, 0)
        self.set_xy(x, y)
        self.multi_cell(w=WRITABLE_WIDTH, h=5, align='L', txt=txt)
