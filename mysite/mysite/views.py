from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User  # Use the built-in User model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from .models import FlashcardSet, Category, Flashcard
from .forms import FlashcardForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator

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

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def custom_logout(request):
    logout(request)
    return redirect('login_user')  # Redirect to your login page

# def delete_user(request):

def signup_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect("signup_user")

        # Create inactive user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),  # Hash the password
            is_active=False  # User is inactive until they verify email
        )

        # Generate email verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        verification_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

        # Render the email template
        html_message = render_to_string("email_verification.html", {
            "username": username,
            "verification_link": verification_link
        })

        # Convert HTML to plain text
        plain_message = strip_tags(html_message)

        # Use EmailMultiAlternatives to send an HTML email
        email_message = EmailMultiAlternatives(
            subject="Verify Your Email - Flashcard App",
            body=plain_message,  # Plain text version
            from_email="noreply@yourdomain.com",
            to=[email]
        )
        email_message.attach_alternative(html_message, "text/html")  # Attach the HTML version
        email_message.send()

        messages.success(request, "An email has been sent for verification. Please check your inbox.")
        return redirect("login_user")

    return render(request, "sign_up.html")

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the account
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect("login_user")
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect("signup_user")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate using the built-in Django User model
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log the user in using Django's built-in login method
            # messages.success(request, "Login successful!")
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

def delete_flashcard(request, card_id):
    flashcard = get_object_or_404(Flashcard, card_id=card_id)
    flashcard.delete()
    return redirect('library_view')  # Change this as needed
