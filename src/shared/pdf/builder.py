import calendar
import locale
import logging

from fpdf import FPDF
from PIL import Image

from applications.tenants.models import Tenant
from fleet_management.settings.base import BASE_DIR
from applications.reports.services.pdf.reports import ReportsPdfPath
from shared.pdf.constants import HORIZONTAL_LEFT_MARGIN, HEADER_TOP_MARGIN, PDF_W, DEFAULT_FONT_FAMILY, WRITABLE_WIDTH, PDF_H


BLUE_DRIVERS_LOGO = ReportsPdfPath.get_logo('BLUEDrivers.png')

logger = logging.getLogger(__name__)


class PdfBuilder(FPDF):
    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__()
        self.tenant = tenant
        self.month = month
        self.year = year
        self.logo_tenant = tenant.logo.path
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        self.month_label = calendar.month_name[month]
        self.add_default_font()

    def header(self):
        # LOGO TENANT (IZQUIERDA)
        # Aquí la X del logo es + 1. No sé por qué, pero así está alineado con el resto del pdf.
        x = HORIZONTAL_LEFT_MARGIN + 1
        y = HEADER_TOP_MARGIN
        h = 12  # La altura debe ser definida. Sin embargo, el ancho NO, porque varía según el tenant.
        self.image(self.logo_tenant, x, y, h=h)

        # LOGO BLUE DRIVERS (DERECHA)
        x = PDF_W - HORIZONTAL_LEFT_MARGIN - h
        self.image(BLUE_DRIVERS_LOGO, x, y, h=h)

    def set_header(self, title: str):
        self.set_xy(HORIZONTAL_LEFT_MARGIN, HEADER_TOP_MARGIN + 20)
        self.set_font(family=DEFAULT_FONT_FAMILY, size=16)
        self.set_text_color(46, 152, 209)  # azul

        title = f'{title} - [{self.month_label} - {self.year}]'
        self.multi_cell(WRITABLE_WIDTH, h=7, align='L', txt=title)

    def set_description(self, txt: str, y: int):
        # Definir posiciones
        h = 5  # Altura de celda. Mientras más altura más separación entre las líneas.
        x = HORIZONTAL_LEFT_MARGIN

        self.set_xy(x, y)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=10)
        self.set_text_color(0, 0, 0)  # negro
        self.multi_cell(WRITABLE_WIDTH, h, txt)

    def set_subtitle(self, txt: str, y: int):
        # Colocar el título en el pdf
        self.set_xy(HORIZONTAL_LEFT_MARGIN, y)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='B', size=12)
        self.set_text_color(46, 152, 209)  # azul
        w = self.get_string_width(txt)
        self.cell(w, h=5, align='L', txt=txt)

    def set_graph(self, title, description, filename, y):
        self.set_subtitle(title, y)
        # Colocar la imagen en el pdf. Estará centrada y con una anchura 4/6 del pdf.
        x = (1 / 6) * PDF_W
        y = y + 5

        image = Image.open(filename)
        width, height = image.size
        w = (4 / 6) * PDF_W
        h = height * w / width

        self.set_xy(x, y)
        self.image(filename, x, y, w, h)

        # Colocar la descripción de la imagen en el pdf.
        y_text = y + h
        self.set_fig_caption(description, y_text)

    def set_double_graph(self, title, description, filename1, filename2, y):
        self.set_subtitle(title, y)
        # Colocar la imagen en el pdf. Estará centrada y con una anchura 4/6 del pdf.
        x = HORIZONTAL_LEFT_MARGIN
        y = y + 5

        image1 = Image.open(filename1)
        image2 = Image.open(filename2)
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
        self.image(filename1, x, y, w, h)
        x = x + w + horizontal_sep_images
        self.image(filename2, x, y, w, h)

        # Colocar la descripción de la imagen en el pdf.
        y_text = y + h
        self.set_fig_caption(description, y_text)

    def set_fig_caption(self, txt: str, y: int):
        # Colocar la descripción de la imagen en el pdf.
        x = HORIZONTAL_LEFT_MARGIN
        self.set_xy(x, y)
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=10)
        self.set_text_color(0, 0, 0)  # negro
        self.multi_cell(WRITABLE_WIDTH, 5, txt, align='C')

    def footer(self) -> None:
        h = 12  # Logo
        x = HORIZONTAL_LEFT_MARGIN
        y = PDF_H - h - HEADER_TOP_MARGIN + 2
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=8)
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
        self.image(BLUE_DRIVERS_LOGO, x, y, h=h)

        # Set page number
        self.set_y(-15)
        self.set_font(DEFAULT_FONT_FAMILY, '', 8)
        self.cell(w=0, h=10, txt=str(self.page_no()), align='C')

    def add_default_font(self):
        fonts = BASE_DIR / 'shared/pdf/fonts/'
        self.add_font(family=DEFAULT_FONT_FAMILY, fname=fonts / 'Barlow-Regular.ttf', uni=True)
        self.add_font(family=DEFAULT_FONT_FAMILY, style='B', fname=fonts / 'Barlow-Bold.ttf', uni=True)
        self.add_font(family=DEFAULT_FONT_FAMILY, style='I', fname=fonts / 'Barlow-Italic.ttf', uni=True)
        self.add_font(family=DEFAULT_FONT_FAMILY, style='BI', fname=fonts / 'Barlow-BoldItalic.ttf', uni=True)
