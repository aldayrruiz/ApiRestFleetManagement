class HoursChartConfiguration:
    """
    This class is used to configure the chart. The reservations which started between start_hour and end_hour will be
    considered. Other reservations will be ignored. It's also possible to configure the number of workdays.

    Motivation for this class:
    The company Intras consider morning shift from 8:00 to 15:00 and afternoon shift from 15:00 to 22:00.
    But also, they consider 7 workdays per week.

    Hours must be in Europe/Madrid timezone. Basically if you want to filter only reservations from 8:00 to 20:00, you
    must pass 8 and 20 as parameters.

    :param ranged_hours: If True, only reservations which started between start_hour and end_hour will be considered.
    :param start_hour: Start hour of the range. Must be between 0 and 23.
    :param end_hour: End hour of the range. Must be between 0 and 23.
    :param working_hours_per_day: Number of working hours per day. Must be between 0 and 24.
    :param workdays_per_month: Number of workdays per month. Must be between 0 and 31.
    """
    def __init__(self, ranged_hours: bool, start_hour: int = 0, end_hour: int = 0,
                 working_hours_per_day: int = 5, workdays_per_month: int = 22):
        self.ranged_hours = ranged_hours
        self.start_hour = start_hour
        self.end_hour = end_hour
        if ranged_hours:
            self.working_hours_per_day = end_hour - start_hour
        else:
            self.working_hours_per_day = working_hours_per_day
        self.workdays_per_month = workdays_per_month

    def get_hours_per_month(self):
        if self.ranged_hours:
            return (self.end_hour - self.start_hour) * self.workdays_per_month
        else:
            return self.working_hours_per_day * self.workdays_per_month
