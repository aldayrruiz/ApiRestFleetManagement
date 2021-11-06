from django.contrib.auth import get_user_model


def delete_if_fake_user_already_exists(serializer):
    user_with_same_email_and_fake = __get_user_with_same_email_and_fake__(serializer)
    if user_with_same_email_and_fake:
        user_with_same_email_and_fake.delete()


def __get_user_with_same_email_and_fake__(serializer):
    # TODO: Update this to get email from fake Tenant
    email = serializer.initial_data['email']
    return get_user_model().objects.filter(email=email).first()
