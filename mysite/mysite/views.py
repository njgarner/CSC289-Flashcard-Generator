from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils.text import Truncator
from django.urls import reverse
from django.contrib.auth.views import PasswordResetView  
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.core.exceptions import *
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from collections import defaultdict
from django.db.models import Q
import pandas as pd
import tempfile
import json
import os
import logging

# ======================= Python files ======================= #

logger = logging.getLogger(__name__)

from .models import FlashcardSet, Category, Flashcard, FavoriteSet, UserActivity, Classroom, UserProfile, Quiz, QuizResult, SavedSet, Reminder
from .forms import FlashcardForm, ChangePasswordForm
from .tasks import send_reminder_email_task

# ======================= Time Management ======================= #

import datetime
from django.utils import timezone
from django.utils.timezone import is_naive, make_aware, now
from datetime import timedelta, datetime

# ======================== Main Pages ======================== #

def home(request):
    # Home page view, allowing guest access with limited features.
    
    # If the user is not authenticated, provide limited access
    if not request.user.is_authenticated:
        return render(request, "home.html", {
            "flashcard_sets": [],
            "favorite_sets": [],
            "last_viewed_set": None,
            "flashcards": [],
            "remaining_cards": 0,
            "reviewable_cards_count": 0,
            "is_guest": True,  # Send a flag to the template
        })

    # Get recent sets (by ID from session)
    recent_ids = request.session.get("recent_sets", [])
    recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids, user=request.user))

    # Sort them to match the order in session
    recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))

    # Get Flashcard sets for the current user
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)

    # Retrieve the last viewed set from session
    last_viewed_set_id = request.session.get("last_viewed_set_id", None)
    last_viewed_set = None
    flashcards = Flashcard.objects.none()

    if last_viewed_set_id:
        # Get the last viewed set for the current user
        last_viewed_set = FlashcardSet.objects.filter(user=request.user, set_id=last_viewed_set_id).first()
        if last_viewed_set:
            # Truncate the title of the last viewed set to 25 characters
            last_viewed_set.title = Truncator(last_viewed_set.title).chars(25)

            # Get the flashcards for the last viewed set
            flashcards = last_viewed_set.flashcard_set.all()

    # Count the flashcards that are ready for review (next_review_date is <= now)
    reviewable_cards = flashcards.filter(next_review_date__lte=timezone.now())

    # Count the number of flashcards with is_learned=False
    remaining_cards = flashcards.filter(is_learned=False).count()

    # Render the home page with all necessary context
    return render(request, "home.html", {
      "flashcard_sets": flashcard_sets,
      "recent_sets": recent_sets,
      "last_viewed_set": last_viewed_set,
      "flashcards": flashcards,
      "remaining_cards": remaining_cards,
      "reviewable_cards_count": reviewable_cards.count(),
      "is_guest": False,
    })

@login_required
def update_last_viewed_set(request):
    if request.method == "POST":
        data = json.loads(request.body)
        set_id = data.get('set_id')

        # Save the selected set's ID in the session
        request.session['last_viewed_set_id'] = set_id

        return JsonResponse({"status": "success"})
    
@login_required
def library_view(request):
    # All sets from the user
    all_sets = FlashcardSet.objects.filter(user=request.user).select_related('category')

    # Get favorite IDs
    favorites = FavoriteSet.objects.filter(user=request.user).select_related('set')
    favorite_set_ids = set(fav.set.set_id for fav in favorites)

    # Combine and group by category
    categorized_sets = defaultdict(list)
    for flashcard_set in all_sets:
        category = flashcard_set.category.name if flashcard_set.category else "Uncategorized"
        categorized_sets[category].append(flashcard_set)

    # Recent sets
    recent_ids = request.session.get("recent_sets", [])
    recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids, user=request.user))
    recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))

    # Get classroom-assigned sets (if user is a student)
    try:
        profile = request.user.userprofile
        if profile.role == 'student':
            # Get all classrooms the student is in
            classrooms = Classroom.objects.filter(students=request.user)
            # Gather all flashcard sets assigned through these classrooms
            assigned_sets = FlashcardSet.objects.filter(classrooms__in=classrooms).distinct()
            # Remove any the user already owns or has favorited
            assigned_sets = assigned_sets.exclude(user=request.user).exclude(set_id__in=favorite_set_ids)
        else:
            assigned_sets = FlashcardSet.objects.none()
    except UserProfile.DoesNotExist:
        assigned_sets = FlashcardSet.objects.none()

    return render(request, 'library.html', {
        'flashcard_sets': all_sets,
        'favorites': favorites,
        'favorite_set_ids': favorite_set_ids,
        'favorite_flashcard_sets': all_sets.filter(set_id__in=favorite_set_ids),
        'categorized_sets': categorized_sets,
        'set_count': all_sets.count(),
        'favorite_count': len(favorite_set_ids),
        'recent_sets': recent_sets,
        'assigned_sets': assigned_sets,
    })

# About Us Page
def about(request):
    is_guest = not request.user.is_authenticated

    # Get recent sets only if the user is logged in
    recent_sets = []
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids, user=request.user))
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))

    return render(request, 'about_us.html', {
        'recent_sets': recent_sets,
        'is_guest': is_guest,
    })

# Terms and conditions page
def terms(request):
    return render(request, 'terms.html')

@login_required
def settings(request):
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'settings.html', {
    'recent_sets': recent_sets # Pass recent sets to the template
    })

@csrf_exempt
def toggle_background(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session["color_background"] = data.get("enabled", False)
        request.session.modified = True
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required  # Schedule study time page
def schedule(request):
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'study_schedule.html', {
    'recent_sets': recent_sets # Pass recent sets to the template
    })

