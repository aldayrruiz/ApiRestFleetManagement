import logging
import os

from dateutil.relativedelta import relativedelta

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
    path = ReportsPdfPath.get_pdf(tenant, month, year)
    pdf.output(path)

    # Guardar información sobre el pdf (localización y mes)
    # report = MonthlyReport(pdf=path, month=month, year=year, tenant=tenant)
    # report.save()
    #
    # # Guardar información sobre las estadísticas del mes para luego obtener la del año.
    # distances, max_speeds, average_speeds = chart1.get_stats()
    # th_reserved_hours, th_free_hours = chart3.get_stats()
    # re_reserved_hours, re_free_hours = chart4.get_stats()
    # takes_out, takes_in, not_taken, frees_out, frees_in = chart5.get_stats()
    # hours = chart6.get_stats()
    #
    # vehicles = chart1.vehicles
    # for i, vehicle in enumerate(vehicles):
    #     rep1 = DistanceMaxAverageReport(
    #         distance=distances[i],
    #         max_speed=max_speeds[i],
    #         average_speed=average_speeds[i],
    #         monthly_report=report,
    #         vehicle=vehicle,
    #         tenant=tenant
    #     )
    #
    #     rep3 = TheoreticalUseOfVehicleReport(
    #         hours=th_reserved_hours[i],
    #         monthly_report=report,
    #         vehicle=vehicle,
    #         tenant=tenant
    #     )
    #
    #     rep4 = PunctualityReport(
    #         take_out=takes_out[i],
    #         take_in=takes_in[i],
    #         free_in=frees_in[i],
    #         free_out=frees_out[i],
    #         not_taken=not_taken[i],
    #         monthly_report=report,
    #         vehicle=vehicle,
    #         tenant=tenant
    #     )
    #
    #     rep5 = RealUseOfVehicleReport(
    #         hours=re_reserved_hours[i],
    #         monthly_report=report,
    #         vehicle=vehicle,
    #         tenant=tenant
    #     )
    #
    #     rep6 = UseWithoutReservation(
    #         hours=hours[i],
    #         monthly_report=report,
    #         vehicle=vehicle,
    #         tenant=tenant
    #     )
    #
    #     rep1.save()
    #     rep3.save()
    #     rep4.save()
    #     rep5.save()
    #     rep6.save()

    logger.info('Pdf generated')