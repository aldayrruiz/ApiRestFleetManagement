from operator import itemgetter

from rest_framework.exceptions import PermissionDenied

from applications.allowed_vehicles.services.queryset import get_vehicles_ordered_by_ids


class RecurrentConfiguration:
    def __init__(self, title, description, start_time, end_time, vehicles, recurrent, owner, is_driver_needed):
        self.title = title
        self.description = description
        self.start_time = start_time.timetz()
        self.end_time = end_time.timetz()
        self.vehicles = vehicles
        self.recurrent = recurrent
        self.owner = owner
        self.is_driver_needed = is_driver_needed

    @staticmethod
    def from_serializer(serializer, owner):
        # Just taking all variables from body request
        (
            title,
            description,
            startTime,
            endTime,
            recurrent,
            vehicles_ids,
            is_driver_needed,
        ) = itemgetter('title',
                       'description',
                       'startTime',
                       'endTime',
                       'recurrent',
                       'vehicles',
                       'is_driver_needed')(serializer.validated_data)

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
            owner=owner,
            is_driver_needed=is_driver_needed
        )
