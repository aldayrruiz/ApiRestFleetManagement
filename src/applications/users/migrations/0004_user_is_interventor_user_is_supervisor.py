# Generated by Django 4.0.5 on 2022-08-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_ble_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_interventor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_supervisor',
            field=models.BooleanField(default=False),
        ),
    ]
