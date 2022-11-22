from pyexpat import model
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import method_overridden
from .models import Client,Comptable,Concession,ServiceGestion
from agent.models import Agent
from django.contrib.auth.models import User

class RepresentationComptable(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "nom":value.nom_complet,
            "mobile": value.mobile,
            "email_envoi_facture":value.email_envoi_facture,
            "telephone":value.telephone,
            "id":value.id,
        }
        return result

class RepresentationServiceGestion(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "nom_complet":value.nom_complet,
            "mobile": value.mobile,
            "email":value.email,
            "telephone":value.telephone,
            "id":value.id
        }
        return result

class RepresentationConcession(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "agence_secteur_rattachement":value.agence_secteur_rattachement,
            "nom_concessionnaire":value.nom_concessionnaire,
            "numero_proposition_prestation":value.numero_proposition_prestation,
            "nom_complet":value.nom_complet,
            "as_client":value.as_client,
            "origine_client":value.origine_client,
            "suivie_technique_client":value.suivie_technique_client,
            
        }
        if value.agent_rattache is not None:
            result['agent_rattache'] = {
                "nom":value.agent_rattache.user.last_name,
                "prenom": value.agent_rattache.user.first_name,
                "email":value.agent_rattache.user.email,
                "trigramme":value.agent_rattache.trigramme,
                "id":value.agent_rattache.id,
                "user": value.agent_rattache.user.id,
                "secteur": value.agent_rattache.secteur_primaire,
                "secteur_secondaire": value.agent_rattache.secteur_secondaire
            }
        else:
            result['agent_rattache'] = None
        
        return result

class RepresentationUser(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "nom":value.last_name,
            "prenom": value.first_name,
            "email":value.email,
            "login":value.username,
            "id":value.id,
            "group":value.groups.all().first().name,
            "is_active":value.is_active
        }
        return result
        

class ClientSerializer(serializers.ModelSerializer):
    user = RepresentationUser(read_only=True,many=False)
    ref_comptable = RepresentationComptable(read_only=True,many=False)
    ref_service_gestion = RepresentationServiceGestion(read_only=True,many=False)
    info_concession = RepresentationConcession(read_only=True,many=False)
    class Meta:
        model= Client
        fields = '__all__'