import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from mysite.models import FlashcardSet, Flashcard, Category
from mysite import views

@pytest.mark.django_db
def test_create_set(client, django_user_model):
    """Test that a logged-in user can create a flashcard deck."""
    user = django_user_model.objects.create_user(username="testuser", password="password123")
    client.login(username="testuser", password="password123")

    response = client.post(reverse('create_set'), {
        'title': 'Test Deck',
        'category': 'Science',
        'description': 'A sample Set'
    })

    assert response.status_code == 302  # Redirect to library view
    assert FlashcardSet.objects.filter(title='Test Deck', user=user).exists()

@pytest.mark.django_db
def test_delete_set(client, django_user_model):
    """Test that a user can delete their flashcard deck."""
    user = django_user_model.objects.create_user(username="testuser", password="password123")
    client.login(username="testuser", password="password123")

    category = Category.objects.create(name="Science")
    deck = FlashcardSet.objects.create(title="My Set", category=category, user=user)

    response = client.post(reverse('delete_set', args=[deck.set_id]))

    assert response.status_code == 302  # Redirect after delete
    assert not FlashcardSet.objects.filter(title="My Set").exists()