from django.shortcuts import render
from rest_framework.response import Response
from .models import Administrateur
from .serializer import AdministrateurSerializer
from rest_framework.views import APIView
from rest_framework.authentication import  TokenAuthentication
from rest_framework import generics
from rest_framework import mixins 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User, Group
from datetime import date, datetime,time,timedelta
from salarie.views import checkifExist,checkifExistEmail,checkUsername


# Create your views here.

class AdministrateurApi(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        admin = Administrateur.objects.all()
        serializer = AdministrateurSerializer(admin,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request):
        data = request.data

        if checkUsername(data['login'],data['email'])== "ouiUs":
            return Response({"status":"existing username"},status=status.HTTP_204_NO_CONTENT)

        if checkUsername(data['login'],data['email'])== "ouiEm":
            return Response({"status":"existing email"},status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            user = User(is_superuser=False, is_active=True, is_staff=False)
            user.first_name = data['prenom']
            user.last_name = data['nom']
            user.email = data['email']
            user.username = data['login']
            user.set_password(data['mdp'])
            user.save()
            user.groups.add(Group.objects.filter(name="Administrateur").first().id)
            user.save()
            admin = Administrateur.objects.create(
                user = user,
                adresse = data['adresse'],
                telephone = data['telephone'],
            )
            admin = Administrateur.objects.filter(pk=admin.id)
            serializer = AdministrateurSerializer(admin,many=True)
            return Response(serializer.data,status= status.HTTP_201_CREATED)

class AdministrateurApiDetails(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id):
        admin = Administrateur.objects.filter(pk=id)
        if admin.exists():
            serializer = AdministrateurSerializer(admin,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status":"none"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        data = request.data
        admin = Administrateur.objects.filter(pk=id)
        if admin.exists():
            admin = admin.first()
            
            if checkifExistEmail(data['email'],admin.user.id) == 1:
                return Response({"status":"existing email"}, status=status.HTTP_204_NO_CONTENT)
                
            if checkifExist(data['login'],admin.user.id) == 1:
                return Response({"status":"existing username"}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                user = admin.user
                user.first_name = data['prenom']
                user.last_name = data['nom']
                user.email = data['email']
                user.username = data['login']
                if data['mdp'] is not None:
                    user.set_password(data['mdp'])
                user.groups.add(Group.objects.filter(name="Administrateur").first().id)
                user.save()
                admin.updated_at = datetime.today()
                admin.adresse = data['adresse']
                admin.telephone = data['telephone']
                admin.save()
                admin = Administrateur.objects.filter(pk=id)
                serializer= AdministrateurSerializer(admin,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

    def delete(self,request,id):
        admin = Administrateur.objects.filter(pk=id)
        if admin.exists():
            admin = admin.first()
            user = admin.user
            user.delete()
            admin.delete()
            return Response({"status":"done"},status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

