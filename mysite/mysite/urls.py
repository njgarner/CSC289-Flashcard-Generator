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
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("guest-login/", views.guest_login, name="guest_login"),
    path('login_user', views.login_user, name="login_user"),
    path('signup_user', views.signup_user, name="signup_user"),
    path("user_login/", views.user_login, name="user_login"),
    path('create_set/', views.create_set, name='create_set'),
    path('account_delete', views.account_delete, name="account_delete"),
    path('delete_account', views.delete_account, name="delete_account"),
    path('delete_set/<int:set_id>/', views.delete_set, name='delete_set'),  # Ensure consistency here
    path('library/', views.library_view, name="library_view"),
    path('settings/', views.settings, name="settings"),
    path('schedule/', views.schedule, name="schedule"),
    path("send-reminder-email/", views.send_reminder_email, name="send_reminder_email"),
    path('customize/', views.customize, name="customize"),
    path('flashcard-set/<int:set_id>/', views.view_flashcard_set, name='view_flashcard_set'),  # Detailed view URL
    path('about/', views.about, name="about"),
    path('terms', views.terms, name="terms"),
    path('', include("django.contrib.auth.urls")),
    path('create_flashcard/', views.create_flashcard, name='create_flashcard'),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate_account"),
    path("toggle_favorite/<int:set_id>/", views.toggle_favorite, name="toggle_favorite"),
    path('favorites/', views.favorite_sets, name='favorite_sets'),
    path('', views.home, name='home'),
    path('delete_flashcard/<int:card_id>/', views.delete_flashcard, name='delete_flashcard'),
    path('edit_flashcard/<int:card_id>/', views.edit_flashcard, name='edit_flashcard'),
    path('edit-set/<int:set_id>/', views.edit_set, name='edit_set'),
    path('logout/', LogoutView.as_view(next_page='login_user'), name="logout_user"),
    path('study/<int:set_id>/', views.study_view, name='study_view'),
    path('update_last_viewed_set/', views.update_last_viewed_set, name='update_last_viewed_set'),
    path('update_last_viewed_set/', views.update_last_viewed_set, name='update_last_viewed_set'),
    path('learn/', views.learn_view, name='learn_view'),
    path('update_learned_flashcards/', views.update_learned_flashcards, name='update_learned_flashcards'),
    path('review/<int:set_id>/', views.review_view, name='review_view'),
    path('update_flashcard_level/<int:card_id>/<str:action>/', views.update_flashcard_level, name='update_flashcard_level'),
    path('mark_flashcard_as_learned/<int:card_id>/', views.mark_flashcard_as_learned, name='mark_flashcard_as_learned'),
    path('update_flashcard_review/<int:card_id>/', views.update_flashcard_review, name='update_flashcard_review'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_change_done/', views.password_change_done, name='password_change_done'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'), 
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/password_reset_complete/'
    ), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