@csrf_exempt
def create_reminder(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            data = json.loads(request.body)

            date_time_str = data.get("date_time")
            if not date_time_str:
                raise ValueError("Missing or invalid date_time value")

            # Convert to aware datetime
            naive_datetime = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
            date_time = timezone.make_aware(naive_datetime)

            reminder = Reminder.objects.create(
                user=request.user,
                title=data["title"],
                description=data["description"],
                date_time=date_time,
                email=data.get("email"),
                email_reminder=data.get("emailReminder", False),
            )

            # Schedule the email reminder task
            if reminder.email_reminder:
                send_reminder_email_task.apply_async(args=[reminder.id], eta=reminder.date_time)

            return JsonResponse({"success": True})

        except ValueError as e:
            return JsonResponse({"error": "Invalid data", "message": str(e)}, status=400)

        except Exception as e:
            return JsonResponse({"error": "Failed to create reminder", "message": str(e)}, status=500)

    return JsonResponse({"error": "Unauthorized or invalid request"}, status=400)

def due_reminders(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)

    now = timezone.now()
    reminders = Reminder.objects.filter(
        user=request.user, date_time__lte=now, notified=False
    )

    # Mark as notified
    for r in reminders:
        r.notified = True
        r.save()

    return JsonResponse([
        {"title": r.title, "description": r.description}
        for r in reminders
    ], safe=False)

@login_required
def get_reminders(request):
    reminders = Reminder.objects.filter(user=request.user).order_by("date_time")
    data = [{
        "title": r.title,
        "description": r.description,
        "date_time": r.date_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "email_reminder": r.email_reminder,
        "email": r.email
    } for r in reminders]
    return JsonResponse(data, safe=False)

@login_required
def delete_reminder(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title")

        try:
            reminder = Reminder.objects.get(user=request.user, title=title)
            reminder.delete()
            return JsonResponse({"success": True})
        except Reminder.DoesNotExist:
            return JsonResponse({"success": False, "error": "Reminder not found."}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)

@login_required  # Customization page
def customize(request):
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'customize.html', {
    'recent_sets': recent_sets # Pass recent sets to the template
    })

@login_required  # User acount deletion page
def account_delete(request):
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'account_delete.html', {
    'recent_sets': recent_sets # Pass recent sets to the template
    })

def get_daily_quote():
    quotes = [
        "Believe you can and you're halfway there.",
        "Your limitation—it's only your imagination.",
        "Push yourself, because no one else is going to do it for you.",
        "Great things never come from comfort zones.",
        "Dream it. Wish it. Do it.",
        "Success doesn’t just find you. You have to go out and get it.",
        "The harder you work for something, the greater you’ll feel when you achieve it.",
        "Dream bigger. Do bigger.",
        "Don’t stop when you’re tired. Stop when you’re done.",
        "Wake up with determination. Go to bed with satisfaction."
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]

def send_reminder_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description")
            recipient_email = data.get("email")

            if not recipient_email:
                return JsonResponse({"error": "No email provided"}, status=400)

            subject = f"Study Reminder: {title}"
            message = f"Hey there!\n\nThis is a reminder for your scheduled study time.\n\nTitle: {title}\nDescription: {description}\n\nDon't forget to study! 📚"
            from_email = "noreply@yourdomain.com"
            recipient_list = [recipient_email]

            send_mail(subject, message, from_email, recipient_list)

            return JsonResponse({"message": "Reminder email sent successfully!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

class CustomPasswordResetView(PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    html_email_template_name = "registration/password_reset_email.html"
    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data["email"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return response  # Prevent revealing user existence

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = self.request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )

        html_message = render_to_string("registration/password_reset_email.html", {
            "username": user,
            "reset_link": reset_link,
        })

        plain_message = strip_tags(html_message)

        email_message = EmailMultiAlternatives(
            "Password Reset",
            plain_message,
            "noreply@yourdomain.com",
            [email]
        )
        email_message.attach_alternative(html_message, "text/html")
        email_message.content_subtype = "html"  # Explicitly set content type
        email_message.send()

        return response
    
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
                return redirect('change_password')
    else:
        form = ChangePasswordForm(request.user)

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'change-password/change_password.html', {
    'form': form,
    'recent_sets': recent_sets # Pass recent sets to the template
    })

def password_change_done(request):
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'change-password/password_change_done.html', {
    'recent_sets': recent_sets # Pass recent sets to the template
    })
    

def guest_login(request):
    # Logs in a user as a guest without requiring authentication.
    request.session["guest_user"] = True  # Mark session as guest
    messages.info(request, "You are browsing as a guest. Some features are restricted.")
    return redirect("home")  # Redirect to homepage or another allowed page

def login_user(request):  # Login page
    daily_quote = get_daily_quote()
    # print("Login view called. Daily Quote:", daily_quote)  # Debugging

    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html', {'daily_quote': daily_quote})

def custom_logout(request):  # Logs out the user
    if request.user.is_authenticated:
        logout(request)
        messages.add_message(request, messages.SUCCESS, "You have been logged out successfully!")
        return redirect('login_user')  # Redirects to login page with success message
    else:
        messages.add_message(request, messages.ERROR, "Logout failed. You were not logged in.")
        return redirect('home')  # Redirects to home page with failure message

def signup_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password_confirm = request.POST["password_confirm"]
        role = request.POST["role"]

        # Check if passwords match
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "sign_up.html", {
                "username": username,
                "email": email,
                "role": role
            })

        # Validate password using Django's built-in validators
        try:
            validate_password(password)
        except ValidationError as errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "sign_up.html", {
                "username": username,
                "email": email,
                "role": role
            })

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "sign_up.html", {
                "username": "",
                "email": email,
                "role": role
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return render(request, "sign_up.html", {
                "username": username,
                "email": "",
                "role": role
            })
        

        try:
            with transaction.atomic(): # Use a transaction for atomicity
                # Create the user first (save to the database)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=False  # User is inactive until email is verified
                )

                user_profile = UserProfile.objects.create(user=user, role=role)

                # Send verification email (similar to your existing code)
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
                return redirect(reverse('login_user')) # Use reverse to get the url from the name.

        except Exception as e:
            messages.error(request, f"An error occurred: {e}") # Log the error for debugging
            return render(request, "sign_up.html", {
                "username": username,
                "email": email,
                "role": role
            })
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
        # Add sample decks upon successful activation
        add_sample_sets_and_cards(user)
        messages.success(request, "Account activated! You can now log in.")
        return redirect("login_user")
    else:
        messages.error(request, "Invalid or expired activation link.")
        return redirect("signup_user")

def user_login(request):  # Logs in user
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', {"username": username})  # Preserve input

    return render(request, 'login.html')

