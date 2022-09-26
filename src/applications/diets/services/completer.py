from applications.diets.exceptions.completed_diet import CompletedDietError
from applications.diets.serializers.update import PatchDietSerializer
from applications.diets.services.emails.supervisor import DietCompletedSupervisorEmail


class DietUpdater:
    def __init__(self, diet, data, requester):
        self.diet = diet
        self.data = data
        self.requester = requester

    def update(self):
        self.raise_error_if_diet_already_completed()
        self.diet.modified = True
        serializer = PatchDietSerializer(self.diet, data=self.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.send_email()
        return serializer

    def send_email(self):
        if self.diet.completed:
            sender = DietCompletedSupervisorEmail(self.diet)
            sender.send()

    def raise_error_if_diet_already_completed(self):
        if self.diet.completed:
            raise CompletedDietError()

