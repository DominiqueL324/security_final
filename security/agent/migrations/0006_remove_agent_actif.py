# Generated by Django 4.0.3 on 2022-07-25 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0005_agent_actif'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='actif',
        ),
    ]
