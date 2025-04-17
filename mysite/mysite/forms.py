from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from .models import Flashcard, FlashcardSet, User

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ['question', 'answer'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question'].widget.attrs.update({
            'maxlength': 200,
            'placeholder': 'Enter question (max 200 characters)',
        })
        self.fields['answer'].widget.attrs.update({
            'maxlength': 200,
            'placeholder': 'Enter answer (max 200 characters)',
        })

class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_pass1', 'new_pass2']
    

class ResetPasswordForm(PasswordResetForm):
    class Meta:
        model = User
        fields = ['', '', '']
