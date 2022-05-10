from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import RoleManager, Logout, checkUsernameApi
from rest_framework.authtoken import views


urlpatterns = [
    path('login/',views.obtain_auth_token),
    path('logout/',Logout.as_view()),
    path('viewset/role/', RoleManager.as_view()),
    path('viewset/checker/', checkUsernameApi.as_view()),
]