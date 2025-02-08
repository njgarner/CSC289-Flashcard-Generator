from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Users, Flashcard, FlashcardSet
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

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
    
def view_html(request):
    return render(request, 'deck.html')

def create_deck(request):
    if request.method == 'POST':
        # Get data from the POST request
        title = request.POST.get('title')  # Get deck name
        category = request.POST.get('category')  # Get category
        description = request.POST.get('description')  # Get description

        # You may also want to add custom validation here
        if title and category:  # Simple validation
            flashcard_set = FlashcardSet(
                title=title,
                category=category,
                description=description,
                user=request.user  # Associate with the logged-in user
            )
            flashcard_set.save()
            return redirect('deck_list')  # Redirect to the list of decks
        else:
            # Handle the case where required fields are missing
            error_message = "Please fill in all required fields."
            return render(request, 'deck.html', {'error_message': error_message})

    return render(request, 'deck.html')