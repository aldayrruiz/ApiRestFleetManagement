from applications.incidents.exceptions.incident_already_solved import IncidentAlreadySolvedError
from utils.email.incidents.solved import send_incident_was_solved_email


class IncidentSolver:
    def __init__(self, incident):
        self.incident = incident

    def solve(self, solver):
        if self.incident.solved:
            raise IncidentAlreadySolvedError()
        self.incident.solver = solver
        self.incident.solved = True
        self.incident.save()
        send_incident_was_solved_email(self.incident)