def delete_account(request):
    if request.method == 'POST':
        deleteUser = User.objects.get(username=request.user)
        deleteUser.delete()
        messages.success(request, "Account deleted! You can now create a new account.")
        return redirect('signup_user')
    
    return render(request, 'account_delete.html')

# ======================== Flashcard Set Management ======================== #

def add_sample_sets_and_cards(user):
    sample_sets = [
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

    for sample_set in sample_sets:
        category, _ = Category.objects.get_or_create(name=sample_set["category"])

        # Check if this set already exists for the user
        if FlashcardSet.objects.filter(title=sample_set["title"], user=user).exists():
            # print(f"Flashcard Set '{sample_set['title']}' already exists for {user.username}, skipping...")
            continue

        flashcard_set = FlashcardSet.objects.create(
            title=sample_set["title"], 
            category=category, 
            description=sample_set["description"], 
            user=user
        )

        # print(f"Created Flashcard Set: {flashcard_set.title} for {user.username}")

        for card in sample_set["cards"]:
            Flashcard.objects.create(
                flashcard_set=flashcard_set,
                question=card["question"],
                answer=card["answer"],
            )

def create_set(request):
    set_count = FlashcardSet.objects.filter(user=request.user).count()
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    if set_count >= 100:  # Check if the user has reached the maximum number of sets (100)
        messages.error(request, "Maximum number of flashcard sets reached. Please delete an existing set before creating a new one.")
        return redirect('library_view')

    if request.method == 'POST':
        title = request.POST.get('title').strip()
        category_name = request.POST.get('category').strip()
        description = request.POST.get('description', '').strip()

        # Get the 'is_shared' value from the form
        is_shared = request.POST.get('is_shared') == 'on'

        # Validate if title and category are provided
        if title and category_name:
            # Check if a set with the same title already exists for this user
            if FlashcardSet.objects.filter(user=request.user, title__iexact=title).exists():
                messages.error(request, "A flashcard set with this title already exists. Please choose a different name.")
                return redirect('create_set')

            # Create or get the Category object
            category, created = Category.objects.get_or_create(name=category_name)

            # Create a new FlashcardSet
            FlashcardSet.objects.create(
                title=title, 
                category=category, 
                description=description, 
                user=request.user,
                is_shared=is_shared  # Save the 'is_shared' value
            )

            messages.success(request, "Flashcard set successfully created!")
            return redirect('library_view')
        
        # Add error message if title or category is missing
        messages.error(request, "Please fill in all required fields.")

    return render(request, 'create_set.html', {
    'recent_sets': recent_sets # Pass recent sets to the template
    })

def flashcard_details_json(request, set_id):
    """API view to return flashcard set details in JSON format."""
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)

    flashcard_data = []
    for flashcard in flashcards:
        flashcard_info = {
            'question': flashcard.question,
            'answer': flashcard.answer,
            'next_review_date': flashcard.next_review_date.strftime('%Y-%m-%d') if flashcard.next_review_date else None
        }
        flashcard_data.append(flashcard_info)

    data = {
        'title': flashcard_set.title,
        'flashcards': flashcard_data
    }

    return JsonResponse(data)

@login_required # Edit a set
def edit_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id, user=request.user)  # Ensure the set belongs to the user

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_name = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()

        if title and category_name:
            # Check if another set by the same user already has this title
            duplicate = FlashcardSet.objects.filter(user=request.user, title=title).exclude(set_id=set_id).exists()
            if duplicate:
                messages.error(request, "A flashcard set with this title already exists.")
                return redirect('view_flashcard_set', set_id=set_id)

            category, _ = Category.objects.get_or_create(name=category_name)
            flashcard_set.title = title
            flashcard_set.category = category
            flashcard_set.description = description
            flashcard_set.save()

            messages.success(request, "Flashcard set updated successfully!")
        else:
            messages.error(request, "Please fill in all required fields.")

        return redirect('view_flashcard_set', set_id=set_id)

    return render(request, 'set_details.html', {'flashcard_set': flashcard_set})

@login_required  # Delete a set
def delete_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)

    if request.method == "POST":
        try:
            flashcard_set.delete()
            messages.success(request, "Flashcard set deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect('library_view')

@login_required
def toggle_favorite(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)

    # Check if the set is already favorited
    favorite, created = FavoriteSet.objects.get_or_create(user=request.user, set=flashcard_set)

    if not created:
        # If the favorite exists, remove it
        favorite.delete()
        favorited = False
    else:
        # Prevent exceeding the limit
        favorite_count = FavoriteSet.objects.filter(user=request.user).count()
        if favorite_count >= 100:
            return JsonResponse({
                "error": "You have reached the maximum limit of 100 favorite sets."
            }, status=400)
        favorited = True

    favorite_count = FavoriteSet.objects.filter(user=request.user).count()

    # Get the last viewed set from the session
    last_viewed_set_id = request.session.get("last_viewed_set_id", None)
    last_viewed_set = None
    if last_viewed_set_id:
        last_viewed_set = FlashcardSet.objects.filter(user=request.user, set_id=last_viewed_set_id).first()

    return JsonResponse({
        "favorited": favorited,
        "favorite_count": favorite_count,
        "last_viewed_set": last_viewed_set.title if last_viewed_set else None
    })

@login_required
def favorite_sets(request):
    favorites = FavoriteSet.objects.filter(user=request.user).select_related('set')
    # print(f"Favorite sets: {favorite_sets}")
    return render(request, 'home.html', {'favorites': favorites})

# ======================== Flashcard Management ======================== #

@login_required
def create_flashcard(request, set_id):
    form = FlashcardForm(request.POST or None)

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    # Get the specific flashcard set
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)

    if request.method == 'POST':
        card_count = Flashcard.objects.filter(flashcard_set=flashcard_set).count()  # Get the number of cards in the selected set

        # print(f'Set ID= {flashcard_set.set_id} Card Count: {card_count}')  # Debugging statement to check the card count

        if card_count >= 500:  # Max number of cards a user can have in one set
            messages.error(request, "Maximum number of flashcards reached for this set. Please delete an existing flashcard before creating a new one.")
        elif form.is_valid():
            question = form.cleaned_data['question'].strip()
            answer = form.cleaned_data['answer'].strip()

            # Ensure the flashcard set belongs to the logged-in user
            if flashcard_set.user == request.user:
                # Check if a flashcard with the same question and answer already exists
                if Flashcard.objects.filter(flashcard_set=flashcard_set, question__iexact=question, answer__iexact=answer).exists():
                    messages.error(request, "A flashcard with the same question and answer already exists in this set.")
                else:
                    # Save the new flashcard and associate it with the current flashcard set
                    form.save(commit=False).flashcard_set = flashcard_set 
                    form.save()
                    messages.success(request, "Flashcard created successfully!")
                    return redirect('create_flashcard', set_id=set_id)
            else:
                messages.error(request, "You do not have permission to add flashcards to this set.")
        else:
            messages.error(request, "Failed to create flashcard. Please check your input.")

    return render(request, 'create_flashcard.html', {
        'form': form,
        'recent_sets': recent_sets,  # Pass recent sets to the template
        'flashcard_set': flashcard_set,
    })

