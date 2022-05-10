from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import ClientApi,ClientApiDetails
from rest_framework.authtoken import views


urlpatterns = [
    path('viewset/client/', ClientApi.as_view()),
    path('viewset/client/<int:id>', ClientApiDetails.as_view()),
]