from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from .models import Flashcard, FlashcardSet, User

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ['flashcard_set', 'question', 'answer']  # Add any other fields you need

    # Remove the static queryset initialization; it'll be set in the view
    # flashcard_set = forms.ModelChoiceField(queryset=FlashcardSet.objects.none())  # No longer needed

class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_pass1', 'new_pass2']
    

class ResetPasswordForm(PasswordResetForm):
    class Meta:
        model = User
        fields = ['', '', '']
