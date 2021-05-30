class AllowedVehicleUpdater:

    def __init__(self, user):
        self.user = user

    def update_allowed_vehicles(self, vehicles):
        self.user.allowed_vehicles.set(vehicles)
