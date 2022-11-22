import imp
from re import M
from statistics import mode
from django.db import models
from agent.models import Agent
from client.models import Client
from django.contrib.auth.models import User


class Salarie(models.Model):  
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name="salarie")
    adresse = models.CharField("Adresse",max_length=300,null=True)
    titre = models.CharField("Titre",max_length=300,null=False,default="")
    fonction = models.CharField("Fonction",max_length=300,null=False,default="")
    company = models.CharField('companie', max_length=50, null=True)
    code = models.CharField('code', max_length=50, null=True)
    telephone = models.CharField('Téléphone', max_length=20, null=True)
    mobile = models.CharField('Mobile', max_length=20,null=True)
    client = models.ForeignKey(Client,on_delete=models.CASCADE,related_name="client_pro_rattache",null=True)
    agent_rattache = models.ForeignKey(Agent,on_delete=models.CASCADE,related_name="agent_rattache",null=True)
    created_at = models.DateTimeField("Date création",auto_now_add=False,null=True)
    updated_at = models.DateTimeField("Date modification",auto_now_add=False,null=True)

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
        
    class Meta:
        verbose_name = "salarie"