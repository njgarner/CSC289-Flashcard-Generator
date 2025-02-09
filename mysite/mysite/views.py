from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Users, Flashcard, FlashcardSet, Category
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'Home.html')

def library_view(request):
    return render(request, 'Library.html')

def settings(request):
    return render(request, 'Settings.html')

def login_user(request):
    return render(request, 'login.html', {})  # Render the login page

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Use correct parameter names to get user
            user = Users.userAuth_objects.get(username=username, password=password)
            
            # Check if user exists
            if user is not None:
                return redirect('home')
                
            else:
                messages.error(request, "Failure to login. Please check your credentials.")
                return redirect('login_user')  # Redirect back to the login page

        except Exception as identifier:
            messages.error(request, "Error logging in.")
            return redirect('login_user')  # Redirect back to the login page
    
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
            return redirect('deck_list')

        else:
            error_message = "Please fill in all required fields."
            return render(request, 'deck.html', {'error_message': error_message})

    return render(request, 'deck.html')

def deck_list(request):
    decks = FlashcardSet.objects.all()  # Get all flashcard decks
    return render(request, 'deck_list.html', {'decks': decks})

def delete_deck(request, deck_id):
    deck = get_object_or_404(FlashcardSet, set_id=deck_id)  # Get the deck or return 404
    deck.delete()  # Delete the deck
    return redirect('deck_list')  # Redirect back to the list of decks
