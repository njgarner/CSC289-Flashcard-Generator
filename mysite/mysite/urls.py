"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login_user', views.login_user, name="login_user"),
    path('signup_user', views.signup_user, name="signup_user"),
    path("user_login/", views.user_login, name="user_login"),
    path('create_deck/', views.create_deck, name='create_deck'),
    path('delete_deck/<int:deck_id>/', views.delete_deck, name='delete_deck'),  # Ensure consistency here
    path('home', views.home, name="home"),
    path('library/', views.library_view, name="library_view"),
    path('settings', views.settings, name="settings"),
    path('flashcard-set/<int:set_id>/', views.view_flashcard_set, name='view_flashcard_set'),  # Detailed view URL
    path('', include("django.contrib.auth.urls")),
    path('create_flashcard/', views.create_flashcard, name='create_flashcard'),
    path('flashcards/<int:set_id>/details/', views.get_flashcard_set_details, name='flashcard_set_details'),

]



