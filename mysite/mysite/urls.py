from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login_user', views.login_user, name="login_user"),
    path('signup_user', views.signup_user, name="signup_user"),
    path("user_login/", views.user_login, name="user_login"),
    path('create_set/', views.create_set, name='create_set'),
    path('account_delete', views.account_delete, name="account_delete"),
    path('delete_account', views.delete_account, name="delete_account"),
    path('delete_set/<int:set_id>/', views.delete_set, name='delete_set'),  # Ensure consistency here
    path('library/', views.library_view, name="library_view"),
    path('settings/', views.settings, name="settings"),
    path('flashcard-set/<int:set_id>/', views.view_flashcard_set, name='view_flashcard_set'),  # Detailed view URL
    path('about/', views.about, name="about"),
    path('terms', views.terms, name="terms"),
    path('', include("django.contrib.auth.urls")),
    path('create_flashcard/', views.create_flashcard, name='create_flashcard'),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate_account"),
    path('favorite/<int:set_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_sets, name='favorite_sets'),
    path('', views.home, name='home'),
    path('delete_flashcard/<int:card_id>/', views.delete_flashcard, name='delete_flashcard'),
    path('logout/', LogoutView.as_view(next_page='login_user'), name="logout_user"),
    path('study/<int:set_id>/', views.study_view, name='study_view'),
    path('flashcards/<int:set_id>/details/', views.get_flashcard_set_details, name='flashcard_set_details'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_change_done/', views.password_change_done, name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='mysite/templates/registration/password_reset_form.html',
        email_template_name='password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password_reset_done/'
    ), name='password_reset'),
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

    # Add the new path for updating the last viewed set in session
    path('update_last_viewed_set/', views.update_last_viewed_set, name='update_last_viewed_set'),
    path('learn/', views.learn_view, name='learn_view'),
    path('update_learned_flashcards/', views.update_learned_flashcards, name='update_learned_flashcards'),
    path('review/<int:set_id>/', views.review_view, name='review_view'),
    path('update_flashcard_level/<int:card_id>/<str:action>/', views.update_flashcard_level, name='update_flashcard_level'),
    path('mark_flashcard_as_learned/<int:card_id>/', views.mark_flashcard_as_learned, name='mark_flashcard_as_learned'),
    path('update_flashcard_review/<int:card_id>/', views.update_flashcard_review, name='update_flashcard_review'),
    path('classrooms/', views.classrooms_view, name="classrooms_view"),
    path('classrooms/', views.classrooms_view, name='classrooms_view'),
    path('classrooms/create/', views.create_classroom, name='create_classroom'),
    path('classrooms/<int:classroom_id>/', views.view_classroom, name='view_classroom'),
    path('classrooms/<int:classroom_id>/delete/', views.delete_classroom, name='delete_classroom'),
]
