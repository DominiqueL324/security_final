# Generated by Django 4.1.1 on 2022-09-14 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0006_remove_agent_actif'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='type',
            field=models.CharField(default='agent secteur', max_length=40, verbose_name="type d'agent"),
        ),
    ]
