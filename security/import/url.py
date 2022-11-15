from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import ImportApi 
from rest_framework.authtoken import views


urlpatterns = [
    path('viewset/import/', ImportApi.as_view()),
]