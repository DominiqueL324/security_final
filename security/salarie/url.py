from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import SalarieApi,SalarieApiDetails
from rest_framework.authtoken import views


urlpatterns = [
    path('login/',views.obtain_auth_token),
    path('viewset/salarie/', SalarieApi.as_view()),
    path('viewset/salarie/<int:id>', SalarieApiDetails.as_view()),
]