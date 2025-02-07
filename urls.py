from django.urls import path
from . import views

urlpatterns = [
    path('login_user',views.Home,name="Home"),
    path("user_login/",views.user_login,name="user_login"),
]