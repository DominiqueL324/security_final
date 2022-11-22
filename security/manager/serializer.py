from pyexpat import model
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import method_overridden
from django.contrib.auth.models import User

class RepresentationGroup(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "group":value.name,
        }
        return result
        
class RepresentationClient(serializers.RelatedField):
    #je retourne juste l'attribut id de l'objet client
    #donc pas besoin de créer tout un objet JSON pour un seul attribut je le retourne directement
    def to_representation(self, value):
        result = {
            "id":value.id,
            "societe": value.societe,
        }
        return result

class RepresentationSalarie(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "id":value.id,
        }
        if value.client is not None:
            result['societe'] = value.client.societe
        else:
            result['societe'] = " "
        return result 

class RepresentationAgent(serializers.RelatedField):
    def to_representation(self, value):
        result = value.id
        return result

class RepresentationAdmin(serializers.RelatedField):
    def to_representation(self, value):
        result = value.id
        return result
class UserSerializer(serializers.ModelSerializer):
    groups = RepresentationGroup(read_only=True,many=True)
    client = RepresentationClient(read_only=True,many=False)
    agent = RepresentationAgent(read_only=True,many=False)
    salarie = RepresentationSalarie(read_only=True,many=False)
    administrateur = RepresentationAdmin(read_only=True,many=False)
    class Meta:
        model= User
        fields = '__all__'
