def update_allowed_vehicles(user, vehicles):
    user.allowed_vehicles.set(vehicles)
