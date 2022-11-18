import email
from email.message import EmailMessage
from http import client
from queue import Empty
from unicodedata import name
from urllib import request
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
from client.models import Client,Concession
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
import datetime, random, string

# Create your views here.
class RoleManager(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #user = Token.objects.filter(key=request.GET.get('token'))
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
                user = User.objects.filter(is_staff=False)
                client = Client.objects.all().count()
                agent = Agent.objects.all().count()
                salarie = Salarie.objects.all().count()
                admin = Administrateur.objects.all().count()
                i=0
                for us in user:
                    liste_ = us.groups.all()
                    if len(liste_)>=1:
                        i = i+1
                final_ = {
                    "utilisateurs":i,
                    "salarie":salarie,
                    "client":client,
                    "agent":agent,
                    "admin":admin
                }
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)

            if us.groups.filter(name="Agent secteur").exists():
                boy = Agent.objects.filter(user=us)
                serializer = AgentSerializer(boy,many=True)
                user = User.objects.filter(is_staff=False,administrateur=None).count()
                cn = Concession.objects.filter(agent_rattache=boy.first().id)
                agent = Agent.objects.filter(agent_secteur=boy.first().id).count()
                i=0
                k=0
                for c in cn:
                    if Client.objects.filter(info_concession=c).first() is not None:
                        i = i+1
                        k = k +  Salarie.objects.filter(client=Client.objects.filter(info_concession=c).first().id).count()
                #salarie = Salarie.objects.filter(agent_rattache=boy.first().id).count()

                final_ = {
                    "client":i,
                    "agent":agent,
                    "salarie":k
                }
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)
            
            if us.groups.filter(name="Agent constat").exists():
                boy = Agent.objects.filter(user=us)
                cn = Concession.objects.filter(agent_rattache=boy.first().id).count()
                serializer = AgentSerializer(boy,many=True)
                client = Client.objects.filter().count()
                salarie = Salarie.objects.filter(agent_rattache=boy.first().id).count()
                final_ = {
                    "client":cn,
                    "salarie":salarie
                }
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)
            
            if us.groups.filter(name="Audit planneur").exists():
                boy = Agent.objects.filter(user=us)
                cn = Concession.objects.filter(agent_rattache=boy.first().id).count()
                salarie = Salarie.objects.filter(agent_rattache=boy.first().id).count()
                serializer = AgentSerializer(boy,many=True)
                final_ = {
                    "client":cn,
                    "salarie":salarie
                }
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)

            if us.groups.filter(name="Salarie").exists():
                boy = Salarie.objects.filter(user=us)
                serializer = SalarieSerializer(boy,many=True)
                final_={}
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)

            if us.groups.filter(name="Client pro").exists():
                boy = Client.objects.filter(user=us)
                serializer = ClientSerializer(boy,many=True)
                salaries = Salarie.objects.filter(client=boy.first().id).count()
                final_={
                    "salarie":salaries,
                }
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)
            
            if us.groups.filter(name="Client particulier").exists():
                boy = Client.objects.filter(user=us)
                serializer = ClientSerializer(boy,many=True)
                final_={}
                data = serializer.data
                data[0]["stats"] = final_
                return Response(data, status=status.HTTP_200_OK)

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

        #recherche
        if(request.GET.get("value",None) is not None):
            val_ = request.GET.get("value",None)
            #users = User.objects.filter(email=val_)
            if(request.GET.get("secteur",None) is not None):
                agent_id = int(request.GET.get("secteur",None))
                user = User.objects.filter(Q(first_name__icontains=val_)|Q(email__icontains=val_)|Q(last_name__icontains=val_),administrateur=None,is_staff=False)
                for u in user:
                    if u.groups.filter(name="Agent constat").exists():
                        Ag = Agent.objects.filter(user=u)
                        if Ag.first().agent_secteur == agent_id:
                            pass
                        else:
                            user = user.exclude(id=u.id)

                    if u.groups.filter(name="Client pro").exists():
                        Ag = Client.objects.filter(user=u)
                        if Ag.first().info_concession.agent_rattache.id == agent_id:
                            pass
                        else:
                            user = user.exclude(id=u.id)
                    
                    if u.groups.filter(name="Client particulier").exists():
                        Ag = Client.objects.filter(user=u)
                        if Ag.first().info_concession.agent_rattache.id == agent_id:
                            pass
                        else:
                            user = user.exclude(id=u.id)

                    if u.groups.filter(name="Salarie").exists():
                        Ag = Salarie.objects.filter(user=u)
                        if Ag.first().client is not None:
                            if Ag.first().client.info_concession.agent_rattache.id == agent_id:
                                pass
                            else:
                                user = user.exclude(id=u.id)
                        else:
                            user = user.exclude(id=u.id)
            elif (request.GET.get("client",None) is not None):
                client = int(request.GET.get("client",None))
                user = User.objects.filter(Q(first_name__icontains=val_)|Q(email__icontains=val_)|Q(last_name__icontains=val_),administrateur=None,client=None,agent=None,is_staff=False)
                for u in user:
                    sal = Salarie.objects.filter(user=u).first()
                    if sal is not None:
                        if sal.client is not None:
                            if sal.client.id == client:
                                pass
                            else:
                                user = user.exclude(id=u.id)
                        else:
                            user = user.exclude(id=u.id)
                    else:
                        user = user.exclude(id=u.id)
            else:
                user = User.objects.filter(Q(first_name__icontains=val_)|Q(email__icontains=val_)|Q(last_name__icontains=val_),is_staff=False)

            final_ = User.objects.none()
            for us in user:
                liste_ = us.groups.all()
                if len(liste_)>=1:
                    final_ = final_ | User.objects.filter(pk=us.id)
                    
            users = self.paginator.paginate_queryset(final_,request,view=self)
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data)

        #recupération des non admin (role agent)
        if(request.GET.get("agent",None) is not None):
            usr = User.objects.none()
            planneur = User.objects.all().order_by('-id')
            ag = Agent.objects.filter(agent_secteur=int(request.GET.get("agent"))).order_by('-id')
            client = Client.objects.all().order_by('-id')
            final_ = []
            for cl in client:
                if cl.info_concession.agent_rattache.id == int(request.GET.get("agent")):
                    final_.append(cl)
            for a in ag:
                usr = usr | User.objects.filter(pk=a.user.id)
            for c in final_:
                usr = usr | User.objects.filter(pk=c.user.id)
            for p in planneur:
                if p.groups.filter(name="Audit planneur").exists():
                    usr = usr | User.objects.filter(pk=p.id)

                if p.groups.filter(name="Salarie").exists():
                    sal = Salarie.objects.filter(user=p).first()
                    if sal.client is not None:
                        if sal.client.info_concession.agent_rattache.id == int(request.GET.get("agent")):
                            usr = usr | User.objects.filter(pk=p.id)
            """user = User.objects.filter(administrateur=None,is_staff=False)
            final_ = User.objects.none()
            for us in user:
                liste_ = us.groups.all()
                if len(liste_)>=1:
                    final_ = final_ | User.objects.filter(pk=us.id)"""
            users = self.paginator.paginate_queryset(usr,request,view=self) 
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data)

        #recupération des non admin (role agent)
        if(request.GET.get("agent",None) is not None):
            usr = User.objects.none()
            planneur = User.objects.all().order_by('-id')
            ag = Agent.objects.filter(agent_secteur=int(request.GET.get("agent"))).order_by('-id')
            #client = Client.objects.all()
            final_ = []
            a = Agent.objects.filter(pk=int(request.GET.get("agent"))).first()
            con = Concession.objects.filter(agent_rattache=a.id).order_by('-id')
            for c in con:
                final_.append(Client.objects.filter(info_concession=c).first())
            #for cl in client:
                #if cl.info_concession.agent_rattache.id == int(request.GET.get("agent")):
                    #final_.append(cl)
            for a in ag:
                usr = usr | User.objects.filter(pk=a.user.id)
            for c in final_:
                if c is not None:
                    usr = usr | User.objects.filter(pk=c.user.id)
            for p in planneur:
                if p.groups.filter(name="Audit planneur").exists():
                    usr = usr | User.objects.filter(pk=p.id)
            """user = User.objects.filter(administrateur=None,is_staff=False)
            final_ = User.objects.none()
            for us in user:
                liste_ = us.groups.all()
                if len(liste_)>=1:
                    final_ = final_ | User.objects.filter(pk=us.id)"""
            users = self.paginator.paginate_queryset(usr,request,view=self) 
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data)

        #recupération des non admin (role agent)
        if(request.GET.get("client",None) is not None):
            user = User.objects.filter(pk=int(request.GET.get("client"))).order_by('-id')
            cl = Client.objects.filter(user=user.first().id)
            sal = Salarie.objects.filter(client=cl.first().id)
            user = User.objects.filter(salarie=sal.first())
            users = self.paginator.paginate_queryset(user,request,view=self) 
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data)

        #recupération globale (role admin)
        user = User.objects.filter(is_staff=False).order_by('-id')
        final_ = User.objects.none()
        for us in user:
            liste_ = us.groups.all()
            if len(liste_)>=1:
                final_ = final_ | User.objects.filter(pk=us.id)
        users = self.paginator.paginate_queryset(final_,request,view=self) 
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


