import email
from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from agent.models import Agent

class Comptable(models.Model):
    nom_complet = models.CharField("Nom Complet",max_length=100)
    email_envoi_facture = models.CharField("2mail d'nvoi de facture",max_length=80)
    telephone = models.CharField("Telephone ",max_length=50)
    mobile = models.CharField("Mobile ",max_length=50)
    def __str__(self):
        return self.nom_complet
        
    class Meta:
        verbose_name = "Reference comptable"

class ServiceGestion(models.Model):
    nom_complet = models.CharField("Nom Complet",max_length=100)
    email = models.CharField("Emailt",max_length=100)
    telephone = models.CharField("Telephone",max_length=100)
    mobile = models.CharField("Mobilet",max_length=100)

    def __str__(self):
        return self.nom_complet
        
    class Meta:
        verbose_name = "Reference service gestion"

class Concession(models.Model):
    agent_rattache = models.ForeignKey(Agent,on_delete=models.CASCADE,related_name="agent_rattachee")
    agence_secteur_rattachement = models.CharField("Agence du secteur de rattachement",max_length=100,null=True)
    nom_concessionnaire = models.CharField("Nom Complet",max_length=100,null=True)
    numero_proposition_prestation = models.CharField("Numéro de proposition de prestation",max_length=100,null=True)
    nom_complet = models.CharField("Nom Complet",max_length=100)
    as_client = models.CharField("AS client ",max_length=100,null=True)
    origine_client = models.CharField("Origine Client",max_length=100,null=True)
    suivie_technique_client = models.CharField("Nom Complet",max_length=100,null=True)

    def __str__(self):
        return self.nom_concessionnaire
        
    class Meta:
        verbose_name = "Information concession"

class Passeur(models.Model):
    nom_complet = models.CharField("Nom complet",max_length=100,null=True)
    emal = models.CharField("Email",max_length=100,null=True)
    telephone = models.CharField("Telephone",max_length=100,null=True)
    mobile = models.CharField("Mobile",max_length=100,null=True)
    fonction = models.CharField("Fonction",max_length=100)

    def __str__(self):
        return self.nom_complet
        
    class Meta:
        verbose_name = "Information Passeur"

class Client(models.Model): 
    statut = models.IntegerField("statut du client",null=True) 
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="client",null=True)
    adresse = models.CharField("Adresse",max_length=300,default=" ")
    titre = models.CharField("Totre",max_length=20,default="Mr")
    fonction = models.CharField("Fonction",max_length=30,default="Vide")
    societe = models.CharField("Societe",max_length=100,default="Vide")
    ref_societe = models.CharField("Référence de la société",max_length=100,null=True)
    email_agence = models.CharField("Email Agence",max_length=100,null=True)
    siret = models.CharField("SIRET",max_length=100,null=True)
    tva_intercommunautaire = models.CharField("TVA Intercommunautaire",max_length=100,null=True)
    complement_adresse = models.CharField("complement d'adresse",max_length=100,null=True)
    code_postal = models.CharField("Code postal",max_length=50,null=True)
    ville = models.CharField("Ville",max_length=80,default="Vide")
    telephone = models.CharField('Téléphone',max_length=20,null=True)
    mobile = models.CharField("Societe",max_length=20,null=True)
    telephone_agence = models.CharField("Telephone Agence",max_length=50,null=True)
    code_client = models.CharField("Code client",max_length=50,null=True)
    passeur = models.ForeignKey(Passeur,on_delete=models.CASCADE,related_name="passeurs_client",null=True)
    ref_comptable = models.OneToOneField(Comptable,on_delete=models.CASCADE,related_name="reference_comptable",null=True)
    ref_service_gestion = models.OneToOneField(ServiceGestion,on_delete=models.CASCADE,related_name="reference_service_gestion",null=True)
    info_concession = models.OneToOneField(Concession,on_delete=models.CASCADE,related_name="informations_concession",null=True)

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
        
    class Meta:
        verbose_name = "client"


