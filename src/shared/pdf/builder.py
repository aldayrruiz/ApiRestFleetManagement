import calendar
import locale

from fpdf import FPDF

from applications.tenants.models import Tenant
from fleet_management.settings.base import BASE_DIR
from applications.reports.generate.reports import ReportsPdfPath
from shared.pdf.constants import HORIZONTAL_LEFT_MARGIN, HEADER_TOP_MARGIN, PDF_W, DEFAULT_FONT_FAMILY, WRITABLE_WIDTH, PDF_H


LOGOS = {
    'Local': ReportsPdfPath.get_logo('Intras.png'),
    'Intras': ReportsPdfPath.get_logo('Intras.png'),
    'SaCyL': ReportsPdfPath.get_logo('SACYL.png'),
    'BLUE Drivers': ReportsPdfPath.get_logo('BLUEDrivers.png')
}


class PdfBuilder(FPDF):
    def __init__(self, tenant: Tenant, month: int, year: int):
        super().__init__()
        self.tenant = tenant
        self.month = month
        self.year = year
        self.logo_tenant = LOGOS[tenant.short_name]
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
        self.image(LOGOS['BLUE Drivers'], x, y, h=h)

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
        self.set_font(family=DEFAULT_FONT_FAMILY, style='', size=12)
        self.set_text_color(46, 152, 209)  # azul
        w = self.get_string_width(txt)
        self.cell(w, h=5, align='L', txt=txt)

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
        self.image(LOGOS['BLUE Drivers'], x, y, h=h)

        # Set page number
        self.set_y(-15)
        self.set_font(DEFAULT_FONT_FAMILY, '', 8)
        self.cell(w=0, h=10, txt=str(self.page_no()), align='C')

    def add_default_font(self):
        self.add_font(family=DEFAULT_FONT_FAMILY, fname=BASE_DIR / 'shared/pdf/fonts/DejaVuSansCondensed.ttf', uni=True)
        self.add_font(family=DEFAULT_FONT_FAMILY, style='B', fname=BASE_DIR / 'shared/pdf/fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
        self.add_font(family=DEFAULT_FONT_FAMILY, style='I', fname=BASE_DIR / 'shared/pdf/fonts/DejaVuSansCondensed-Oblique.ttf', uni=True)
        self.add_font(family=DEFAULT_FONT_FAMILY, style='BI', fname=BASE_DIR / 'shared/pdf/fonts/DejaVuSansCondensed-BoldOblique.ttf', uni=True)
