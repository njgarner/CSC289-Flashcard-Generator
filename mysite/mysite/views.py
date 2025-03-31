from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .models import FlashcardSet, Category, Flashcard, FavoriteSet
from .forms import FlashcardForm, ChangePasswordForm
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.core.exceptions import *

# ======================== Main Pages ======================== #

@login_required  # Home page
def home(request):
    # Get favorite sets for the current user
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related("set")

    # Get Flashcard sets for the current user
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)

    # Render the home page with favorite_sets in the context
    return render(request, "home.html", {"flashcard_sets": flashcard_sets, "favorite_sets": favorite_sets})

@login_required
def library_view(request):
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)
    favorites = FavoriteSet.objects.filter(user=request.user).select_related('set')

    # Get a list of favorited set IDs for easy lookup
    favorite_set_ids = set(favorite.set.set_id for favorite in favorites)

    return render(request, 'library.html', {
        'flashcard_sets': flashcard_sets,
        'favorites': favorites,
        'favorite_set_ids': favorite_set_ids  # Pass the IDs to the template
    })

@login_required  # About Us page
def about(request):
    return render(request, 'about_us.html')

@login_required  # Terms and conditions page
def terms(request):
    return render(request, 'terms.html')

@login_required
def settings(request):
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
    return render(request, 'settings.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # User acount deletion page
def account_delete(request):
    return render(request, 'account_delete.html')

# ======================== User Authentication (Signup, Login, Logout) ======================== #

def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # To keep the user logged in
            return redirect('password_change_done')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
                return redirect('change-password/change_password.html')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'change-password/change_password.html', {'form': form})

def password_change_done(request):
    return render(request, 'change-password/password_change_done.html')

def add_sample_decks_and_cards(user):
    sample_decks = [
        {
            "title": "Country Capitals",
            "category": "Geography",
            "description": "A random assortment of countries and their capitals.",
            "cards": [
                {"question": "What is the capital of France?", "answer": "Paris"},
                {"question": "What is the capital of Sweden?", "answer": "Stockholm"},
                {"question": "What is the capital of Saudi Arabia?", "answer": "Riyadh"},
                {"question": "What is the capital of Japan?", "answer": "Tokyo"},
                {"question": "What is the capital of Mexico?", "answer": "Mexico City"},
                {"question": "What is the capital of Canada?", "answer": "Ottawa"},
                {"question": "What is the capital of China?", "answer": "Beijing"},
                {"question": "What is the capital of Egypt?", "answer": "Cairo"}
            ]
        },
        {
            "title": "Great Battles",
            "category": "History",
            "description": "A random assortment of battles and the wars they are from.",
            "cards": [
                {"question": "During which war was the battle of Iwo Jima fought?", "answer": "World War II"},
                {"question": "During which war was the battle of Gettysburg fought?", "answer": "The American Civil War"},
                {"question": "During which war was the battle of Trenton fought?", "answer": "The American Revolutionary War"},
                {"question": "During which war was the battle of Verdun fought?", "answer": "World War I"},
                {"question": "During which war was the battle of Thermopylae fought?", "answer": "The Greco-Persian Wars"},
                {"question": "During which war was the battle of San Juan Hill fought?", "answer": "The Spanish-American War"}
            ]
        },
    ]

    for deck in sample_decks:
        category, _ = Category.objects.get_or_create(name=deck["category"])
        flashcard_set = FlashcardSet.objects.create(
            title=deck["title"], 
            category=category, 
            description=deck["description"], 
            user=user
        )
        for card in deck["cards"]:
            Flashcard.objects.create(
                flashcard_set=flashcard_set,
                question=card["question"],
                answer=card["answer"],
                user=user
            )

def login_user(request):  # Login page
    return render(request, 'login.html')

def custom_logout(request):  # Logs out the user
    logout(request)
    return redirect('login_user')

def signup_user(request):  # Signup page with email verification
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect("signup_user")

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_active=False
        )

        # Add sample decks for the new user
        add_sample_decks(user)

        # Email verification setup
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"http://{get_current_site(request).domain}/activate/{uid}/{token}/"
        
        html_message = render_to_string("email_verification.html", {
            "username": username,
            "verification_link": verification_link
        })
        
        email_message = EmailMultiAlternatives(
            subject="Verify Your Email - Flashcard App",
            body=strip_tags(html_message),
            from_email="noreply@yourdomain.com",
            to=[email]
        )
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()

        messages.success(request, "Check your email for verification.")
        return redirect("login_user")

    return render(request, "sign_up.html")

def activate_account(request, uidb64, token):  # Activates user account via email link
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated! You can now log in.")
        return redirect("login_user")
    else:
        messages.error(request, "Invalid or expired activation link.")
        return redirect("signup_user")

def user_login(request):  # Logs in user
    if request.method == 'POST':
        user = authenticate(
            request, 
            username=request.POST.get('username'), 
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_user')
    return render(request, 'login.html')

def delete_account(request):
    if request.method == 'POST':
        deleteUser = User.objects.get(username=request.user)
        deleteUser.delete()
        messages.success(request, "Account deleted! You can now create a new account.")
        return redirect('sign_up.html')
    
    return render(request, 'account_delete.html')

# ======================== Flashcard set Management ======================== #

@login_required  # Create a new set
def create_set(request):
    # Get favorite sets for the current user
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')

    if request.method == 'POST':
        title, category_name, description = (
            request.POST.get('title'), 
            request.POST.get('category'), 
            request.POST.get('description')
        )
        
        if title and category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            FlashcardSet.objects.create(
                title=title, category=category, description=description, user=request.user
            )
            return redirect('library_view')
        messages.error(request, "Please fill in all required fields.")

    return render(request, 'create_set.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # View flashcard set details
def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})

@login_required  # Delete a set
def delete_set(request, set_id):
    get_object_or_404(FlashcardSet, set_id=set_id).delete()
    return redirect('library_view')

@login_required
def toggle_favorite(request, set_id):
    set = get_object_or_404(FlashcardSet, set_id=set_id)
    favorite, created = FavoriteSet.objects.get_or_create(user=request.user, set=set)
    
    if not created:
        favorite.delete()
        return JsonResponse({"favorited": False})

    return JsonResponse({"favorited": True})

@login_required
def favorite_sets(request):
    favorites = FavoriteSet.objects.filter(user=request.user).select_related('set')
    print(f"Favorite sets: {favorite_sets}")
    return render(request, 'home.html', {'favorites': favorites})

# ======================== Flashcard Management ======================== #

@login_required  # Create a flashcard
def create_flashcard(request):
    form = FlashcardForm(request.POST or None)
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')

    if request.method == 'POST' and form.is_valid():
        flashcard_set = form.cleaned_data['flashcard_set']
        if flashcard_set.user == request.user:
            form.save()
            return redirect('home')

    form.fields['flashcard_set'].queryset = FlashcardSet.objects.filter(user=request.user)

    return render(request, 'create_flashcard.html', {
        'form': form,
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # View flashcard deck details
def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})

@login_required  # Delete a flashcard
def delete_flashcard(request, card_id):
    get_object_or_404(Flashcard, card_id=card_id).delete()
    return redirect('library_view')

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

# ======================== Study Mode ======================== #

@login_required  # Study flashcards in a set
def study_view(request, set_id):
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id, user=request.user)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)

    # Get favorite sets for the current user
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')

    return render(request, 'home.html', {
        "flashcard_set": flashcard_set,
        "flashcards": flashcards,
        "favorite_sets": favorite_sets,  # Pass favorite sets to the template
        "flashcard_sets": flashcard_sets,
    })
