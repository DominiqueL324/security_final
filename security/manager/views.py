import email
from email.message import EmailMessage
from unicodedata import name
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import  TokenAuthentication
from rest_framework import generics
from rest_framework import mixins 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from administrateur.models import Administrateur
from administrateur.serializer import AdministrateurSerializer
from agent.models import Agent
from agent.serializer import AgentSerializer
from salarie.models import Salarie
from salarie.serializer import SalarieSerializer
from client.models import Client
from client.serializer import ClientSerializer
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User, Group
from datetime import date, datetime,time,timedelta
from django.http import JsonResponse
from salarie.views import checkifExist,checkifExistEmail,checkUsername
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializer import UserSerializer
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from django.db.models import Q

# Create your views here.
class RoleManager(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #user = Token.objects.filter(key=request.GET.get('token'))
        odj_token = AccessToken(request.GET.get('token')) 
        user = User.objects.filter(pk=int(odj_token['user_id']))

        if user.exists():
            
            us = User.objects.filter(pk=user.first().id).first()
            if not us.is_active:
                refresh_token = request.GET.get('token',None)
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"status":" user not activated"},status=status.HTTP_403_FORBIDDEN)
                 
            if us.groups.filter(name="Administrateur").exists():
                boy = Administrateur.objects.filter(user=us)
                serializer = AdministrateurSerializer(boy,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if us.groups.filter(name="Agent").exists():
                boy = Agent.objects.filter(user=us)
                serializer = AgentSerializer(boy,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if us.groups.filter(name="Salarie").exists():
                boy = Salarie.objects.filter(user=us)
                serializer = SalarieSerializer(boy,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            if us.groups.filter(name="Client").exists():
                boy = Client.objects.filter(user=us)
                serializer = ClientSerializer(boy,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status':'none'}, status=200)
    
class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        #try:
        refresh_token = request.GET.get('token',None)
        token = RefreshToken(refresh_token)
        token.blacklist()
        #odj_token = AccessToken(request.GET.get('token')) 

        return JsonResponse({"status":"done"},status=205)
        #except Exception as e:
            #return JsonResponse({"status":"bad request"},status=400)

class checkUsernameApi(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):

        username_= request.GET.get('username',None)
        email_ = request.GET.get('email',None)
        id = request.GET.get('id',None) 
        if username_ is not None and id is not None and email_ is not None:
            return JsonResponse({"status":"Bad parameters"},status = status.HTTP_400_BAD_REQUEST)

        if username_ is not None and id is not None:
            if checkifExist(username_,id)==1:
                return JsonResponse({"status":"existing username"})
            return JsonResponse({"status":"good"})

        if email_ is not None and id is not None:
            if checkifExistEmail(email_,id)==1:
                return JsonResponse({"status":"existing email"})
            return JsonResponse({"status":"good"})
        
        if request.GET.get('email',None) is not None:
            if checkUsername(email=email_)== "ouiEm":
                return Response({"status":"existing email"})
            return JsonResponse({"status":"good"})
                
        if username_  is not None:
            if checkUsername(name=username_)== "ouiUs":
                return Response({"status":"existing username"})
            return JsonResponse({"status":"good"})

        return JsonResponse({"status":"good"})

class getAllUserApi(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    paginator = pagination_class()
    def get(self,request):
        if(request.GET.get("value",None) is not None):
            val_ = request.GET.get("value",None)
            #users = User.objects.filter(email=val_)
            users = User.objects.filter(Q(first_name__icontains=val_)|Q(email__icontains=val_)|Q(last_name__icontains=val_))
            serializer = UserSerializer(users,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)

        users = self.paginator.paginate_queryset(User.objects.filter(is_staff=False),request,view=self) 
        serialized = UserSerializer(users,many=True)
        return self.paginator.get_paginated_response(serialized.data)

class userStateAPI(APIView):

    #permission_classes = [IsAuthenticated]

    def get(self,request,id):
        user = User.objects.filter(pk=int(id))
        if user.exists():
            user = user.first()
            user.is_active = 0 if user.is_active==1  else 1
            user.save()
            return Response({"status":"done"},status=status.HTTP_200_OK)
        return Response({"status":"not found"},status=status.HTTP_204_NO_CONTENT)


