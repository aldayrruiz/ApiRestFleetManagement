from applications.diets.exceptions.completed_collection import CompletedDietCollectionError
from applications.diets.serializers.update import PatchDietCollectionSerializer
from applications.diets.services.emails.completed import DietCompletedEmail



class DietCollectionUpdater:
    def __init__(self, collection, data, requester):
        self.collection = collection
        self.data = data
        self.requester = requester

    def update(self):
        self.raise_error_if_diet_already_completed()
        self.collection.modified = True
        serializer = PatchDietCollectionSerializer(self.collection, data=self.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.send_email()
        return serializer

    def send_email(self):
        if self.collection.completed:
            sender = DietCompletedEmail(self.collection)
            sender.send()

    def raise_error_if_diet_already_completed(self):
        if self.collection.completed:
            raise CompletedDietCollectionError()

