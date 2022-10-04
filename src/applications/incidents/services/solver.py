from applications.incidents.exceptions.incident_already_solved import IncidentAlreadySolvedError
from applications.incidents.services.emails.solved import IncidentSolvedEmail


class IncidentSolver:
    def __init__(self, incident):
        self.incident = incident

    def solve(self, solver):
        if self.incident.solved:
            raise IncidentAlreadySolvedError()
        self.incident.solver = solver
        self.incident.solved = True
        self.incident.save()
        IncidentSolvedEmail(self.incident).send()
