from rest_framework.exceptions import ValidationError


class IncidentSolver():
    def __init__(self, incident):
        self.incident = incident

    def solve(self):
        if self.incident.solved:
            raise ValidationError('Incident is already solved')
        self.incident.solved = True
        self.incident.save()
        print('I would send email here :)')



