import logging
from datetime import date, datetime, timedelta

import numpy as np

from applications.reservations.models import Reservation
from applications.reservations.services.queryset import get_future_reservations_of
from applications.reservations.services.recurrent.recurrent_config import RecurrentConfiguration
from applications.reservations.services.validator import ReservationValidator
from utils.dates import from_naive_to_aware

logger = logging.getLogger(__name__)


class RecurrentReservationCreator:
    def __init__(self, config: RecurrentConfiguration):
        self.config = config
        self.my_future_reservations = get_future_reservations_of(self.config.owner)

    def try_create(self):
        successful_reservations = []
        error_reservations = []

        starts = self.__get_start_reservations__()
        ends = self.__get_end_reservations__(starts)
        date_times = zip(starts, ends)

        for (start, end) in date_times:
            [valid, reservation] = self.__try_with__(start, end, self.config.vehicles)
            if valid:
                successful_reservations.append(reservation)
            else:
                error_reservations.append(reservation)

        return [successful_reservations, error_reservations]

    def __get_start_reservations__(self) -> np.ndarray:
        """
        Return an array which contains all start reservations dates.
        """
        start = datetime.combine(self.config.recurrent.since, self.config.start_time)
        end = datetime.combine(self.config.recurrent.until, self.config.end_time)
        # All Days from one date to another.
        all_dates = np.arange(start, end, timedelta(days=1)).astype(date)
        all_dates = np.array([from_naive_to_aware(d) for d in all_dates])
        # Filter them to just include weekdays selected by user.
        starts = self.__only_weekdays__(all_dates)
        return starts

    def __only_weekdays__(self, dates: np.ndarray):
        weekdays = self.__get_weekdays__()
        validator = np.array(list(map(lambda day: day.weekday() not in weekdays, dates)))
        dates_included = np.delete(dates, np.where(validator)).astype(datetime)
        return dates_included

    def __get_weekdays__(self):
        weekdays = self.config.recurrent.weekdays.split(',')
        weekdays = list(map(int, weekdays))
        return weekdays

    def __get_end_reservations__(self, start_reservations: np.ndarray):
        """
        Return an array which contains all end reservations dates with the same size as start_reservations.
        Start reservations dates + end_res time will be used to calculate end reservations dates.
        :param start_reservations: array with reservations dates
        """
        start_delta = timedelta(hours=self.config.start_time.hour)
        end_delta = timedelta(hours=self.config.end_time.hour)
        diff = start_delta - end_delta
        if diff.total_seconds() > 0:
            # Reservations ends the next day
            sum_diff = timedelta(days=1) - diff
            end_reservations = np.copy(start_reservations) + sum_diff
            return end_reservations
        else:
            # Reservations ends the same day
            end_reservations = np.copy(start_reservations) - diff
            return end_reservations

    def __try_with__(self, start, end, vehicles):
        """
        Validate the reservation with all vehicles that are passed. If reservation can be saved,
        it returns [True, reservation]. Otherwise, it returns [false, error_reservation].
        :param start: Start of reservation
        :param end: End of reservation
        :param vehicles: Vehicles ordered by user preference
        :return:
        """

        for vehicle in vehicles:
            reservation = self.__get_reservation__(start=start, end=end, vehicle=vehicle)
            [is_valid, r_conflict] = ReservationValidator(vehicle, self.config.owner).is_reservation_valid(reservation)
            if is_valid:
                return [True, reservation]
        error_reservation = self.__get_fake_reservation__(start=start, end=end, vehicles=vehicles)
        return [False, error_reservation]

    def __get_reservation__(self, start, end, vehicle):
        return Reservation(
            title=self.config.title,
            description=self.config.description,
            start=start,
            end=end,
            recurrent=self.config.recurrent,
            owner=self.config.owner,
            vehicle=vehicle
        )

    def __get_fake_reservation__(self, start, end, vehicles):
        """
        Returns a fake reservation that cannot be saved. But it is useful to know what reservation failed.

        :param start: Start reservation.
        :param end: End reservation.
        :param vehicles: queryset of vehicles.
        :return: Reservation that should not be saved.
        """
        return self.__get_reservation__(start, end, vehicles.first())

    @staticmethod
    def create(valid_reservations, tenant):
        for reservation in valid_reservations:
            reservation.is_recurrent = True
            reservation.tenant = tenant
            reservation.save()
