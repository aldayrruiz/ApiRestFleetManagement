# Generated by Django 4.0.5 on 2022-08-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0002_tenant_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='diet',
            field=models.BooleanField(default=False),
        ),
    ]