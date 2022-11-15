from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import datetime, random, string
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from datetime import date, datetime,time,timedelta
from django.db import transaction, IntegrityError
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from django.core.mail import send_mail
from django.db.models import Q
from manager.serializer import UserSerializer
from agent.models import Agent
from client.models import Client, Concession
# Create your views here.

class FiltreAPI(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    paginator = pagination_class()

    def get(self,request):
        
        if request.GET.get('administrateur',None) is not None or request.GET.get('auditplanneur',None) is not None:
            user = User.objects.filter(is_staff=False).order_by('-id')
            if request.GET.get('role',None) is not None:
                grp = request.GET.get('role')
                for us in user:
                    if us.groups.filter(name=grp).exists():
                        pass
                    else:
                        user=user.exclude(id=us.id)
            
            if request.GET.get('etat',None) is not None:
                grp = int(request.GET.get('etat'))
                for us in user:
                    if us.is_active==grp:
                        pass
                    else:
                        user=user.exclude(id=us.id)
            users = self.paginator.paginate_queryset(user,request,view=self) 
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data)

        if request.GET.get('agent',None) is not None:
            final_ = User.objects.none()
            agent = int(request.GET.get('agent',None))
            ag = Agent.objects.filter(agent_secteur=agent)
            cp = Concession.objects.filter(agent_rattache=agent)
            planneur = User.objects.all().order_by('-id')
            for c in cp:
                cl = Client.objects.filter(info_concession=c).first()
                if cl is not None:
                    final_ = final_ | User.objects.filter(pk=cl.user.id)
            for a in ag:
                final_ = final_ | User.objects.filter(pk=a.user.id)

            for u in planneur:
                if u.groups.filter(name="Audit planneur").exists():
                    final_ = final_ | User.objects.filter(pk=u.id)

            
            if request.GET.get('role',None) is not None:
                grp = request.GET.get('role')
                for us in final_:
                    if us.groups.filter(name=grp).exists():
                        pass
                    else:
                        final_=final_.exclude(id=us.id)
            
            if request.GET.get('etat',None) is not None:
                grp = int(request.GET.get('etat'))
                for us in final_:
                    if us.is_active==grp:
                        pass
                    else:
                        final_=final_.exclude(id=us.id)
            users = self.paginator.paginate_queryset(final_,request,view=self) 
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data) 

        if request.GET.get('client',None) is not None:
            final_ = User.objects.none()
            client = int(request.GET.get('client',None))
            client_ = Client.objects.filter(pk=client).first()
            salaries = Salarie.objects.filter(client=client_)
            for c in salaries:
                final_ = final_ | User.objects.filter(pk=c.user.id)
            
            if request.GET.get('etat',None) is not None:
                grp = int(request.GET.get('etat'))
                for us in final_:
                    if us.is_active==grp:
                        pass
                    else:
                        final_=final_.exclude(id=us.id)
            users = self.paginator.paginate_queryset(final_,request,view=self) 
            serialized = UserSerializer(users,many=True)
            return self.paginator.get_paginated_response(serialized.data)

        user__ = User.objects.all()
        users = self.paginator.paginate_queryset(user__,request,view=self) 
        serialized = UserSerializer(users,many=True)
        return self.paginator.get_paginated_response(serialized.data)
        

