import numpy as np


class FilterByConfiguration:

    def __init__(self, users, vehicles, x_axis):
        self.users = users
        self.vehicles = vehicles
        self.x_axis = x_axis
        self.users_labels = self.get_users_labels()
        self.vehicles_labels = self.get_vehicles_labels()

    def get_data(self):
        if self.x_axis == 'user':
            return self.users
        elif self.x_axis == 'vehicle':
            return self.vehicles
        else:
            raise ValueError(f'Invalid x_axis: {self.x_axis}')

    def get_labels(self):
        if self.x_axis == 'user':
            return self.users_labels
        elif self.x_axis == 'vehicle':
            return self.vehicles_labels
        else:
            raise ValueError(f'Invalid x_axis: {self.x_axis}')

    def filter(self, reservations, obj):
        if self.x_axis == 'user':
            return reservations.filter(owner=obj)
        elif self.x_axis == 'vehicle':
            return reservations.filter(vehicle=obj)
        else:
            raise ValueError(f'Invalid x_axis: {self.x_axis}')

    def get_vehicles_labels(self):
        labels = []
        for vehicle in self.vehicles:
            label = self.get_vehicle_label(vehicle)
            labels.append(label)
        return np.array(labels)

    def get_users_labels(self):
        labels = []
        for user in self.users:
            label = self.get_user_label(user)
            labels.append(label)
        return np.array(labels)

    @staticmethod
    def get_vehicle_label(vehicle):
        return f'{vehicle.number_plate}<br>{vehicle.model}'

    @staticmethod
    def get_user_label(user):
        return f'{user.fullname}'
