from pyexpat import model
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import method_overridden
from .models import Salarie
from agent.models import Agent
from django.contrib.auth.models import User

class RepresentationUser(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "nom":value.last_name,
            "prenom": value.first_name,
            "email":value.email,
            "login":value.username,
            "id":value.id,
            "group":value.groups.all().first().name,
        }
        return result

class RepresentationAgent(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "user":{
                "nom":value.user.last_name,
                "prenom": value.user.first_name,
                "email":value.user.email,
                "login":value.user.username,
                "id":value.user.id
            },
            "trigramme":value.trigramme,
            "id":value.id,
        }
        return result

class SalarieSerializer(serializers.ModelSerializer):
    user = RepresentationUser(read_only=True,many=False)
    agent_rattache = RepresentationAgent(read_only=True,many=False)
    class Meta:
        model= Salarie
        fields = '__all__'