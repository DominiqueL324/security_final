# Generated by Django 4.0.3 on 2022-07-25 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salarie', '0002_salarie_agent_rattache_salarie_fonction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='salarie',
            name='actif',
            field=models.CharField(default='oui', max_length=5, verbose_name='Actif'),
        ),
    ]