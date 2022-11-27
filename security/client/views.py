from ast import In
from http import client
from pydoc import cli
from django.shortcuts import render

from agent.models import Agent
from salarie.models import Salarie
from salarie.serializer import SalarieSerializer
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
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


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

        if(request.GET.get("token",None) is not None):
            odj_token = AccessToken(request.GET.get('token'))
            user = User.objects.filter(pk=int(odj_token['user_id'])).first()
            final_ = Client.objects.none()

            #recupération clients pour un AS
            if user.groups.filter(name="Agent secteur").exists():
                ag = Agent.objects.filter(user=user).first()
                ifc = Concession.objects.filter(agent_rattache=ag)
                for ik in ifc:
                    cl = Client.objects.filter(info_concession=ik).first()
                    if cl is not None:
                        if cl.user.groups.filter(name="Client pro").exists() or cl.user.groups.filter(name="Client particulier").exists():
                            final_ = final_ | Client.objects.filter(pk=cl.id)

            #recupération clients pour un agent de constat                
            if user.groups.filter(name="Agent constat").exists() and not user.groups.filter(name="Agent secteur").exists():
                ag = Agent.objects.filter(user=user).first()
                if ag is not None:
                    if Agent.objects.filter(pk=ag.agent_secteur).first() is not None:
                        ifc = Concession.objects.filter(agent_rattache=Agent.objects.filter(pk=ag.agent_secteur).first())
                        for ik in ifc:
                            cl = Client.objects.filter(info_concession=ik).first()
                            if cl is not None:
                                if cl.user.groups.filter(name="Client pro").exists() or cl.user.groups.filter(name="Client particulier").exists():
                                    final_ = final_ | Client.objects.filter(pk=cl.id)
            

            #recupération clients pour un audit planneur                
            if user.groups.filter(name="Audit planneur").exists() and not user.groups.filter(name="Agent secteur").exists() and not user.groups.filter(name="Agent constat").exists():
                pass
                #il peut prendre un RDV pour tous les clients donc il estr comme un admin

                    
            if (request.GET.get("paginated",None) is not None):
                client = self.paginator.paginate_queryset(final_,request,view=self)
                serializer = ClientSerializer(client,many=True)
                return self.paginator.get_paginated_response(serializer.data)
            
            serializer = ClientSerializer(final_,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)

        client = Client.objects.all()
        if(request.GET.get("paginated",None) is not None):
            final_ = Client.objects.none()
            for cl in client:
                if cl.user.groups.filter(name="Client pro").exists() or cl.user.groups.filter(name="Client particulier").exists():
                    final_ = final_ | Client.objects.filter(pk=cl.id)
            serializer = ClientSerializer(final_,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        """if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)"""

        

        final_ = Client.objects.none()
        for cl in client:
            if cl.user.groups.filter(name="Client pro").exists() or cl.user.groups.filter(name="Client particulier").exists():
                final_ = final_ | Client.objects.filter(pk=cl.id)
        client = self.paginator.paginate_queryset(final_,request,view=self)
        serializer = ClientSerializer(client,many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def post(self,request):
        data = request.data
        if request.POST.get('login',None) is not None:
            if checkUsername(data['login'],data['email_reponsable'])== "ouiUs":
                return Response({"status":"existing username"},status=status.HTTP_204_NO_CONTENT)

        #if checkEmail(data['email_reponsable']) == 1:
            #return Response({"status":"existing email"},status=status.HTTP_204_NO_CONTENT)


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
            #user.email = data['email_reponsable']

            user.username = login
            user.is_active = True
            user.set_password(mdp)

            us = User.objects.filter(email = data['email_reponsable'])
            if us.exists():
                i = 1
                email_ = data['email_reponsable']+"/"+str(i)
                use = User.objects.filter(email = email_)
                while use.exists():
                    i = i+1
                    email_ = data['email_reponsable']+"/"+str(i)
                    use = User.objects.filter(email = email_)
                user.email = email_
            else:
                user.email = data['email_reponsable']
            user.save()

            if int(data['type']) == 1:
                user.groups.add(Group.objects.filter(name="Client pro").first().id)
            else:
                user.groups.add(Group.objects.filter(name="Client particulier").first().id)
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

            concession = Concession.objects.create(
                agent_rattache = Agent.objects.filter(pk=int(data['agent_rattache'])).first(),
                agence_secteur_rattachement = None,
                nom_concessionnaire = None,
                numero_proposition_prestation = None,
                nom_complet = None,
                as_client = None,
                origine_client = None,
                suivie_technique_client = None
            )
            type_ =""
            if int(data['type']) == 1:
                type_="professionnel"
            else:
                type_="particulier"
            client = Client.objects.create(
                user = user,
                adresse = data['adresse'],
                type = type_,
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
                info_concession = concession  
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
        
        
        if request.GET.get("specific",None) is not None:
            us = User.objects.filter(pk=id)
            try:
                client = Client.objects.filter(user=us.first().id)
            except:
                return Response([{"status":"none"}], status=status.HTTP_200_OK)
            if client.exists():
                serializer = ClientSerializer(client,many=True)
                final_ = serializer.data
                client = client.first()
                if client.type != "particulier":
                    salarie = Salarie.objects.filter(client=client)
                    serializer_sal = SalarieSerializer(salarie,many=True)
                    sal = serializer_sal.data
                    final_[0]['passeur']=sal
                return Response(final_,status=status.HTTP_200_OK)
        try:
            client = Client.objects.filter(pk=id)
        except:
            return Response([{"status":"none"}], status=status.HTTP_200_OK)
        if client.exists():
            serializer = ClientSerializer(client,many=True)
            final_ = serializer.data
            client = client.first()
            if client.type != "particulier":
                salarie = Salarie.objects.filter(client=client)
                serializer_sal = SalarieSerializer(salarie,many=True)
                sal = serializer_sal.data
                final_[0]['passeur']=sal

            return Response(final_,status=status.HTTP_200_OK)
        return Response([{"status":"none"}], status=status.HTTP_200_OK)

    def put(self,request,id):
        data = request.data
        client = Client.objects.filter(pk=id)
        if client.exists():
            client = client.first()

            #if checkifExistEmail(data['email_reponsable'],client.user.id) == 1:
                #return Response({"status":"existing email"}, status=status.HTTP_204_NO_CONTENT)

            if request.POST.get('login',None) is not None:    
                if checkifExist(data['login'],client.user.id) == 1:
                    return Response({"status":"existing username"}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                user = client.user
                user.first_name = data['prenom']
                user.last_name = data['nom']
                #user.email = data['email_reponsable']
                if request.POST.get('is_active',None):
                    user.is_active = data['is_active']

                if request.POST.get('login',None) is not None:  
                    user.username = data['login']

                if request.POST.get('mdp',None) is not None:  
                    user.set_password(data['mdp'])
                
                user.groups.remove(Group.objects.filter(name="Client pro").first().id)
                user.groups.remove(Group.objects.filter(name="Client particulier").first().id)

                if int(data['type']) == 1:
                    user.groups.add(Group.objects.filter(name="Client pro").first().id)
                else:
                    user.groups.add(Group.objects.filter(name="Client particulier").first().id)

                us = User.objects.filter(email = data['email_reponsable'])
                if us.exists() and us.first().id != client.user.id:
                    i = 1
                    email_ = data['email_reponsable']+"/"+str(i)
                    use = User.objects.filter(email = email_)
                    while use.exists() and use.first().id != client.user.id :
                        i = i+1
                        email_ = data['email_reponsable']+"/"+str(i)
                        use = User.objects.filter(email = email_)
                    user.email = email_
                else:
                    user.email = data['email_reponsable']
                    
                user.save()
                #user.groups.add(Group.objects.filter(name="Client").first().id)
                user.save()
                #changement ici
                if int(data['type']) == 1:
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
                    client.ref_comptable = comptable
                    client.ref_service_gestion = service
                    client.fonction = data['fonction']
                    client.societe = data['societe']
                    client.ref_societe = data['ref_societe']
                    client.email_agence = data['email_agence']
                    client.siret = data['siret']
                    client.tva_intercommunautaire = data['tva_intercommunautaire']
                    client.type = "professionnel"
                    client.code_client = data['code_client']
                elif int(data['type']) == 0:
                    pass
                else:    
                    client.code_client = None
                    client.ref_comptable = None
                    client.ref_service_gestion = None
                    client.fonction = None
                    client.societe = None
                    client.ref_societe = None
                    client.email_agence = None
                    client.siret = None
                    client.tva_intercommunautaire = None
                    client.type = "particulier"

                concession = Concession.objects.create(
                    agence_secteur_rattachement = request.POST.get("agence_secteur_rattachement",None),
                    nom_concessionnaire = request.POST.get("nom_concessionnaire",None),
                    numero_proposition_prestation = request.POST.get("numero_proposition_prestation",None),
                    nom_complet = request.POST.get("nom_concessionnaire",None),
                    as_client = request.POST.get("as_client",None),
                    origine_client = request.POST.get("origine_client",None),
                    suivie_technique_client = request.POST.get("suivie_technique_client",None)
                )
                if request.POST.get("agent_rattache",None) is not None:
                    concession.agent_rattache = Agent.objects.filter(pk=int(data['agent_rattache'])).first()
                else:
                    concession.agent_rattache = None
                concession.save()

                client.user = user
                if request.POST.get("statut_client",None) is not None:
                    client.statut = data['statut_client']
                if request.POST.get("adresse",None) is not None:
                    client.adresse = data['adresse']
                if request.POST.get("titre",None) is not None:
                    client.titre = data['titre']
                if request.POST.get("complement_adresse",None) is not None:
                    client.complement_adresse = data['complement_adresse']
                if request.POST.get("code_postal",None) is not None:
                    client.code_postal = data['code_postal']
                if request.POST.get("ville",None) is not None:
                    client.ville = data['ville']
                if request.POST.get("telephone",None) is not None:
                    client.telephone = data['telephone']
                if request.POST.get("mobile",None) is not None:    
                    client.mobile = data['mobile']
                if request.POST.get("telephone_agence",None) is not None:
                    client.telephone_agence = request.POST.get('telephone_agence',None)
                
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

