from re import M
from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime,time,timedelta

class Administrateur(models.Model):  
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name="administrateur")
    adresse = models.CharField("Adresse",max_length=300,null=True)
    telephone = models.CharField('Téléphone', max_length=30,null=True)
    created_at = models.DateTimeField('Date de création', auto_now_add=True,null=True)
    updated_at = models.DateTimeField('Dernièrre modification',auto_now_add=False,null=True)

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
        
    class Meta:
        verbose_name = "administrateur"