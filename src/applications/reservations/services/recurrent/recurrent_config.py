from operator import itemgetter

from rest_framework.exceptions import PermissionDenied

from applications.allowed_vehicles.services.queryset import get_vehicles_ordered_by_ids


class RecurrentConfiguration:
    def __init__(self, title, description, start_time, end_time, vehicles, recurrent, owner):
        self.title = title
        self.description = description
        self.start_time = start_time.timetz()
        self.end_time = end_time.timetz()
        self.vehicles = vehicles
        self.recurrent = recurrent
        self.owner = owner

    @staticmethod
    def from_serializer(serializer, owner):
        # Just taking all variables from body request
        (
            title,
            description,
            startTime,
            endTime,
            recurrent,
            vehicles_ids
        ) = itemgetter('title',
                       'description',
                       'startTime',
                       'endTime',
                       'recurrent',
                       'vehicles')(serializer.validated_data)

        if not (owner == recurrent.owner):
            raise PermissionDenied('You must be owner of recurrent data.')

        # Get vehicles ordered by user preference
        vehicles = get_vehicles_ordered_by_ids(vehicles_ids, owner)

        return RecurrentConfiguration(
            title=title,
            description=description,
            start_time=startTime,
            end_time=endTime,
            vehicles=vehicles,
            recurrent=recurrent,
            owner=owner
        )
