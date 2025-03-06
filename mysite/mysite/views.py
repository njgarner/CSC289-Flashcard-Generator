from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from mysite.models import FlashcardSet, Category, Flashcard
from .forms import FlashcardForm
from django.http import JsonResponse

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags

# ======================== Main Pages ======================== #

@login_required  # Home page
def home(request):
    return render(request, 'Home.html')

@login_required  # Library page showing user's decks
def library_view(request):
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)
    return render(request, 'Library.html', {'flashcard_sets': flashcard_sets})

@login_required  # About Us page
def about(request):
    return render(request, 'About_Us.html')

@login_required  # Terms and conditions page
def terms(request):
    return render(request, 'Terms.html')

@login_required  # User settings page
def settings(request):
    return render(request, 'Settings.html')

# ======================== User Authentication (Signup, Login, Logout) ======================== #

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

# ======================== Flashcard Deck Management ======================== #

@login_required  # Create a new deck
def create_deck(request):
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
    return render(request, 'Deck.html')

@login_required  # View flashcard deck details
def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})

@login_required  # Delete a deck
def delete_deck(request, deck_id):
    get_object_or_404(FlashcardSet, set_id=deck_id).delete()
    return redirect('library_view')

# ======================== Flashcard Management ======================== #

@login_required  # Create a flashcard
def create_flashcard(request):
    form = FlashcardForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        flashcard_set = form.cleaned_data['flashcard_set']
        if flashcard_set.user == request.user:
            form.save()
            return redirect('home')
    form.fields['flashcard_set'].queryset = FlashcardSet.objects.filter(user=request.user)
    return render(request, 'create_flashcard.html', {'form': form})

@login_required  # Delete a flashcard
def delete_flashcard(request, card_id):
    get_object_or_404(Flashcard, card_id=card_id).delete()
    return redirect('library_view')

# ======================== Study Mode ======================== #

@login_required  # Study flashcards in a deck
def study_view(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id, user=request.user)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    return render(request, 'Home.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})
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