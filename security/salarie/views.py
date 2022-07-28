from cmath import e
from django.shortcuts import render
from .models import Salarie
from agent.models import Agent
from .serializer import SalarieSerializer
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
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination


# Create your views here.

class SalarieApi(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    queryset = Salarie.objects.all()
    serializer_class = SalarieSerializer
    paginator = pagination_class()


    def get(self,request):

        if(request.GET.get("paginated",None) is not None):
            salarie = Salarie.objects.all()
            serializer = SalarieSerializer(salarie,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        """page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)"""
        salarie = self.paginator.paginate_queryset(self.queryset,request,view=self)
        serializer = SalarieSerializer(salarie,many=True)
        return self.paginator.get_paginated_response(serializer.data)

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
            user.is_active = True
            user.set_password(data['mdp'])
            user.save()
            user.groups.add(Group.objects.filter(name="Salarie").first().id)
            user.save()
            salarie = Salarie.objects.create(
                user = user,
                titre =  data['titre'],
                fonction =  data['fonction'],
                telephone =  data['telephone'],
                mobile =  data['mobile'],
                agent_rattache = Agent.objects.filter(pk=int( data['agent'])).first()
            )
            salarie = Salarie.objects.filter(pk=salarie.id)
            serializer = SalarieSerializer(salarie,many=True)
            return Response(serializer.data,status= status.HTTP_201_CREATED)
            
    """@property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self,queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self,data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)"""

class SalarieApiDetails(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id):
        salarie = Salarie.objects.filter(pk=id)
        if salarie.exists():
            serializer = SalarieSerializer(salarie,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status":"none"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        data = request.data
        salarie = Salarie.objects.filter(pk=id)
        
        if salarie.exists():
            salarie = salarie.first()
            if checkifExistEmail(data['email'],salarie.user.id) == 1:
                return Response({"status":"existing email"}, status=status.HTTP_204_NO_CONTENT)
                
            if checkifExist(data['login'],salarie.user.id) == 1:
                return Response({"status":"existing username"}, status=status.HTTP_204_NO_CONTENT)
            with transaction.atomic():
                user = salarie.user
                user.first_name = data['prenom']
                user.last_name = data['nom']
                user.email = data['email']
                user.is_active = data['is_active']
                user.username = data['login']
                if data['mdp'] is not None:
                    user.set_password(data['mdp'])
                user.groups.add(Group.objects.filter(name="Salarie").first().id)
                user.save()
                salarie.updated_at = datetime.today()
                salarie.titre =  data['titre']
                salarie.fonction =  data['fonction']
                salarie.telephone =  data['telephone']
                salarie.mobile =  data['mobile']
                salarie.agent_rattache = Agent.objects.filter(pk=int( data['agent'])).first()
                salarie.save()
                salarie = Salarie.objects.filter(pk=id)
                serializer= SalarieSerializer(salarie,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

    def delete(self,request,id):
        salarie = Salarie.objects.filter(pk=id)
        if salarie.exists():
            salarie = salarie.first()
            user = salarie.user
            user.delete()
            salarie.delete()
            return Response({"status":"done"},status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

def checkUsername(name="",email=""):
    user = User.objects.filter(username=name)
    if user.exists():
        return "ouiUs"
    user = User.objects.filter(email=email)
    if user.exists():
        return "ouiEm"
    return "non"

def checkifExistEmail(nom,id):
        user = User.objects.filter(email=nom)
        if user.exists():
            user = user.first()
            if int(user.id) == int(id):
                return 0
            else:
                return 1 
        else:
            return 0

def checkifExist(nom,id):
        user = User.objects.filter(username=nom)
        if user.exists():
            user = user.first()
            if int(user.id) == int(id):
                return 0
            else:
                return 1 
        else:
            return 0

