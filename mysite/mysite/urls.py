from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login_user', views.login_user, name="login_user"),
    path('signup_user', views.signup_user, name="signup_user"),
    path("user_login/", views.user_login, name="user_login"),
    path('create_deck/', views.create_deck, name='create_deck'),
    path('delete_deck/<int:deck_id>/', views.delete_deck, name='delete_deck'),
    path('library/', views.library_view, name="library_view"),
    path('settings', views.settings, name="settings"),
    path('flashcard-set/<int:set_id>/', views.view_flashcard_set, name='view_flashcard_set'),
    path('about', views.about, name="about"),
    path('terms', views.terms, name="terms"),
    path('', include("django.contrib.auth.urls")),
    path('create_flashcard/', views.create_flashcard, name='create_flashcard'),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate_account"),
    path('delete_flashcard/<int:card_id>/', views.delete_flashcard, name='delete_flashcard'),
    path('logout/', LogoutView.as_view(next_page='login_user'), name="logout_user"),
    path('study/<int:set_id>/', views.study_view, name='study_view'),  # Specific route for studying a deck
    path('favorite/<int:deck_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_decks, name='favorite_decks'),
    path('', views.home, name='home'),  # Home page
]
