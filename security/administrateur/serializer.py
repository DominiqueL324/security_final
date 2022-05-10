from pyexpat import model
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import method_overridden
from .models import Administrateur
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
class AdministrateurSerializer(serializers.ModelSerializer):
    user = RepresentationUser(read_only=True,many=False)
    class Meta:
        model= Administrateur
        fields = '__all__'