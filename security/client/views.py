from http import client
from pydoc import cli
from django.shortcuts import render

from agent.models import Agent
from .models import Client,Comptable,Concession,ServiceGestion
from .serializer import ClientSerializer
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
from salarie.views import checkifExist,checkifExistEmail,checkUsername
import datetime, random, string
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination


# Create your views here.

class ClientApi(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    queryset = Client.objects.all()
    paginator = pagination_class()
    #serializer_class = ClientSerializer

    def get(self,request):
        #page = self.paginate_queryset(self.queryset)
        """if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)"""
        client = self.paginator.paginate_queryset(self.queryset,request,view=self)
        serializer = ClientSerializer(client,many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def post(self,request):
        data = request.data
        if request.POST.get('login',None) is not None:
            if checkUsername(data['login'],data['email_reponsable'])== "ouiUs":
                return Response({"status":"existing username"},status=status.HTTP_204_NO_CONTENT)

        if checkEmail(data['email_reponsable']) == 1:
            return Response({"status":"existing email"},status=status.HTTP_204_NO_CONTENT)


        with transaction.atomic():
            login = ""
            code_client=""
            mdp = ""
            if request.POST.get('login',None) is None:
                login = "".join([random.choice(string.ascii_letters) for _ in range(5)])
            else:
                login = data['login']

            if request.POST.get('mdp',None) is None:
                mdp = "".join([random.choice(string.ascii_letters) for _ in range(10)]) 
            else:
                mdp = data['mdp']

            if request.POST.get('code_client',None) is None:
                code_client = "".join([random.choice(string.ascii_letters) for _ in range(15)]) 
            else:
                code_client = data['code_client']
            
            user = User(is_superuser=False, is_active=True, is_staff=False)
            user.first_name = data['prenom']
            user.last_name = data['nom']
            user.email = data['email_reponsable']
            user.username = login
            user.set_password(mdp)
            user.save()
            user.groups.add(Group.objects.filter(name="Client").first().id)
            user.save()

            """comptable = Comptable.objects.create(
                nom_complet = data['nom_complet_comptable'],
                email_envoi_facture = data['email_envoi_facture'],
                telephone = data['telephone_comptable'],
                mobile = data['mobile_comptable']
            )"""

            """service = ServiceGestion.objects.create(
                nom_complet = data['nom_complet_contact'],
                email = data['email_service_gestion'],
                telephone = data['telephone_service_gestion'],
                mobile = data['mobile_service_gestion']
            )"""

            """concession = Concession.objects.create(
                agent_rattache = Agent.objects.filter(pk=int(data['agent_rattache'])).first(),
                agence_secteur_rattachement = data['agence_secteur_rattachement'],
                nom_concessionnaire = data['nom_concessionnaire'],
                numero_proposition_prestation = data['numero_proposition_prestation'],
                nom_complet = data['nom_concessionnaire'],
                as_client = data['as_client'],
                origine_client = data['origine_client'],
                suivie_technique_client = data['suivie_technique_client']
            )"""

            client = Client.objects.create(
                user = user,
                adresse = data['adresse'],
                #statut = data['statut_client'],
                #titre = data['titre'],
                #fonction = data['fonction'],
                #societe = data['societe'],
                #ref_societe = data['ref_societe'],
                #email_agence = data['email_agence'],
                #siret = data['siret'],
                #tva_intercommunautaire = data['tva_intercommunautaire'],
                #complement_adresse = data['complement_adresse'],
                #code_postal = data['code_postal'],
                #ville = data['ville'],
                telephone = data['telephone'],
                #mobile = data['mobile'],
                #telephone_agence = data['telephone_agence'],
                code_client = code_client,
                #ref_comptable = comptable,
                #ref_service_gestion = service,
                #info_concession = concession  
            )

            client = Client.objects.filter(pk=client.id)
            serializer = ClientSerializer(client,many=True)
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

class ClientApiDetails(APIView):

    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id):
        client = Client.objects.filter(pk=id)
        if client.exists():
            serializer = ClientSerializer(client,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status":"none"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        data = request.data
        client = Client.objects.filter(pk=id)
        if client.exists():
            client = client.first()

            if checkifExistEmail(data['email_reponsable'],client.user.id) == 1:
                return Response({"status":"existing email"}, status=status.HTTP_204_NO_CONTENT)

            if request.POST.get('login',None) is not None:    
                if checkifExist(data['login'],client.user.id) == 1:
                    return Response({"status":"existing username"}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                user = client.user
                #comptable = client.ref_comptable
                #service = client.ref_service_gestion
                #concession = client.info_concession

                user.first_name = data['prenom']
                user.last_name = data['nom']
                user.email = data['email_reponsable']

                if request.POST.get('login',None) is not None:  
                    user.username = data['login']

                if request.POST.get('mdp',None) is not None:  
                    user.set_password(data['mdp'])
                user.save()
                user.groups.add(Group.objects.filter(name="Client").first().id)
                user.save()

                comptable = Comptable.objects.create(
                    nom_complet = data['nom_complet_comptable'],
                    email_envoi_facture = data['email_envoi_facture'],
                    telephone = data['telephone_comptable'],
                    mobile = data['mobile_comptable']
                )

                service = ServiceGestion.objects.create(
                    nom_complet = data['nom_complet_contact'],
                    email = data['email_service_gestion'],
                    telephone = data['telephone_service_gestion'],
                    mobile = data['mobile_service_gestion']
                )

                concession = Concession.objects.create(
                    agent_rattache = Agent.objects.filter(pk=int(data['agent_rattache'])).first(),
                    agence_secteur_rattachement = data['agence_secteur_rattachement'],
                    nom_concessionnaire = data['nom_concessionnaire'],
                    numero_proposition_prestation = data['numero_proposition_prestation'],
                    nom_complet = data['nom_concessionnaire'],
                    as_client = data['as_client'],
                    origine_client = data['origine_client'],
                    suivie_technique_client = data['suivie_technique_client']
                )

                """comptable.nom_complet = data['nom_complet_comptable']
                comptable.email_envoi_facture = data['email_envoi_facture']
                comptable.telephone = data['telephone_comptable']
                comptable.mobile = data['mobile_comptable']
                comptable.save()

                service.nom_complet = data['nom_complet_contact']
                service.email = data['email_service_gestion']
                service.telephone = data['telephone_service_gestion']
                service.mobile = data['mobile_service_gestion']
                service.save()

                concession.agent_rattache = Agent.objects.filter(pk=int(data['agent_rattache'])).first()
                concession.agence_secteur_rattachement = data['agence_secteur_rattachement']
                concession.nom_concessionnaire = data['nom_concessionnaire']
                concession.numero_proposition_prestation = data['numero_proposition_prestation']
                concession.nom_complet = data['nom_concessionnaire']
                concession.as_client = data['as_client']
                concession.origine_client = data['origine_client']
                concession.suivie_technique_client = data['suivie_technique_client']
                concession.save()"""

                client.user = user
                client.statut = data['statut_client']
                client.adresse = data['adresse']
                client.titre = data['titre']
                client.fonction = data['fonction']
                client.societe = data['societe']
                client.ref_societe = data['ref_societe']
                client.email_agence = data['email_agence']
                client.siret = data['siret']
                client.tva_intercommunautaire = data['tva_intercommunautaire']
                client.complement_adresse = data['complement_adresse']
                client.code_postal = data['code_postal']
                client.ville = data['ville']
                client.telephone = data['telephone']
                client.mobile = data['mobile']
                client.telephone_agence = data['telephone_agence']
                client.code_client = data['code_client']
                client.ref_comptable = comptable
                client.ref_service_gestion = service
                client.info_concession = concession
                client.save()
                client = Client.objects.filter(pk=id)

                serializer = ClientSerializer(client,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)

        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

    def delete(self,request,id):
        client = Client.objects.filter(pk=id)
        if client.exists():
            client = client.first()
            comptable = client.ref_comptable
            gestion = client.ref_service_gestion
            concession = client.info_concession
            user = client.user
            client.delete()
            comptable.delete()
            gestion.delete()
            concession.delete()
            user.delete()
            return Response({"status":"done"},status=status.HTTP_200_OK)
        return Response({"status":"none"},status=status.HTTP_204_NO_CONTENT)

def checkEmail(nom):
        user = User.objects.filter(email=nom)
        if user.exists():
            return 1
        else:
            return 0

