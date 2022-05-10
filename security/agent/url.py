from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import AgentApi,AgentApiDetails
from rest_framework.authtoken import views


urlpatterns = [
    path('viewset/agent/', AgentApi.as_view()),
    path('viewset/agent/<int:id>', AgentApiDetails.as_view()),
]