def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)

    # Restrict access to private sets for non-owners or guest users
    if not flashcard_set.is_shared:
        if not request.user.is_authenticated:
            messages.error(request, "This flashcard set is private.")
            return redirect('home')

        is_owner = flashcard_set.user == request.user
        is_assigned = flashcard_set.classrooms.filter(students=request.user).exists()

        if not is_owner and not is_assigned:
            messages.error(request, "This flashcard set is private.")
            return redirect('home')

    # Track recently viewed sets (only for authenticated users)
    if request.user.is_authenticated:
        recent = request.session.get('recent_sets', [])
        if set_id in recent:
            recent.remove(set_id)
        recent.insert(0, set_id)
        request.session['recent_sets'] = recent[:3]

    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    card_count = flashcards.count()

    # Handle visibility update (only owner can change)
    if request.method == 'POST':
        if request.user.is_authenticated and flashcard_set.user == request.user:
            is_shared = request.POST.get('is_shared') == 'on'
            flashcard_set.is_shared = is_shared
            flashcard_set.save()
            # print("Visibility updated:", is_shared)
            messages.success(request, "Visibility updated successfully.")
            return redirect('view_flashcard_set', set_id=set_id)
        else:
            messages.error(request, "You do not have permission to update this set.")

    # Calculate time until next review
    for flashcard in flashcards:
        if flashcard.next_review_date:
            next_review = flashcard.next_review_date
            now_time = now()
            if is_naive(next_review):
                next_review = make_aware(next_review)

            time_remaining = next_review - now_time
            if time_remaining.total_seconds() <= 0:
                flashcard.time_until_next_review = "Overdue"
            else:
                days = time_remaining.days
                hours = time_remaining.seconds // 3600
                flashcard.time_until_next_review = f"{days}d {hours}h"

    # Pick template based on ownership
    is_owner = request.user.is_authenticated and request.user == flashcard_set.user
    template = 'flashcard_set_detail.html' if is_owner else 'flashcard_set_detail_world.html'

    return render(request, template, {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
        'card_count': card_count,
        'is_guest': not request.user.is_authenticated,
        'is_owner': is_owner
    })

@login_required  # Delete a flashcard
def delete_flashcard(request, card_id):
    flashcard = get_object_or_404(Flashcard, card_id=card_id)
    try:
        flashcard.delete()
        messages.success(request, "Flashcard deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect('view_flashcard_set', set_id=flashcard.flashcard_set.set_id)

@login_required
def edit_flashcard(request, card_id):
    flashcard = get_object_or_404(Flashcard, card_id=card_id)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()

        if question and answer:
            # Check for duplicates within the same set, excluding the current card
            duplicate = Flashcard.objects.filter(
                flashcard_set=flashcard.flashcard_set,
                question__iexact=question,
                answer__iexact=answer
            ).exclude(card_id=card_id).exists()

            if duplicate:
                messages.error(request, "A flashcard with this question and answer already exists in this set.")
            else:
                flashcard.question = question
                flashcard.answer = answer
                flashcard.save()
                messages.success(request, "Flashcard updated successfully.")
        else:
            messages.error(request, "Both question and answer fields are required.")

        return redirect('view_flashcard_set', set_id=flashcard.flashcard_set.set_id)

    return render(request, 'flashcard_set_details.html', {'flashcard': flashcard})

@login_required
def get_flashcard_set_details(request, set_id):

    # print("Existing FlashcardSet IDs:", list(FlashcardSet.objects.values_list('set_id', flat=True)))

    try:
        flashcard_set = FlashcardSet.objects.get(set_id=set_id)
    except FlashcardSet.DoesNotExist:
        return JsonResponse({'error': f'Flashcard set with ID {set_id} not found'}, status=404)

    flashcard_set = FlashcardSet.objects.get(set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    flashcards_data = [{'question': fc.question, 'answer': fc.answer} for fc in flashcards]

    data = {
        'title': flashcard_set.title,
        'flashcards': flashcards_data
    }

    return JsonResponse(data)

# ======================== Study Mode ======================== #

def study_view(request, set_id):
    if request.user.is_authenticated:
        flashcard_set = get_object_or_404(
            FlashcardSet.objects.filter(
                Q(set_id=set_id) &
                (
                    Q(is_shared=True) |
                    Q(user=request.user) |
                    Q(classrooms__students=request.user)
                )
            ).distinct()
        )
    else:
        # For guests, fetch only shared flashcard sets
        flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id, is_shared=True)

    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)

    # Initialize flashcard_sets and other variables in both cases
    flashcard_sets = []  # Initialize as an empty list by default
    favorite_sets = []
    recent_sets = []
    last_viewed_set = None
    remaining_cards = 0

    # Authenticated user logic
    if request.user.is_authenticated:
        # Retrieve the list of recent sets from the session
        recent = request.session.get('recent_sets', [])
        
        # If the set_id is already in the recent list, remove it to add it at the top
        if set_id in recent:
            recent.remove(set_id)
        
        # Add the current set to the top of the list
        recent.insert(0, set_id)
        
        # Limit the list to the top 3 recent sets
        recent = recent[:3]
        
        # Save the updated list back to the session
        request.session['recent_sets'] = recent

        # Fetch all sets that are in the recent list (not limited to user-owned sets)
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort the sets by the order they appear in the recent list
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))

        # Fetch the user's favorite sets
        favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
        
        # Track the last viewed set
        last_viewed_set = flashcard_set
        
        # Count the remaining flashcards that have not been learned yet
        remaining_cards = flashcards.filter(is_learned=False).count()

    else:
        flashcard_sets = []
        recent_sets = []
        favorite_sets = []
        last_viewed_set = None
        remaining_cards = 0

    return render(request, 'home.html', {
        "flashcard_set": flashcard_set,
        "flashcards": flashcards,
        "favorite_sets": favorite_sets,
        "flashcard_sets": flashcard_sets,
        "recent_sets": recent_sets,
        "last_viewed_set": last_viewed_set,
        "remaining_cards": remaining_cards,
        "is_guest": not request.user.is_authenticated,
    })

