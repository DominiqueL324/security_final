# Generated by Django 4.0.3 on 2022-04-21 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_client_statut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='statut',
            field=models.IntegerField(null=True, verbose_name='statut du client'),
        ),
    ]
