from applications.reports.services.pdf.charts.use_of_vehicles.real_use_of_vehicle import RealUseOfVehicleChart
from applications.reports.services.pdf.charts.use_of_vehicles.theoretical_use_of_vehicle import \
    TheoreticalUseOfVehicleChart
from applications.reports.services.pdf.charts.use_of_vehicles.use_of_vehicles import UseOfVehicleChart
from applications.reports.services.pdf.charts.vehicle_punctuality import PunctualityChart
from applications.reports.services.pdf.configuration.chart_configuration import HoursChartConfiguration


def get_use_by_vehicle_chart(tenant, month, year, conf: HoursChartConfiguration = None, by='vehicle'):
    theoretical = TheoreticalUseOfVehicleChart(tenant, month, year, hour_config=conf, by=by)
    punctuality = PunctualityChart(tenant, month, year, hour_config=conf, by=by)
    real = RealUseOfVehicleChart(tenant, month, year, theoretical, punctuality, hour_config=conf, by=by)
    use_of_vehicles = UseOfVehicleChart(tenant, month, year, theoretical, real, hour_config=conf, by=by)
    return use_of_vehicles
