from django.shortcuts import render
from .models import Agent
from .serializer import AgentSerializer
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
from manager.serializer import UserSerializer
from rest_framework.response import Response
from salarie.views import checkifExist,checkifExistEmail,checkUsername
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination


# Create your views here.

class AgentApi(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    queryset = Agent.objects.all()
    paginator = pagination_class()
    #serializer_class = AgentSerializer
    
    def get(self,request):

        if request.GET.get('agent',None) is not None:
            ag = int(request.GET.get('agent',None))
            agent = Agent.objects.filter(agent_secteur=ag)
        
            if(request.GET.get("paginated",None) is not None):
                agents = self.paginator.paginate_queryset(agent,request,view=self)
                serializer = AgentSerializer(agents,many=True)
                return self.paginator.get_paginated_response(serializer.data)
            serializer = AgentSerializer(agent,many=True)
            return Response(serializer.data,status= status.HTTP_200_OK) 

        agent = Agent.objects.all()
        final_ = Agent.objects.none()
        for ag in agent:
            if ag.user.groups.filter(name="Agent secteur").exists() or ag.user.groups.filter(name="Agent constat").exists() or ag.user.groups.filter(name="Audit planneur").exists():
                final_ = final_ | Agent.objects.filter(pk=ag.id)

        if(request.GET.get("paginated",None) is not None):
            serializer = AgentSerializer(final_,many=True)
            return Response(serializer.data,status= status.HTTP_200_OK)
    
        agent = self.paginator.paginate_queryset(final_,request,view=self)
        serializer = AgentSerializer(agent,many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def post(self,request):
        data = request.data

        if checkUsername(data['login'],data['email'])== "ouiUs":
            return Response({"status":"existing username"},status=status.HTTP_204_NO_CONTENT)

        #if checkUsername(data['login'],data['email'])== "ouiEm":
            #return Response({"status":"existing email"},status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            user = User(is_superuser=False, is_active=True, is_staff=False)
            user.first_name = data['prenom']
            user.last_name = data['nom']
            #user.email = data['email']
            user.username = data['login']
            user.set_password(data['mdp'])
            user.is_active = True

            us = User.objects.filter(email = data['email'])
            if us.exists():
                i = 1
                email_ = data['email']+"/"+str(i)
                use = User.objects.filter(email = email_)
                while use.exists():
                    i = i+1
                    email_ = data['email']+"/"+str(i)
                    use = User.objects.filter(email = email_)
                user.email = email_
            else:
                user.email = data['email']

            user.save()

            if int(data['role']) == 1:
                user.groups.add(Group.objects.filter(name="Agent secteur").first().id)
            elif int(data['role'])== 2:
                user.groups.add(Group.objects.filter(name="Agent constat").first().id)
            else:
                user.groups.add(Group.objects.filter(name="Audit planneur").first().id)

            user.save()
            admin = Agent.objects.create(
                user = user,
                trigramme = data['trigramme'],
                telephone = data['telephone'],
                adresse = data['adresse'],
                created_at = datetime.today()
            )
            if request.POST.get('secteur_primaire',None):
                admin.secteur_primaire = data["secteur_primaire"]

            if request.POST.get('secteur_secondaire',None):
                admin.secteur_secondaire = data["secteur_secondaire"]
            
            if request.POST.get('agent_secteur',None):
                admin.agent_secteur = data["agent_secteur"]
            admin.save()

            admin = Agent.objects.filter(pk=admin.id)
            serializer = AgentSerializer(admin,many=True)
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

class AgentApiDetails(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self,request,id):

        if request.GET.get("specific",None) is not None:
            us = User.objects.filter(pk=id)
            if us.exists():
                ag = Agent.objects.filter(user=us.first().id)
                serializer = AgentSerializer(ag,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)

        admin = Agent.objects.filter(pk=id)
        if admin.exists():
            serializer = AgentSerializer(admin,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response([{"status":"none"}], status=status.HTTP_200_OK)

    def put(self,request,id):
        data = request.data
        admin = Agent.objects.filter(pk=id)
        if admin.exists():
            admin = admin.first()

            #if checkifExistEmail(data['email'],admin.user.id) == 1:
                #return Response({"status":"existing email"}, status=status.HTTP_204_NO_CONTENT)
                
            if checkifExist(data['login'],admin.user.id) == 1:
                return Response({"status":"existing username"}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                user = admin.user
                user.first_name = data['prenom']
                user.last_name = data['nom']
                #user.email = data['email']
                user.username = data['login']
                if request.POST.get('is_active',None):
                    user.is_active = data['is_active']
                if request.POST.get('mdp',None) is not None:
                    user.set_password(data['mdp'])
<<<<<<< HEAD
                
                user.groups.remove(Group.objects.filter(name="Agent secteur").first().id)
                user.groups.remove(Group.objects.filter(name="Agent constat").first().id)
                user.groups.remove(Group.objects.filter(name="Audit planneur").first().id)

                if int(data['role']) == 1:
                    user.groups.add(Group.objects.filter(name="Agent secteur").first().id)
                    admin.agent_secteur=None
=======

                if int(data['role']) == 1:
                    user.groups.add(Group.objects.filter(name="Agent secteur").first().id)
>>>>>>> 00dddfd2bc586d0f596ac76e93b0147e04c8afd7
                elif int(data['role']) == 2:
                    user.groups.add(Group.objects.filter(name="Agent constat").first().id)
                else:
                    user.groups.add(Group.objects.filter(name="Audit planneur").first().id)
                    #.views.py.swp"
                us = User.objects.filter(email = data['email'])

                if us.exists() and us.first().id != admin.user.id:
                    i = 1
                    email_ = data['email']+"/"+str(i)
                    use = User.objects.filter(email = email_)
                    while use.exists() and use.first().id != admin.user.id :
                        i = i+1
                        email_ = data['email']+"/"+str(i)
                        use = User.objects.filter(email = email_)
                    user.email = email_
                else:
                    user.email = data['email']

                user.save()
                admin.updated_at = datetime.today()
                admin.trigramme = data['trigramme']
                admin.adresse = data['adresse']
                admin.telephone = data['telephone']
                admin.save()

                if request.POST.get('secteur_primaire',None):
                    admin.secteur_primaire = data["secteur_primaire"]

                if request.POST.get('secteur_secondaire',None):
                    admin.secteur_secondaire = data["secteur_secondaire"]
                
                if request.POST.get('agent_secteur',None):
                    admin.agent_secteur = data["agent_secteur"]
                admin.save()

                admin = Agent.objects.filter(pk=id)
                serializer= AgentSerializer(admin,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

    def delete(self,request,id):
        admin = Agent.objects.filter(pk=id)
        if admin.exists():
            admin = admin.first()
            user = admin.user
            user.delete()
            admin.delete()
            return Response({"status":"done"},status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)



