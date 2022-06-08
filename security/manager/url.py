from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import RoleManager, Logout, checkUsernameApi,getAllUserApi
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import(TokenObtainPairView, TokenRefreshView,TokenVerifyView)



urlpatterns = [
    path('login/',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/',Logout.as_view()),
    path('viewset/role/', RoleManager.as_view()),
    path('viewset/checker/', checkUsernameApi.as_view()),
    path('viewset/users/', getAllUserApi.as_view()),
]