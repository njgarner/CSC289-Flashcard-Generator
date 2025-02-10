from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Users, Flashcard, FlashcardSet, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 

# Create a new user

def home(request):
    return render(request, 'Home.html')

def library_view(request):
    flashcard_sets = FlashcardSet.objects.all()  # Fetch all FlashcardSets
    return render(request, 'Library.html', {'flashcard_sets': flashcard_sets})  # Pass the data to the template

def settings(request):
    return render(request, 'Settings.html')

def login_user(request):
    return render(request, 'login.html', {})  # Render the login page

def signup_user(request):
    return render(request, 'sign_up.html', {}) # render the signup page

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        try:
            # Use correct parameter names to get user
            user = Users.userAuth_objects.get(username=username, password=password)
            
            # Check if user exists
            if user is not None:
                login(request, user)
                return redirect('Home.html')
                
            else:
                messages.success(request, "Failure to login. Please check your credentials.")
                return redirect('login.html')  # Redirect back to the login page

        except Exception as identifier:
            messages.success(request, "Error logging in.")
            return redirect('login.html')  # Redirect back to the login page
    
    else:
        return render(request, 'login.html')  # Render the login page for GET request

def create_deck(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category_name = request.POST.get('category')  # This is a string from the form
        description = request.POST.get('description')

        if title and category_name:  # Ensure required fields are filled
            category, created = Category.objects.get_or_create(name=category_name)

            flashcard_set = FlashcardSet(
                title=title,
                category=category,  # Assign Category instance, not string
                description=description
            )
            flashcard_set.save()
            return redirect('library_view')

        else:
            error_message = "Please fill in all required fields."
            return render(request, 'Deck.html', {'error_message': error_message})

    return render(request, 'Deck.html')

def view_flashcard_set(request, set_id):
    flashcard_set = FlashcardSet.objects.get(set_id=set_id)  # Get the FlashcardSet by its ID
    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set})

def delete_deck(request, deck_id):
    deck = get_object_or_404(FlashcardSet, set_id=deck_id)  # Ensure 'set_id' is consistent here
    deck.delete()  # Delete the deck
    return redirect('library_view')  # Redirect back to the library view

