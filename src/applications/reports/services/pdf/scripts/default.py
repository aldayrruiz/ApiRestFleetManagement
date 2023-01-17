import logging
import os

from dateutil.relativedelta import relativedelta

from applications.reports.models import MonthlyReport
from applications.reports.services.emails.report import VehicleUseReportEmail
from applications.reports.services.pdf.charts.distance_max_average_speed import DistanceMaxAverageSpeedChart
from applications.reports.services.pdf.charts.fuel_consumed import FuelConsumedChart
from applications.reports.services.pdf.charts.use_without_reservation import UseWithoutReservationChart
from applications.reports.services.pdf.charts.vehicle_punctuality import PunctualityChart
from applications.reports.services.pdf.generators.default_generator import DefaultUseOfVehiclesReportPdf, \
    DefaultChartImages
from applications.reports.services.pdf.reports import ReportsPdfPath
from applications.reports.services.pdf.scripts.helpers import get_use_by_vehicle_chart
from applications.tenants.models import Tenant
from utils.dates import get_now_utc

logger = logging.getLogger(__name__)


# Main
now = get_now_utc()
previous_month = now - relativedelta(months=1)
month = previous_month.month
year = previous_month.year

tenants = Tenant.objects.exclude(name__in=['Pruebas Local', 'Pruebas BLUE', 'Fundación Intras'])

for tenant in tenants:
    if not os.path.exists(ReportsPdfPath.get_tenant(tenant)):
        os.mkdir(ReportsPdfPath.get_tenant(tenant))
        os.mkdir(ReportsPdfPath.get_graphs(tenant))

    logger.info('Generating image: DistanceMaxAverageSpeedChart')
    distance_max_average_speed_chart = DistanceMaxAverageSpeedChart(tenant, month, year, orientation='v')
    filename = ReportsPdfPath.get_graph(tenant, 'DistanceMaxAverageSpeedChart')
    distance_max_average_speed_chart.generate_images(filename)

    logger.info('Generating image: FuelConsumedChart')
    fuel_consumed_chart = FuelConsumedChart(tenant, month, year, distance_max_average_speed_chart, orientation='v')
    filename = ReportsPdfPath.get_graph(tenant, 'FuelConsumedChart')
    fuel_consumed_chart.generate_images(filename)

    logger.info('Generating image: PunctualityChart')
    punctuality_chart = PunctualityChart(tenant, month, year, orientation='v')
    filename = ReportsPdfPath.get_graph(tenant, 'PunctualityChart')
    punctuality_chart.generate_images(filename)

    logger.info('Generating image: UseWithoutReservationChart')
    use_of_vehicles_without_reservation_chart = UseWithoutReservationChart(tenant, month, year, orientation='v')
    filename = ReportsPdfPath.get_graph(tenant, 'UseWithoutReservationChart')
    use_of_vehicles_without_reservation_chart.generate_images(filename)

    logger.info('Generating image: UseOfVehicleChart')
    use_of_vehicles_by_vehicles_chart = get_use_by_vehicle_chart(tenant, month, year)
    filename = ReportsPdfPath.get_graph(tenant, 'UseOfVehicleByVehiclesChart')
    use_of_vehicles_by_vehicles_chart.generate_images(filename)

    chart_images = DefaultChartImages(
        distance_max_average_speed_images=distance_max_average_speed_chart.images,
        fuel_consumed_images=fuel_consumed_chart.images,
        punctuality_images=punctuality_chart.images,
        use_of_vehicles_without_reservation_images=use_of_vehicles_without_reservation_chart.images,
        use_of_vehicles_by_vehicles_images=use_of_vehicles_by_vehicles_chart.images,
    )
    pdf = DefaultUseOfVehiclesReportPdf(tenant, month, year, chart_images)
    pdf.generate()

    # If report is already generated delete pdf and update report
    report = MonthlyReport.objects.filter(tenant=tenant, month=month, year=year).first()
    if report:
        report.delete()

    path = ReportsPdfPath.get_pdf(tenant, month, year)
    pdf.output(path)

    # Guardar información sobre el pdf (localización y mes)
    report = MonthlyReport(pdf=path, month=month, year=year, tenant=tenant)
    report.save()

    sender = VehicleUseReportEmail(tenant, report)
    sender.send()

    logger.info('Pdf generated')
