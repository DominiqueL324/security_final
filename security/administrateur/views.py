from django.shortcuts import render
from rest_framework.response import Response
from .models import Administrateur
from .serializer import AdministrateurSerializer
from rest_framework.views import APIView
from rest_framework.authentication import  TokenAuthentication
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
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
from django.conf import settings
from security.settings import *


# Create your views here.

class AdministrateurApi(APIView):

    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated,]
    pagination_class = PageNumberPagination
    paginator = pagination_class()
    def get(self,request): 
        #page = self.paginate_queryset(self.queryset)
        if(request.GET.get("paginated",None) is not None):
            admin = Administrateur.objects.all()
            serializer = AdministrateurSerializer(admin,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        """if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)"""
        page = self.paginator.paginate_queryset(Administrateur.objects.all(), request, view=self)
        serializer = AdministrateurSerializer(page,many=True)
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
            user.save()
            user.groups.add(Group.objects.filter(name="Administrateur").first().id)
            
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
            admin = Administrateur.objects.create(
                user = user,
                adresse = data['adresse'],
                telephone = data['telephone'],
            )
            admin = Administrateur.objects.filter(pk=admin.id)
            serializer = AdministrateurSerializer(admin,many=True)
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

class AdministrateurApiDetails(APIView):

    #authentication_classes = [TokenAuthentication]
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
                user.groups.add(Group.objects.filter(name="Administrateur").first().id)

                us = User.objects.filter(email = data['email'])
                if us.exists() and us.first().id != admin.user.id:
                    i = 1
                    email_ = data['email']+"/"+str(i)
                    use = User.objects.filter(email = email_)
                    while use.exists() and use.first().id != admin.user.id:
                        i = i+1
                        email_ = data['email']+"/"+str(i)
                        use = User.objects.filter(email = email_)
                    user.email = email_
                else:
                    user.email = data['email']
                    
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

class UserrechercheApi(APIView):
    def post(self,request):
        data = request.data
        