def learn_view(request):
    set_id = request.GET.get('set_id')

    # Handle missing or invalid set_id
    if not set_id or not set_id.isdigit():
        messages.error(request, "Invalid or missing flashcard set ID.")
        return redirect('home')  # Redirect to home with the error message
    try:
        flashcard_set = FlashcardSet.objects.get(set_id=set_id)
    except FlashcardSet.DoesNotExist:
        messages.error(request, "Flashcard set not found.")
        return redirect('home')

    # Get flashcards that are not yet learned
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set, is_learned=False)

    # If the set is empty, show a message instead of causing an error
    if not flashcards.exists():
        return render(request, 'learn.html', {
            'flashcard_set': flashcard_set,
            'error': 'This flashcard set is empty. Add cards to begin learning.'
        })

    return render(request, 'learn.html', {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
    })

@csrf_exempt  # You may need to add this to bypass CSRF for AJAX requests (if not using CSRF token)
def update_learned_flashcards(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Get the data sent with the request
        flashcard_ids = data.get('flashcard_ids', [])
        
        # Update the flashcards with the provided IDs
        flashcards = Flashcard.objects.filter(card_id__in=flashcard_ids)
        
        # Set is_learned to True for each flashcard and set next_review_date to 2 minutes from now
        flashcards.update(
            is_learned=True,
            next_review_date=timezone.now() + timedelta(minutes=2)  # Set review time to 2 minutes later
        )

        # Retrieve or create the current user's activity
        activity, created = UserActivity.objects.get_or_create(user=request.user)

        # Add the learned flashcards to the activity's learned_cards field (ManyToManyField)
        activity.learned_cards.add(*flashcards)

        # Save the user activity
        activity.save()
        
        # Return success response
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@login_required
def review_view(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id, user=request.user)

    # Fetch all flashcards for the set that are marked as learned
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set, is_learned=True)

    # If the set has no flashcards at all
    if not Flashcard.objects.filter(flashcard_set=flashcard_set).exists():
        messages.error(request, "This set has no flashcards. Add some to begin reviewing.")
        return redirect('library_view')

    # If no learned flashcards exist
    if not flashcards.exists():
        messages.info(request, "You haven't learned any cards from this set yet.")
        return redirect('study_view', set_id=set_id)

    # Filter flashcards that are due for review (next_review_date <= now)
    reviewable_cards = flashcards.filter(next_review_date__lte=timezone.now())

    # If there are no reviewable flashcards yet
    if not reviewable_cards.exists():
        messages.info(request, "There are no flashcards to review at this time.")
        return redirect('study_view', set_id=set_id)

    return render(request, "review.html", {"flashcards": reviewable_cards})

