from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User  # Use the built-in User model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from mysite.models import FlashcardSet, Category, Flashcard
from .forms import FlashcardForm
from django.http import JsonResponse


# Create a new user
@login_required
def home(request):
    return render(request, 'Home.html')

@login_required
def library_view(request):
    # Fetch only the flashcard sets that belong to the logged-in user
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)
    return render(request, 'Library.html', {'flashcard_sets': flashcard_sets})

@login_required
def settings(request):
    return render(request, 'Settings.html')

def login_user(request):
    return render(request, 'login.html', {})  # Render the login page

def signup_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Check if user already exists
        if User.objects.filter(username=username).exists():  # Use the built-in User model
            messages.error(request, "Username already taken")
            return redirect("signup_user")

        if User.objects.filter(email=email).exists():  # Use the built-in User model
            messages.error(request, "Email already in use")
            return redirect("signup_user")

        # Hash the password before storing it (handled by Django)
        user = User.objects.create_user(username=username, email=email, password=password)

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login_user")  # Redirect to login page after signup

    return render(request, "sign_up.html")  # Render the signup page

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate using the built-in Django User model
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log the user in using Django's built-in login method
            messages.success(request, "Login successful!")
            return redirect('home')  # Redirect to home after successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_user')  # Redirect back to login

    return render(request, 'login.html')  # Render login page for GET request

@login_required
def create_deck(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category_name = request.POST.get('category')  # This is a string from the form
        description = request.POST.get('description')

        if title and category_name:  # Ensure required fields are filled
            category, created = Category.objects.get_or_create(name=category_name)

            # Create the FlashcardSet and associate it with the logged-in user
            flashcard_set = FlashcardSet(
                title=title,
                category=category,  # Assign Category instance, not string
                description=description,
                user=request.user  # Associate the current user with the flashcard set
            )
            flashcard_set.save()
            return redirect('library_view')  # Redirect to library view after saving the deck

        else:
            error_message = "Please fill in all required fields."
            return render(request, 'Deck.html', {'error_message': error_message})

    return render(request, 'Deck.html')

@login_required
def view_flashcard_set(request, set_id):
    # Fetch the FlashcardSet by its set_id instead of id
    flashcard_set = FlashcardSet.objects.get(set_id=set_id)  # Use 'set_id' as the primary key field name

    # Fetch the flashcards related to this set
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)  # Assuming 'flashcard_set' is the field in Flashcard model

    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})

@login_required
def delete_deck(request, deck_id):
    deck = get_object_or_404(FlashcardSet, set_id=deck_id)  # Ensure 'set_id' is consistent here
    deck.delete()  # Delete the deck
    return redirect('library_view')  # Redirect back to the library view

@login_required
def create_flashcard(request):
    # If the request is POST, process the form
    if request.method == 'POST':
        form = FlashcardForm(request.POST)
        if form.is_valid():
            flashcard_set = form.cleaned_data['flashcard_set']
            
            # Ensure that the flashcard set belongs to the current user
            if flashcard_set.user == request.user:
                print("SUCCESS")
                form.save()  # Save the flashcard
                return redirect('home')  # Redirect after successful form submission
        else:
            print("Form errors:", form.errors)
    else:
        form = FlashcardForm()

    # Filter to show only the flashcard sets that belong to the current user
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)
    
    # Set the queryset for the flashcard_set field in the form dynamically
    form.fields['flashcard_set'].queryset = flashcard_sets
    
    return render(request, 'create_flashcard.html', {'form': form, 'flashcard_sets': flashcard_sets})

@login_required
def get_flashcard_set_details(request, set_id):

    print("Existing FlashcardSet IDs:", list(FlashcardSet.objects.values_list('set_id', flat=True)))

    try:
        flashcard_set = FlashcardSet.objects.get(set_id=set_id)
    except FlashcardSet.DoesNotExist:
        return JsonResponse({'error': f'Flashcard set with ID {set_id} not found'}, status=404)

    print("we got here 1")
    flashcard_set = FlashcardSet.objects.get(set_id=set_id)
    print("we got here 2")
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    print("we got here 3")
    flashcards_data = [{'question': fc.question, 'answer': fc.answer} for fc in flashcards]

    data = {
        'title': flashcard_set.title,
        'flashcards': flashcards_data
    }

    return JsonResponse(data)
