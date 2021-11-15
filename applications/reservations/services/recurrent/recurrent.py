import logging
import uuid
from datetime import date, datetime, timedelta

import numpy as np

from applications.reservations.models import Reservation
from applications.reservations.services.validator import ReservationValidator
from utils.dates import from_naive_to_aware

logger = logging.getLogger(__name__)


class RecurrentReservationCreator:
    def __init__(self, config):
        self.config = config

    def try_create(self):
        possible_successful_reservations = []
        possible_error_reservations = []

        start_reservations = self.__get_start_reservations__()
        end_reservations = self.__get_end_reservations__(start_reservations)
        time_reservations = zip(start_reservations, end_reservations)

        for (start_res, end_res) in time_reservations:
            [valid, reservation] = self.__try_with__(start_res, end_res, self.config.vehicles)
            if valid:
                possible_successful_reservations.append(reservation)
            else:
                possible_error_reservations.append(reservation)

        return [possible_successful_reservations, possible_error_reservations]

    def __get_start_reservations__(self):
        """
        Return an array which contains all start reservations dates.
        """
        start_reservation_datetime = datetime.combine(self.config.start, self.config.start_res)
        end_reservation_datetime = datetime.combine(self.config.end, self.config.end_res)
        all_dates = np.arange(start_reservation_datetime, end_reservation_datetime, timedelta(days=1)).astype(date)
        all_dates = np.array([from_naive_to_aware(d) for d in all_dates])
        start_reservations = self.__only_include_weekdays__(all_dates)
        return start_reservations

    def __only_include_weekdays__(self, dates):
        validator = np.array(list(map(lambda day: day.weekday() not in self.config.weekdays, dates)))
        dates_included = np.delete(dates, np.where(validator)).astype(datetime)
        return dates_included

    def __get_end_reservations__(self, start_reservations):
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

    def __try_with__(self, start_res, end_res, vehicles):
        """
        Validate the reservation with all vehicles that are passed. If reservation can be saved,
        it returns [True, reservation]. Otherwise, it returns [false, error_reservation].

        :param start_res: Start of reservation
        :param end_res: End of reservation
        :param vehicles: Vehicles ordered by user preference
        :return:
        """
        for vehicle in vehicles:
            reservation = self.__get_reservation__(start=start_res, end=end_res, vehicle=vehicle)
            is_valid = ReservationValidator(vehicle).is_reservation_valid(reservation)
            if is_valid:
                return [True, reservation]

        error_reservation = self.__get_fake_reservation__(start=start_res, end=end_res, vehicles=vehicles)
        return [False, error_reservation]

    def __get_reservation__(self, start, end, vehicle):
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
        return self.__get_reservation__(start, end, vehicles.first())

    @staticmethod
    def create(valid_reservations, tenant):
        recurrent_uuid = uuid.uuid4()

        for reservation in valid_reservations:
            reservation.recurrent_id = recurrent_uuid
            reservation.is_recurrent = True
            reservation.tenant = tenant
            reservation.save()
