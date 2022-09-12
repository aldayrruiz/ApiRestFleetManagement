from applications.diets.models import DietType
from applications.diets.models.diet import DietCollection, Diet
from utils.email.shared import EmailSender
from decouple import config
from django.template.loader import render_to_string

diet_collection_was_completed_body = """Se ha completado una dieta.

Dieta:
{diets_body}
Creador:
    Nombre completo: {fullname}
    Email: {email}
"""


common_diet_body = """{i}.
    Tipo: {type} €
    Importe: {amount}
    Descripción: {description}
    Imágenes: {images}
"""

gasolina_diet_body = """{i}.
    Tipo: {type}
    Importe: {amount} €
    Litros: {liters}
    Descripción: {description}
    Imágenes: {images}
"""

images_diet_body = """
        - {baseurl}{url}
"""


class DietCompletedEmail(EmailSender):

    def __init__(self, collection: DietCollection):
        self.collection = collection
        self.subject = 'Dieta completada'
        self.diets = collection.diets.all()
        self.body = self.get_body()
        supervisors = self.get_supervisors()
        super().__init__(supervisors, self.subject)

    def get_supervisors(self):
        supervisors = self.collection.tenant.users.filter(is_supervisor=True)
        emails = list(map(lambda supervisor: supervisor.email, supervisors))
        emails = ', '.join(emails)
        return emails

    def get_body(self):
        # body = diet_collection_was_completed_body.format(
        #     diets_body=self.get_diets_body(),
        #     fullname=self.collection.owner.fullname,
        #     email=self.collection.owner.email
        # )
        # return body
        body = render_to_string(
            'index.html',
            {'collection': self.collection,
             'owner': self.collection.owner,
             'baseurl': config('SERVER_URL')
             })
        return body

    def get_diets_body(self):
        body = ''
        for i, diet in enumerate(self.collection.diets.all()):
            if diet.type == DietType.Gasolina:
                body += gasolina_diet_body.format(
                    i=i+1,
                    type=diet.type,
                    amount=diet.amount,
                    liters=diet.liters,
                    description=diet.description,
                    images=self.get_images_body(diet)
                )
            else:
                body += common_diet_body.format(
                    i=i+1,
                    type=diet.type,
                    amount=diet.amount,
                    description=diet.description,
                    images=self.get_images_body(diet)
                )
        return body

    def get_images_body(self, diet: Diet):
        body = ''
        for image in diet.photos.all():
            body += images_diet_body.format(baseurl=config('SERVER_URL'), url=image.photo.url)
        return body

    def send(self):
        self.attach_html(self.body)
        super().send()
