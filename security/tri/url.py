from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import FiltreAPI
from rest_framework.authtoken import views


urlpatterns = [
    path('viewset/tri/', FiltreAPI.as_view()),
]
