import logging
import os

from dateutil.relativedelta import relativedelta

from applications.reports.models import MonthlyReport
from applications.reports.services.emails.report import VehicleUseReportEmail
from applications.reports.services.pdf.charts.distance_max_average_speed import DistanceMaxAverageSpeedChart
from applications.reports.services.pdf.charts.fuel_consumed import FuelConsumedChart
from applications.reports.services.pdf.charts.use_without_reservation import UseWithoutReservationChart
from applications.reports.services.pdf.charts.vehicle_punctuality import PunctualityChart
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration
from applications.reports.services.pdf.generators.intras_generator import IntrasUseOfVehiclesReportPdf, \
    IntrasChartImages
from applications.reports.services.pdf.reports import ReportsPdfPath
from applications.reports.services.pdf.scripts.helpers import get_use_by_vehicle_chart
from applications.tenants.models import Tenant
from utils.dates import get_now_utc, get_number_of_days_in_month

logger = logging.getLogger(__name__)

# Main
now = get_now_utc()
previous_month = now - relativedelta(months=1)
month = previous_month.month
year = previous_month.year

workdays_per_month = get_number_of_days_in_month(month, year)

tenant = Tenant.objects.get(name='Fundación Intras')

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

logger.info('Generating image: UseOfVehicleByVehiclesMorningChart')
morning_configuration = HoursChartConfiguration(True, 8, 15, workdays_per_month=workdays_per_month)
use_of_vehicles_by_vehicles_morning_chart = get_use_by_vehicle_chart(tenant, month, year, morning_configuration)
filename = ReportsPdfPath.get_graph(tenant, 'UseOfVehicleByVehiclesMorningChart')
use_of_vehicles_by_vehicles_morning_chart.generate_images(filename)

logger.info('Generating image: UseOfVehicleByVehiclesAfternoonChart')
afternoon_configuration = HoursChartConfiguration(True, 15, 22, workdays_per_month=workdays_per_month)
use_of_vehicles_by_vehicles_afternoon_chart = get_use_by_vehicle_chart(tenant, month, year, afternoon_configuration)
filename = ReportsPdfPath.get_graph(tenant, 'UseOfVehicleByVehiclesAfternoonChart')
use_of_vehicles_by_vehicles_afternoon_chart.generate_images(filename)
#
logger.info('Generating image: UseOfVehicleByUsersChart')
workdays_per_month = get_number_of_days_in_month(month, year)
by_user_config = HoursChartConfiguration(False, working_hours_per_day=14, workdays_per_month=workdays_per_month)
use_of_vehicles_by_users_chart = get_use_by_vehicle_chart(tenant, month, year, by_user_config, 'user')
filename = ReportsPdfPath.get_graph(tenant, 'UseOfVehicleByUsersChart')
use_of_vehicles_by_users_chart.generate_images(filename)

image_charts = IntrasChartImages(distance_max_average_speed_images=distance_max_average_speed_chart.images,
                                 fuel_consumed_images=fuel_consumed_chart.images,
                                 punctuality_images=punctuality_chart.images,
                                 use_of_vehicles_without_reservation_images=use_of_vehicles_without_reservation_chart.images,
                                 use_of_vehicles_by_vehicle_morning_images=use_of_vehicles_by_vehicles_morning_chart.images,
                                 use_of_vehicles_by_vehicle_afternoon_images=use_of_vehicles_by_vehicles_afternoon_chart.images,
                                 use_of_vehicles_by_user_images=use_of_vehicles_by_users_chart.images)

pdf = IntrasUseOfVehiclesReportPdf(tenant, month, year, image_charts)
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

# # Guardar información sobre las estadísticas del mes para luego obtener la del año.
# distances, max_speeds, average_speeds = chart1.get_stats()
# th_reserved_hours, th_free_hours = chart2.get_stats()
# re_reserved_hours, re_free_hours = chart3.get_stats()
# takes_out, takes_in, not_taken, frees_out, frees_in = chart4.get_stats()
# hours = chart5.get_stats()
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
#     rep2 = TheoreticalUseOfVehicleReport(
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
#     rep3 = RealUseOfVehicleReport(
#         hours=re_reserved_hours[i],
#         monthly_report=report,
#         vehicle=vehicle,
#         tenant=tenant
#     )
#
#     rep5 = UseWithoutReservation(
#         hours=hours[i],
#         monthly_report=report,
#         vehicle=vehicle,
#         tenant=tenant
#     )
#
#     rep1.save()
#     rep2.save()
#     rep3.save()
#     rep4.save()
#     rep5.save()

logger.info('Pdf generated')
