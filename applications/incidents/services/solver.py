from applications.incidents.exceptions.incident_already_solved import IncidentAlreadySolvedError


class IncidentSolver:
    def __init__(self, incident):
        self.incident = incident

    def solve(self):
        if self.incident.solved:
            raise IncidentAlreadySolvedError()
        self.incident.solved = True
        self.incident.save()
        print('I would send email here :)')
