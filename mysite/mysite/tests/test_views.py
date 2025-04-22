import pytest
from django.contrib.auth.models import User
from django.urls import reverse

@pytest.mark.django_db
def test_signup_user(client):
    """Test user registration."""
    response = client.post(reverse('signup_user'), {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123',
        'password_confirm': 'securepassword123',  # Required
        'role': 'student'  # Required
    })

    # Ensure user is created in the database
    assert User.objects.filter(username='testuser').exists()

    # Check for redirect to login page after signup
    assert response.status_code == 302  # Redirect
    assert response.url == reverse('login_user')


@pytest.mark.django_db
def test_user_login(client):
    """Test user login with valid and invalid credentials."""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='securepassword123')

    # Correct credentials
    response = client.post(reverse('user_login'), {
        'username': 'testuser',
        'password': 'securepassword123'
    })
    
    assert response.status_code == 302  # Redirect to home
    assert response.url == reverse('home')

    # Incorrect credentials
    response = client.post(reverse('user_login'), {
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 200  # Redirect back to login
    assert b'Invalid username or password' in response.content