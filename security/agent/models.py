from re import M
from statistics import mode
from django.db import models
from django.contrib.auth.models import User


class Agent(models.Model):  
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name="agent")
    adresse = models.CharField("Adresse",max_length=300,null=True)
    trigramme = models.CharField('trigramme',max_length=40,null=True)
    telephone = models.CharField('telephone',max_length=40,null=True)
    created_at = models.DateTimeField("date de création",auto_now_add=False,null=True)
    updated_at = models.DateTimeField("date dernière modification",auto_now_add=False,null=True)
    secteur_primaire = models.CharField("secteur primaire",max_length=300,null=True)
    secteur_secondaire = models.CharField("secteur secondaire",max_length=300,null=True)
    agent_secteur = models.IntegerField('agent secteur',null=True)


    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
        
    class Meta:
        verbose_name = "agent"
 