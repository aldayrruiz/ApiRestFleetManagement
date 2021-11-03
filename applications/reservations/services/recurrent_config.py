from operator import itemgetter

from applications.allowed_vehicles.services import get_vehicles_ordered_by_ids


class RecurrentConfiguration:
    def __init__(self, title, description, start, end, start_res, end_res, vehicles, weekdays, owner):
        self.title = title
        self.description = description
        self.start = start
        self.end = end
        self.start_res = start_res.timetz()
        self.end_res = end_res.timetz()
        self.vehicles = vehicles
        self.weekdays = weekdays
        self.owner = owner

    @staticmethod
    def from_serializer(serializer, owner):
        # Just taking all variables from body request
        (
            title,
            description,
            start,
            end,
            start_res,
            end_res,
            weekdays,
            vehicles_ids
        ) = itemgetter('title',
                       'description',
                       'startReservations',
                       'endReservations',
                       'startReservationTime',
                       'endReservationTime',
                       'weekdays',
                       'vehicles')(serializer.validated_data)

        # Get vehicles ordered by user preference
        vehicles = get_vehicles_ordered_by_ids(vehicles_ids, owner)

        return RecurrentConfiguration(
            title=title,
            description=description,
            start=start,
            end=end,
            start_res=start_res,
            end_res=end_res,
            vehicles=vehicles,
            weekdays=weekdays,
            owner=owner
        )
