from pyexpat import model
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import method_overridden
from .models import Agent
from django.contrib.auth.models import User

class RepresentationUser(serializers.RelatedField):
    def to_representation(self, value):
        result = {
            "nom":value.last_name,
            "prenom": value.first_name,
            "email":value.email,
            "login":value.username,
            "id":value.id,
            "is_active":value.is_active,
            "group":value.groups.all().first().name,
        }
        return result

class RepresentationAs(serializers.RelatedField):
    def to_representation(self, value):
        age = Agent.objects.filter(pk=int(value)).first()
        result = {}
        if age is not None:
            result = {
                "nom":age.user.last_name,
                "prenom": age.user.first_name,
                "email":age.user.email,
                "id_user":age.user.id,
                "id":age.id,
            }
        else:
            result={
                "agent_id":value
            }
        return result

class AgentSerializer(serializers.ModelSerializer):
    user = RepresentationUser(read_only=True,many=False)
    agent_secteur = RepresentationAs(read_only=True,many=False)
    class Meta:
        model= Agent
        fields = '__all__'