import logging
from datetime import date, datetime, timedelta

import numpy as np

from applications.reservations.models import Reservation
from applications.reservations.services.validator import ReservationValidator

logger = logging.getLogger(__name__)


class RecurrentReservationCreator:
    def __init__(self, config):
        self.config = config

    def create(self):
        possible_successful_reservations = []
        possible_error_reservations = []

        start_reservations = self.get_start_reservations()
        end_reservations = self.get_end_reservations(start_reservations)
        time_reservations = zip(start_reservations, end_reservations)

        for (start_res, end_res) in time_reservations:
            [valid, reservation] = self.try_with(start_res, end_res, self.config.vehicles)
            if valid:
                possible_successful_reservations.append(reservation)
            else:
                possible_error_reservations.append(reservation)

        return [possible_successful_reservations, possible_error_reservations]

    def get_start_reservations(self):
        """
        Return an array which contains all start reservations dates.
        """
        start_reservation_datetime = datetime.combine(self.config.start, self.config.start_res)
        all_dates = np.arange(start_reservation_datetime, self.config.end, timedelta(days=1)).astype(date)
        start_reservations = self.__only_include_weekdays__(all_dates)
        return start_reservations

    def __only_include_weekdays__(self, dates):
        validator = np.array(list(map(lambda day: day.weekday() not in self.config.weekdays, dates)))
        dates_included = np.delete(dates, np.where(validator)).astype(datetime)
        return dates_included

    def get_end_reservations(self, start_reservations):
        """
        Return an array which contains all end reservations dates with the same size as start_reservations.
        Start reservations dates + end_res time will be used to calculate end reservations dates.
        :param start_reservations: array with reservations dates
        """
        start_delta = timedelta(hours=self.config.start_res.hour)
        end_delta = timedelta(hours=self.config.end_res.hour)
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

    def try_with(self, start_res, end_res, vehicles):
        """
        Validate the reservation with all vehicles that are passed. If reservation can be saved,
        it returns [True, reservation]. Otherwise, it returns [false, error_reservation].

        :param start_res: Start of reservation
        :param end_res: End of reservation
        :param vehicles: Vehicles ordered by user preference
        :return:
        """
        for vehicle in vehicles:
            reservation = self.get_reservation(start=start_res, end=end_res, vehicle=vehicle)
            is_valid = ReservationValidator(vehicle).is_reservation_valid(reservation)
            if is_valid:
                return [True, reservation]

        error_reservation = self.__get_fake_reservation__(start=start_res, end=end_res, vehicles=vehicles)
        return [False, error_reservation]

    def get_reservation(self, start, end, vehicle):
        return Reservation(
            title=self.config.title,
            description=self.config.description,
            start=start,
            end=end,
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
        return self.get_reservation(start, end, vehicles.first())
