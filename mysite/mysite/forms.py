from django import forms
from .models import Flashcard, FlashcardSet

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ['flashcard_set', 'question', 'answer']  # Add any other fields you need

    # Remove the static queryset initialization; it'll be set in the view
    # flashcard_set = forms.ModelChoiceField(queryset=FlashcardSet.objects.none())  # No longer needed