@login_required
def update_flashcard_level(request, card_id, action):
    if request.method == 'POST':
        flashcard = get_object_or_404(Flashcard, card_id=card_id, flashcard_set__user=request.user)

        # Get the new level from the request body (the action indicates whether it's a promotion or demotion)
        data = json.loads(request.body)
        new_level = data.get('level')

        # Define the review times for each level (in minutes)
        review_times = {
            1: timedelta(minutes=5),    # Level 1: 5 minutes
            2: timedelta(minutes=10),   # Level 2: 10 minutes
            3: timedelta(minutes=30),   # Level 3: 30 minutes
            4: timedelta(hours=1),      # Level 4: 1 hour
            5: timedelta(days=1)        # Level 5: 1 day
        }

        # Calculate the next review date based on the new level
        if new_level in review_times:
            next_review_date = timezone.now() + review_times[new_level]
            flashcard.level = new_level
            flashcard.next_review_date = next_review_date
            flashcard.save()

            return JsonResponse({"status": "success", "new_level": new_level, "next_review_date": next_review_date})

        else:
            return JsonResponse({"status": "error", "message": "Invalid level"}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def mark_flashcard_as_learned(request, card_id):
    if request.method == 'POST':
        flashcard = get_object_or_404(Flashcard, card_id=card_id, flashcard_set__user=request.user)
        
        # Mark the flashcard as learned
        flashcard.is_learned = True
        flashcard.level = 0  # Set level to 0 when learned
        flashcard.next_review_date = timezone.now() + timedelta(minutes=1)  # Set review time to 1 minute later
        flashcard.save()
        
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@csrf_exempt
def update_flashcard_review(request, card_id):
    if request.method == "POST":
        flashcard = Flashcard.objects.filter(card_id=card_id).first()
        if flashcard:
            # Increment the level or change review time depending on if the card was correct or not
            flashcard.next_review_date = timezone.now() + timedelta(minutes=5)  # Example: Add 5 mins for the next review
            flashcard.save()

            return JsonResponse({"status": "success", "next_review_date": flashcard.next_review_date})
        return JsonResponse({"status": "error", "message": "Flashcard not found."}, status=404)

# ======================== Activity Logs ======================== #
    
@login_required
@csrf_exempt
def track_time_spent(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body of the request
            data = json.loads(request.body)

            # Extract flashcard ID and time spent
            card_id = data.get('flashcard_id')
            time_spent = int(data.get('time_spent', 0))

            # Find the flashcard or return 404
            flashcard = get_object_or_404(Flashcard, card_id=card_id)

            # Get or create user activity record
            activity, created = UserActivity.objects.get_or_create(user=request.user)

            # Get viewed flashcards list from session
            viewed_flashcards = request.session.get('viewed_flashcards', [])

            # If this card hasn't been counted yet, increment cards_viewed
            if card_id not in viewed_flashcards:
                activity.cards_viewed += 1
                viewed_flashcards.append(card_id)

            # Always update time spent and recent flashcard
            activity.time_spent += time_spent
            activity.recent_flashcard = flashcard
            activity.save()

            # Save updated viewed flashcards list back to session
            request.session['viewed_flashcards'] = viewed_flashcards

            return JsonResponse({"status": "success"})

        except Exception as e:
            # print("Error in track_time_spent:", e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

@login_required
def activity_dashboard(request):
    activity, created = UserActivity.objects.get_or_create(user=request.user)
    
    # Ensure that time_spent is an integer representing the total time spent in seconds
    time_spent_seconds = activity.time_spent

    # Calculate hours, minutes, and seconds
    hours = time_spent_seconds // 3600
    minutes = (time_spent_seconds % 3600) // 60
    seconds = time_spent_seconds % 60

    # Format the time to always show two digits for hours, minutes, and seconds
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    return render(request, 'activity_dashboard.html', {
        'activity': activity,
        'time_spent': formatted_time,
        'learned_count': activity.learned_cards.count(),
        'recent_flashcard': activity.recent_flashcard,
    })

@csrf_exempt
@login_required
def update_user_activity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            activity_type = data.get('activity_type')
            total_questions = data.get('total_questions', 0)
            time_spent = data.get('time_spent', 0)

            logger.debug(f"Received activity_type: {activity_type}, total_questions: {total_questions}, time_spent: {time_spent}")

            # Handling the activity type 'quiz_completed'
            if activity_type == 'quiz_completed':
                # Log the activity (e.g., increment quiz completed count)
                user_activity, created = UserActivity.objects.get_or_create(user=request.user)

                # Increment the quiz completed count
                user_activity.quizzes_completed += 1
                user_activity.save()

                # Save the time spent
                user_activity.time_spent += time_spent
                user_activity.save()

                logger.debug(f"Updated quizzes_completed: {user_activity.quizzes_completed}, time_spent: {user_activity.time_spent}")

                return JsonResponse({'success': True, 'message': 'Activity updated successfully.'})

            logger.error("Unknown activity type.")
            return JsonResponse({'success': False, 'message': 'Unknown activity type.'})

        except Exception as e:
            logger.error(f"Error in update_user_activity: {e}")
            return JsonResponse({'success': False, 'message': 'An error occurred.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt
def track_flashcard_time(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse incoming JSON data
        flashcard_id = data.get('flashcard_id')
        time_spent = data.get('time_spent')

        # Get or create the user's activity record
        activity, created = UserActivity.objects.get_or_create(user=request.user)

        # Track the time spent on the specific flashcard
        flashcard = Flashcard.objects.get(id=flashcard_id)
        activity.time_spent += time_spent
        activity.cards_viewed += 1  # Increment the number of cards viewed
        activity.save()  # Save the updated activity

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def reset_user_activity(request):
    if request.method == 'POST':
        try:
            # Get or create the user's activity record
            activity, created = UserActivity.objects.get_or_create(user=request.user)

            # Reset the stats
            activity.quizzes_completed = 0
            activity.time_spent = 0
            activity.cards_viewed = 0
            activity.learned_cards.clear()  # Clear the learned cards (ManyToManyField)

            # Save the reset stats
            activity.save()

            # Provide a success message
            messages.success(request, "Your activity stats have been reset.")

        except Exception as e:
            messages.error(request, f"An error occurred while resetting the stats: {str(e)}")

        # Redirect back to the activity dashboard after reset
        return redirect('activity_dashboard') 

    return redirect('activity_dashboard')  # If not a POST request, redirect to dashboard

# ======================== Classrooms ======================== #

@login_required
def classrooms_view(request):
    user_profile = request.user.userprofile

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    if user_profile.role == 'teacher':
        classrooms = Classroom.objects.filter(user=request.user)
        class_count = classrooms.count()
        return render(request, 'teacher_classrooms.html', {
            'classrooms': classrooms,
            'class_count': class_count,
            "recent_sets": recent_sets,
        })
    else:
        classrooms = Classroom.objects.filter(students=request.user)
        student_class_count = classrooms.count()
        return render(request, 'student_classrooms.html', {
            'classrooms': classrooms,
            'student_class_count': student_class_count,
            "recent_sets": recent_sets,
        })

# Teacher-specific classrooms view
@login_required
def teacher_classrooms(request):
    # Only teachers will access this view
    classrooms = Classroom.objects.filter(user=request.user)

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    return render(request, 'teacher_classrooms.html', {'classrooms': classrooms}, {
        "recent_sets": recent_sets,
    })

# Student-specific classrooms view
@login_required
def student_classrooms(request):
    # Only students will access this view

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    classrooms = Classroom.objects.filter(students=request.user)
    student_class_count = classrooms.count()
    return render(request, 'student_classrooms.html', {
        'classrooms': classrooms,
        'student_class_count': student_class_count
    })

@login_required
def create_classroom(request):
    # Count the number of classrooms the user already has
    current_count = Classroom.objects.filter(user=request.user).count()
    if current_count >= 50:
        messages.error(request, "You have reached the maximum of 50 classrooms. Please delete one to create a new one.")
        return redirect('classrooms')
    
    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, "Classroom name is required.")
            return render(request, 'create_classroom.html')

        # Check for duplicate classroom name for the same teacher
        if Classroom.objects.filter(user=request.user, name__iexact=name).exists():
            messages.error(request, "You already have a classroom with that name.")
            return render(request, 'create_classroom.html')

        # Create the classroom and assign the teacher field
        Classroom.objects.create(
            name=name,
            description=description,
            user=request.user,
            teacher=request.user  # Auto-assign the creator as the teacher
        )

        messages.success(request, "Classroom created successfully.")
        return redirect('classrooms')

    return render(request, 'create_classroom.html', {
        "recent_sets": recent_sets,
    })

@login_required
def view_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    # Determine the user's role based on their UserProfile
    if user_profile.role == 'teacher' and classroom.user == request.user:
        role = 'teacher'
    elif user_profile.role == 'student' and request.user in classroom.students.all():
        role = 'student'
    else:
        return HttpResponseForbidden("Access denied: You do not have permission to view this classroom.")
    
    students = None
    quizzes = Quiz.objects.filter(classroom=classroom).select_related('flashcard_set')

    # If student, fetch their quiz results and attach to quizzes
    quiz_results = {}
    if role == 'student':
        student_results = QuizResult.objects.filter(student=request.user, quiz__in=quizzes)
        quiz_results = {result.quiz.quiz_id: result for result in student_results}

        # Attach result to each quiz
        for quiz in quizzes:
            quiz.result = quiz_results.get(quiz.quiz_id)

    elif role == 'teacher':
        students = classroom.students.all()

    context = {
        'classroom': classroom,
        'role': role,
        'students': students,
        'quizzes': quizzes,
        "recent_sets": recent_sets,
    }
    return render(request, 'view_classroom.html', context)

# Delete a classroom
@login_required
def delete_classroom(request, classroom_id):
    try:
        classroom = get_object_or_404(Classroom, id=classroom_id, user=request.user)
        classroom.delete()
        messages.success(request, "Classroom deleted successfully.")
    except Exception as e:
        messages.error(request, "Failed to delete classroom. Please try again.")
        # print(f"Error deleting classroom: {e}")
    return redirect('classrooms')

def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    classroom_id = quiz.classroom.id
    quiz.delete()
    messages.success(request, "Quiz deleted successfully.")
    return redirect('view_classroom', classroom_id=classroom_id)

# Join a classroom as a student
@login_required
def join_classroom(request):
    if request.method == "POST":
        student = request.user
        current_classroom_count = Classroom.objects.filter(students=student).count()

        if current_classroom_count >= 50:
            messages.error(request, "You have reached the maximum of 50 classrooms. Leave one to join another.")
            return redirect('student_classrooms')

        classroom_code = request.POST['classroom_code']
        try:
            classroom = Classroom.objects.get(code=classroom_code)

            # Optional: prevent rejoining same class
            if classroom.students.filter(id=student.id).exists():
                messages.info(request, "You are already enrolled in this classroom.")
            else:
                classroom.students.add(student)
                messages.success(request, "You have successfully joined the classroom!")

        except Classroom.DoesNotExist:
            messages.error(request, "Invalid classroom code. Please try again.")

        return redirect('student_classrooms')

    return redirect('student_classrooms')

@login_required
def assign_flashcard_sets(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    # Check if the logged-in user is a teacher and authorized for this classroom
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # print(f"User Profile Role: {user_profile.role}")  # Debugging
        # print(f"Classroom Teacher: {classroom.teacher}")  # Debugging
        # print(f"Classroom Creator: {classroom.user}")     # Debugging

        is_teacher = user_profile.role == 'teacher'
        is_classroom_owner = classroom.user == request.user
        is_assigned_teacher = classroom.teacher == request.user if classroom.teacher else False

        if not is_teacher or not (is_classroom_owner or is_assigned_teacher):
            messages.error(request, "You are not authorized to assign flashcard sets to this classroom.")
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('home')

    # Get the IDs of already assigned flashcard sets
    assigned_ids = classroom.flashcard_sets.values_list('set_id', flat=True)

    # Only show flashcard sets created by the teacher and not already assigned
    flashcard_sets = FlashcardSet.objects.filter(user=request.user).exclude(set_id__in=assigned_ids)

    if request.method == 'POST':
        if 'remove_set' in request.POST:
            remove_id = request.POST.get('remove_set')
            flashcard_set = get_object_or_404(FlashcardSet, set_id=remove_id)
            classroom.flashcard_sets.remove(flashcard_set)
            messages.success(request, f"Removed '{flashcard_set.title}' from the classroom.")
            return redirect('assign_flashcard_sets', classroom_id=classroom.id)

        selected_set_ids = request.POST.getlist('sets')
        if not selected_set_ids:
            messages.error(request, "Please select at least one flashcard set to assign.")
        else:
            for set_id in selected_set_ids:
                flashcard_set = FlashcardSet.objects.get(set_id=set_id)
                classroom.flashcard_sets.add(flashcard_set)
            messages.success(request, "Selected flashcard sets have been assigned successfully.")
        return redirect('assign_flashcard_sets', classroom_id=classroom.id)

    assigned_flashcard_sets = classroom.flashcard_sets.all()

    return render(request, 'assign_flashcard_sets.html', {
        'classroom': classroom,
        'flashcard_sets': flashcard_sets,
        'assigned_flashcard_sets': assigned_flashcard_sets,
        "recent_sets": recent_sets,
    })

@login_required
def assign_quiz(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, user=request.user)
    flashcard_sets = classroom.flashcard_sets.all()

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    if request.method == "POST":
        title = request.POST.get("title")
        set_id = request.POST.get("set_id")
        due_date = request.POST.get("due_date")

        if not title or not set_id:
            messages.error(request, "Quiz title and flashcard set are required.")
        elif Quiz.objects.filter(classroom=classroom, title=title).exists():
            messages.error(request, "A quiz with this title already exists in this classroom.")
        else:
            flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
            Quiz.objects.create(
                title=title,
                flashcard_set=flashcard_set,
                classroom=classroom,
                due_date=due_date or None
            )
            messages.success(request, "Quiz successfully assigned.")
            return redirect("view_classroom", classroom_id=classroom.id)

    return render(request, "assign_quiz.html", {
        "classroom": classroom,
        "flashcard_sets": flashcard_sets,
        "recent_sets": recent_sets,
    })

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    classroom = quiz.classroom

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets

    if request.user not in classroom.students.all():
        return HttpResponseForbidden("You are not assigned to this quiz.")

    # Check if the user has already taken the quiz
    existing_result = QuizResult.objects.filter(student=request.user, quiz=quiz).first()
    if existing_result:
        return render(request, 'quiz_result.html', {
            'score': existing_result.score,
            'total': existing_result.total,
            'classroom': classroom,
            'already_taken': True
        })

    flashcard_set = quiz.flashcard_set
    flashcards = flashcard_set.flashcard_set.all()

    if request.method == 'POST':
        score = 0
        for flashcard in flashcards:
            user_answer = request.POST.get(f'flashcard_{flashcard.card_id}')
            if user_answer and user_answer.lower() == flashcard.answer.lower():
                score += 1

        # Save the quiz result
        QuizResult.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total=len(flashcards)
        )

        user_activity, created = UserActivity.objects.get_or_create(user=request.user)
        user_activity.quizzes_completed += 1
        user_activity.save()

        return render(request, 'quiz_result.html', {
            'score': score,
            'total': len(flashcards),
            'classroom': classroom,
            "recent_sets": recent_sets,
        })
    
    # Handle GET request (show quiz form)
    return render(request, 'start_quiz.html', {
        'quiz': quiz,
        'flashcards': flashcards,
        'classroom': classroom,
        "recent_sets": recent_sets,
    })

@login_required
def student_scores(request, classroom_id, student_id):
    # Fetch the student using the provided student_id
    student = get_object_or_404(User, id=student_id)

    classroom = get_object_or_404(Classroom, id=classroom_id, user=request.user)
    
    # Get all quizzes assigned to the classroom the student is enrolled in
    enrolled_classrooms = Classroom.objects.filter(students=student)
    
    # Fetch quizzes that have been assigned to any of the classrooms the student is in
    quizzes = Quiz.objects.filter(classroom__in=enrolled_classrooms)
    
    # Get quiz results for the student, if any
    quiz_results = QuizResult.objects.filter(student=student, quiz__in=quizzes)
    
    # Create a dictionary of quiz results for easy access in the template
    quiz_results_dict = {result.quiz.quiz_id: result for result in quiz_results}
    
    # Add quiz results to each quiz object
    for quiz in quizzes:
        quiz.result = quiz_results_dict.get(quiz.quiz_id)

    # Get recent sets from session only for authenticated users
    if request.user.is_authenticated:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids))
        
        # Sort them in the order stored in session
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))
    else:
        recent_sets = []  # Empty list for guest users as they cannot access recent sets
    
    context = {
        'student': student,
        'quizzes': quizzes,
        'classroom': classroom,
        "recent_sets": recent_sets,
    }
    
    return render(request, 'student_scores.html', context)

