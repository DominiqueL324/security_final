import email
from pydoc import cli
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from agent.models import Agent
from salarie.models import Salarie
from client.models import Client,Comptable,Concession,ServiceGestion
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import datetime, random, string
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from datetime import date, datetime,time,timedelta
from django.db import transaction, IntegrityError
import xlwt, xlrd,random, string, json
from django.contrib.auth.models import User, Group


class ImportApi(APIView):

    def post(self,request):
        fichier = request.FILES.get('fichier')
        data_=request.data
        data = None
        if not fichier.name.endswith('xls'):
            return JsonResponse({"status":1},status=401)
        try:
            data = xlrd.open_workbook(filename=None, file_contents=fichier.read(), formatting_info=True)
        except Exception as e:
            return JsonResponse({"status":2},status=401)

        table = data.sheets()[0]
        nligne = table.nrows
        ncolonnes = table.ncols
        colnames = table.row_values(0)
        liste_finale =[]
        for i in range(nligne):
            liste_temp = []
            for j in range(ncolonnes):
                cell_values = table.row_values(i)[j]
                liste_temp.append(cell_values)
            liste_finale.append(liste_temp)
        del(liste_finale[0])
        for liste in liste_finale: 
            #try:
            #cas des users
            if int(data_["cible"]) == 1:

                #detction des valeur = NULL sur le fichier excell affectation de None 
                for u in range(14):
                    if liste[u] == "NULL":
                        liste[u] = None

                #gestion des date NULL (Affectation de None)
                if type(liste[5]) != float:
                    last_log=None
                else:
                    last_log = datetime(*xlrd.xldate_as_tuple(liste[5],data.datemode))

                if type(liste[13]) != float:
                    date_join= datetime(2000, 5, 17,12,12)
                else:
                    date_join = datetime(*xlrd.xldate_as_tuple(liste[13],data.datemode))

                user = User()
                user.id = int(liste[0])
                user.first_name = liste[10]
                user.last_name = liste[9]
                user.username = liste[2]
                user.set_password("france")
                
                user.is_active = int(liste[7])
                user.last_login = last_log
                user.date_joined = date_join
                user.is_staff = False
                us = User.objects.filter(email = liste[8])
                if us.exists():
                    i = 1
                    email_ = liste[8]+"/"+str(i)
                    use = User.objects.filter(email = email_)
                    while use.exists():
                        i = i+1
                        email_ = liste[8]+"/"+str(i)
                        use = User.objects.filter(email = email_)
                    user.email = email_
                else:
                    user.email = liste[8]
                user.save()
            if int(data_["cible"]) == 2:

                #detction des valeur = NULL sur le fichier excell affectation de None 
                for u in range(4):
                    if liste[u] == "NULL":
                        liste[u] = None

                #gestion des date NULL (Affectation de None)
                if type(liste[3]) != float:
                    created_at=None
                else:
                    created_at = datetime(*xlrd.xldate_as_tuple(liste[3],data.datemode))

                if type(liste[4]) != float:
                    updated_at= datetime(2000, 5, 17,12,12)
                else:
                    updated_at = datetime(*xlrd.xldate_as_tuple(liste[4],data.datemode))
                
                agent = Agent.objects.create(
                    id=liste[0],
                    user = User.objects.filter(pk=liste[1]).first(),
                    trigramme = liste[2],
                    created_at = created_at,
                    updated_at = updated_at
                )
            if int(data_["cible"]) == 3:

                """if int(liste[1]) == 10:
                    user = User.objects.filter(pk=int(liste[0])).first()
                    user.groups.add(Group.objects.filter(name="Agent secteur").first().id)
                    user.save()
                        
                elif int(liste[1]) == 11:
                    user = User.objects.filter(pk=int(liste[0])).first()
                    user.groups.add(Group.objects.filter(name="Agent constat").first().id)
                    user.save()
                else:
                    user = User.objects.filter(pk=int(liste[0])).first()
                    user.groups.add(Group.objects.filter(name="Audit planneur").first().id)
                    user.save()
                    #return JsonResponse({"user":user.first_name})"""
                #specification des rôles Agent
                #ag = Agent.objects.all()
                us = User.objects.filter(pk=int(liste[0])).first()
                if  us.groups.filter(name="Agent secteur").exists() :
                    us.groups.clear()
                    us.groups.add(Group.objects.filter(name="Agent secteur").first().id)
                    us.save() 

                if  us.groups.filter(name="Agent constat").exists():                  
                    us.groups.clear() 
                    us.groups.add(Group.objects.filter(name="Agent constat").first().id)
                    us.save()

                if  not us.groups.filter(name="Agent constat").exists() and not us.groups.filter(name="Agent secteur").exists():                  
                    us.groups.clear()
                    us.groups.add(Group.objects.filter(name="Audit planneur").first().id)
                    us.save()
                        
                
            if int(data_['cible']) == 4:

                for u in range(37):
                    if liste[u] == "NULL":
                        liste[u] = None
                #if liste[2] is not None:
                compta = Comptable.objects.create(
                    nom_complet = liste[21],
                    email_envoi_facture = liste[22],
                    telephone = liste[27],
                    mobile =liste[28]
                )

                gestion = ServiceGestion.objects.create(
                    nom_complet = liste[25],
                    email = liste[26],
                    telephone = liste[27],
                    mobile = liste[28]
                )

                concession = Concession.objects.create(
                    agence_secteur_rattachement = liste[29],
                    nom_concessionnaire = liste[30],
                    numero_proposition_prestation = liste[31],
                    as_client =liste[33],
                    origine_client = liste[34],
                    suivie_technique_client = liste[35]
                )
                if liste[32] is  None:

                    us = Agent.objects.filter(trigramme="Jonh Doe Max")
                    if not us.exists():
                        user_ = User()
                        user_.first_name = "John"
                        user_.last_name = "Doe"
                        user_.username = "Doe11"
                        user_.set_password("france")
                        user_.email = "johndoe@gmail.com"
                        user_.is_active = True
                        user_.date_joined = datetime(2000, 5, 17,12,12)
                        user_.is_staff = True
                        user_.save()
                        user_.groups.add(Group.objects.filter(name="Agent secteur").first().id)
                        user_.save()
                        agent = Agent.objects.create(
                            user = user_,
                            trigramme = "Jonh Doe Max",
                            created_at = datetime(2000, 5, 17,12,12),
                            updated_at = datetime(2000, 5, 17,12,12)
                        )
                    concession.agent_rattache = Agent.objects.filter(trigramme="Jonh Doe Max").first()                
                else:
                    user_ = User.objects.filter(pk=int(liste[32])).first()
                    if user_.groups.filter(name="Agent secteur").exists():
                        concession.agent_rattache = Agent.objects.filter(user=user_).first()
                    else:
                        concession.agent_rattache = Agent.objects.filter(trigramme="Jonh Doe Max").first() 
                concession.save()


                client = Client.objects.create(
                    id = int(liste[0]),
                    user = User.objects.filter(pk=int(liste[1])).first() ,
                    adresse = liste[14],
                    titre = liste[4],
                    fonction = liste[8],
                    societe = liste[9],
                    ref_societe =liste[10],
                    email_agence = liste[11],
                    siret = liste[12],
                    tva_intercommunautaire = liste[13],          
                    complement_adresse = liste[15],
                    code_postal = liste[16],
                    ville = liste[17],
                    telephone = liste[18],
                    mobile = liste[19],
                    telephone_agence = liste[20],
                    code_client = liste[3],
                    ref_comptable = compta,
                    ref_service_gestion = gestion,
                    info_concession = concession
                )
                created_at = ""
                updated_at= ""
                if type(liste[36]) != float:
                    created_at=None
                else:
                    created_at = datetime(*xlrd.xldate_as_tuple(liste[36],data.datemode))

                if type(liste[37]) != float:
                    updated_at= datetime(2000, 5, 17,12,12)
                else:
                    updated_at = datetime(*xlrd.xldate_as_tuple(liste[37],data.datemode))
                client.created_at = created_at
                client.updated_at = updated_at
                client.save()
                client = Client.objects.filter(pk=int(liste[0])).first()
                if client.siret is not None:
                    user = User.objects.filter(client=client).first()
                    user.groups.add(Group.objects.filter(name="Client pro").first().id)
                    user.save()
                    client.type = "professionnel"
                    client.save()
                else:
                    user = User.objects.filter(client=client).first()
                    user.groups.add(Group.objects.filter(name="Client particulier").first().id)
                    user.save()
                    client = Client.objects.filter(pk=int(liste[0])).first()
                    client.type = "particulier"
                    client.save()
            #else:
                #Us = User.objects.filter(pk=int(liste[1]))
                #if Us.exists():
                    #Us = Us.first()
                    #Us.delete()
                        
            if int(data_['cible']) == 5:
                for u in range(37):
                    if liste[u] == "NULL":
                        liste[u] = None
                        

                        
            if int(data_['cible']) == 6:

                for u in range(15):
                    if liste[u] == "NULL":
                        liste[u] = None

               
                user = User.objects.filter(pk=int(liste[1])).first()
                user.groups.add(Group.objects.filter(name="Salarie").first().id)
                sal = Salarie()
                
                user.save()
                sal.user = user
                sal.id = pk=int(liste[0])
                if liste[5] == "Monsieur": 
                    sal.titre = "M"
                if liste[5] == "Madame": 
                    sal.titre = "Me"
                if liste[5] == "Mademoiselle": 
                    sal.titre = "Mmll"
                sal.company = liste[10]
                sal.code = liste[4]
                sal.telephone = liste[11]
                sal.mobile = liste[12]
                sal.created_at = liste[14]
                sal.updated_at = liste[15]

                usr_ag = User.objects.filter(pk=int(liste[13])).first()
                usr_cl = User.objects.filter(pk=int(liste[3])).first()
                if usr_ag is not None:
                    ag = Agent.objects.filter(user=usr_ag)
                if usr_cl is not None:
                    cl = Client.objects.filter(user=usr_cl)

                if type(liste[14]) != float:
                    created_at= datetime(2000, 5, 17,12,12)
                else:
                    created_at = datetime(*xlrd.xldate_as_tuple(liste[14],data.datemode))
                
                if type(liste[15]) != float:
                    updated_at= datetime(2000, 5, 17,12,12)
                else:
                    updated_at = datetime(*xlrd.xldate_as_tuple(liste[15],data.datemode))

                sal.updated_at = updated_at
                sal.created_at = created_at

                if ag.exists():
                    sal.agent_rattache = ag.first()
                if cl.exists():
                    sal.client = cl.first()
                sal.save()

            #except Exception as e:
                #return JsonResponse({"status":3},status=401)    
        return Response({},status=status.HTTP_200_OK)