class getSingleUser(APIView):

    def get(self,request,id):
        us = User.objects.filter(pk=int(id))
        if us.exists():
            serialized = UserSerializer(us,many=True)
            return Response(serialized.data,status=status.HTTP_200_OK)
        return Response([{"status":"not found"}],status=status.HTTP_200_OK)


class backupPwd(APIView):
    def get(self,request):
        email = request.GET.get("email",None)
        if email is not None:
            us = User.objects.filter(email=email)
            if us.exists():
                serialized = UserSerializer(us,many=True)
                return Response(serialized.data,status=status.HTTP_200_OK)
        return Response({"status":"not found"},status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        data = request.data
        us = User.objects.filter(email=data['email']).first()
        pwd ="".join([random.choice(string.ascii_letters) for _ in range(10)]) 
        us.set_password(pwd)
        us.save()
        return Response({"pass":pwd},status=status.HTTP_200_OK)

class TriView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    paginator = pagination_class()

    def get(self,request):

        users = User.objects.all()
        groupe=""
        etat=""
        client=""
        agent=""
        criteres = {
            "group":False,
            "is_active":False,
            "client":False,
            "agent":False
        }
        #filtre (requette)
        query = Q()

        r = 1
        #cas etat
        if(request.GET.get('etat',None) is not None):
            statut_ = request.GET.get('etat',None)
            query &= Q(is_active=int(statut_))

        #cas d'un client
        if(request.GET.get('client',None) is not None):
            statut_ = request.GET.get('client',None)
            query &= Q(client=int(statut_))

        #cas agent
        if(request.GET.get('agent',None) is not None):
            statut_ = request.GET.get('agent',None)
            query &= Q(client=int(statut_))

        #cas de groupe
        if request.GET.get('role',None) is not None:
            groupe = request.GET.get('role',None)
            criteres['group']=True

        query_set=User.objects.filter(query)
        page = self.paginator.paginate_queryset(query_set,request,view=self)
        serializer = UserSerializer(page,many=True)
        return self.paginator.get_paginated_response(serializer.data)