def toggle_grade_status(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id)

    if request.method == 'POST':
        result.graded = not result.graded
        result.save()
        status = "marked as graded" if result.graded else "grade removed"
        messages.success(request, f"Quiz result has been {status}.")
    else:
        messages.error(request, "Invalid request method.")

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def unenroll_student(request, classroom_id, student_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, user=request.user)
    student = get_object_or_404(User, id=student_id)

    if request.method == 'POST':
        classroom.students.remove(student)
        messages.success(request, f"{student.username} has been unenrolled.")
        return redirect('view_classroom', classroom_id=classroom.id)

    messages.error(request, "Invalid request method.")
    return redirect('student_scores', student_id=student.id, classroom_id=classroom.id)

# ======================== Search & World Sets ======================== #

def search_results(request):
    query = request.GET.get('query', '')
    
    if query:
        flashcard_sets = FlashcardSet.objects.filter(title__icontains=query)
    else:
        flashcard_sets = FlashcardSet.objects.none()
    
    return render(request, 'search_results.html', {
        'flashcard_sets': flashcard_sets,
        'query': query
    })

def world_sets(request):
    is_guest = not request.user.is_authenticated

    favorite_set_ids = []
    favorite_flashcard_sets = []

    # Handle favorites for logged-in users
    if not is_guest:
        favorite_sets = FavoriteSet.objects.filter(user=request.user)
        favorite_set_ids = list(favorite_sets.values_list('set_id', flat=True))
        favorite_flashcard_sets = FlashcardSet.objects.filter(
            set_id__in=favorite_set_ids,
            is_shared=True
        ).select_related('user', 'category')

    recent_sets = []
    if not is_guest:
        recent_ids = request.session.get("recent_sets", [])
        recent_sets = list(FlashcardSet.objects.filter(set_id__in=recent_ids, user=request.user))
        recent_sets.sort(key=lambda x: recent_ids.index(x.set_id))

    # Get all shared/public sets
    all_shared_sets = FlashcardSet.objects.filter(is_shared=True).select_related('user', 'category')

    # Create a merged list of all shared sets + the favorites
    seen_ids = set()
    flashcard_sets = []

    # Add all shared sets, ensuring no duplicates with favorites
    for fs in all_shared_sets:
        if fs.set_id not in seen_ids:
            flashcard_sets.append(fs)
            seen_ids.add(fs.set_id)

    # Add favorite sets that are shared but ensure no duplicates
    for fs in favorite_flashcard_sets:
        if fs.set_id not in seen_ids:
            flashcard_sets.append(fs)
            seen_ids.add(fs.set_id)

    # print("All shared set IDs:", [fs.set_id for fs in all_shared_sets])
    # print("Shared favorite IDs:", [fs.set_id for fs in favorite_flashcard_sets])
    # print("Displayed All Sets:", [fs.set_id for fs in flashcard_sets])

    return render(request, 'world_sets.html', {
        'flashcard_sets': flashcard_sets,
        'favorite_flashcard_sets': favorite_flashcard_sets,
        'favorite_set_ids': favorite_set_ids,
        'recent_sets': recent_sets,
        'is_guest': is_guest,
    })

# ======================== Export to Excel ======================== #

def export_card_set(request):
    """
    Handle request to export a card set to Excel.
    """
    if request.method == "POST":
        card_set = request.POST.get('card_set')

        # Validate card set
        if not card_set:
            return JsonResponse({"error": "No card set data provided"}, status=400)
        
        try:
            # Convert card_set from JSON string to Python object
            card_set = json.loads(card_set)

            # Export the card set to an Excel file
            file_name = export_card_set_to_excel(card_set)

            # Read file contents before deletion
            with open(file_name, 'rb') as excel_file:
                file_data = excel_file.read()

            # Remove the temporary file
            os.remove(file_name)

            # Send the response with the file data
            response = HttpResponse(
                file_data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
            return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

def export_card_set_to_excel(card_set):
    df = pd.DataFrame(card_set)
    if 'Question' not in df.columns or 'Answer' not in df.columns:
        raise ValueError("Each card must have 'Question' and 'Answer' keys.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False, engine="openpyxl")
            return tmp.name
    except Exception as e:
        raise Exception(f"Failed to export card set to Excel: {e}")
