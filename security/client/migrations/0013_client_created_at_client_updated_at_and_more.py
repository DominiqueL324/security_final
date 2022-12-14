# Generated by Django 4.1.1 on 2022-09-25 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0008_remove_agent_type'),
        ('client', '0012_alter_client_adresse_alter_client_fonction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='created_at',
            field=models.DateTimeField(null=True, verbose_name='Date ajout'),
        ),
        migrations.AddField(
            model_name='client',
            name='updated_at',
            field=models.DateTimeField(null=True, verbose_name='Date ajout'),
        ),
        migrations.AlterField(
            model_name='client',
            name='type',
            field=models.CharField(default='particulier', max_length=30, null=True, verbose_name='Type de client'),
        ),
        migrations.AlterField(
            model_name='comptable',
            name='email_envoi_facture',
            field=models.CharField(max_length=80, null=True, verbose_name="2mail d'nvoi de facture"),
        ),
        migrations.AlterField(
            model_name='comptable',
            name='mobile',
            field=models.CharField(max_length=50, null=True, verbose_name='Mobile '),
        ),
        migrations.AlterField(
            model_name='comptable',
            name='nom_complet',
            field=models.CharField(max_length=100, null=True, verbose_name='Nom Complet'),
        ),
        migrations.AlterField(
            model_name='comptable',
            name='telephone',
            field=models.CharField(max_length=50, null=True, verbose_name='Telephone '),
        ),
        migrations.AlterField(
            model_name='concession',
            name='agent_rattache',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agent_rattachee', to='agent.agent'),
        ),
        migrations.AlterField(
            model_name='concession',
            name='nom_complet',
            field=models.CharField(max_length=100, null=True, verbose_name='Nom Complet'),
        ),
        migrations.AlterField(
            model_name='servicegestion',
            name='email',
            field=models.CharField(max_length=100, null=True, verbose_name='Emailt'),
        ),
        migrations.AlterField(
            model_name='servicegestion',
            name='mobile',
            field=models.CharField(max_length=100, null=True, verbose_name='Mobilet'),
        ),
        migrations.AlterField(
            model_name='servicegestion',
            name='nom_complet',
            field=models.CharField(max_length=100, null=True, verbose_name='Nom Complet'),
        ),
        migrations.AlterField(
            model_name='servicegestion',
            name='telephone',
            field=models.CharField(max_length=100, null=True, verbose_name='Telephone'),
        ),
    ]
