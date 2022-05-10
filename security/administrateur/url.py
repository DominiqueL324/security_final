from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import AdministrateurApiDetails,AdministrateurApi
from rest_framework.authtoken import views


urlpatterns = [
    path('viewset/administrateur/', AdministrateurApi.as_view()),
    path('viewset/administrateur/<int:id>', AdministrateurApiDetails.as_view()),
]