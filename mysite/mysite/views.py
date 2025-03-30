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
import json

# ======================== Main Pages ======================== #

from django.shortcuts import render
from .models import Flashcard, FlashcardSet

from django.utils import timezone

@login_required
def home(request):
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')

    # Retrieve the last viewed set from session
    last_viewed_set_id = request.session.get('last_viewed_set_id', None)
    last_viewed_set = None
    flashcards = Flashcard.objects.none()  # Start with an empty queryset, not a list

    if last_viewed_set_id:
        last_viewed_set = FlashcardSet.objects.filter(user=request.user, set_id=last_viewed_set_id).first()
        if last_viewed_set:
            flashcards = last_viewed_set.flashcard_set.all()  # This is a queryset

    # Count the flashcards that are ready for review (next_review_date is <= now)
    reviewable_cards = flashcards.filter(next_review_date__lte=timezone.now())  # Adjusted to filter properly

    # Count the number of flashcards with is_learned=False
    remaining_cards = flashcards.filter(is_learned=False).count()

    return render(
        request,
        "home.html",
        {
            "flashcard_sets": flashcard_sets,
            "favorite_sets": favorite_sets,
            "last_viewed_set": last_viewed_set,
            "flashcards": flashcards,
            "remaining_cards": remaining_cards,
            "reviewable_cards_count": reviewable_cards.count(),  # Update count
        }
    )


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
        title = request.POST.get('title')
        category_name = request.POST.get('category')
        description = request.POST.get('description')

        # Validate if title and category are provided
        if title and category_name:
            # Create or get the Category object
            category, created = Category.objects.get_or_create(name=category_name)

            # Create a new FlashcardSet
            FlashcardSet.objects.create(
                title=title, 
                category=category, 
                description=description, 
                user=request.user
            )

            # Redirect to library view after creating the set
            return redirect('library_view')
        
        # Add error message if title or category is missing
        messages.error(request, "Please fill in all required fields.")
    
    return render(request, 'create_set.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })


@login_required  # View flashcard set details
def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)

    # Calculate time until next review for each flashcard
    for flashcard in flashcards:
        if flashcard.next_review_date:
            time_remaining = flashcard.next_review_date - date.today()  # Time difference
            flashcard.time_until_next_review = time_remaining

    return render(
        request,
        'flashcard_set_detail.html',
        {'flashcard_set': flashcard_set, 'flashcards': flashcards}
    )

@login_required  # Delete a set
def delete_set(request, set_id):
    get_object_or_404(FlashcardSet, set_id=set_id).delete()
    return redirect('library_view')

@login_required
def toggle_favorite(request, set_id):
    set = get_object_or_404(FlashcardSet, set_id=set_id)
    favorite, created = FavoriteSet.objects.get_or_create(user=request.user, set=set)
    
    # If the favorite already exists, remove it
    if not created:
        favorite.delete()
        favorited = False
    else:
        favorited = True

    # Get the last viewed set from the session to return to the frontend
    last_viewed_set_id = request.session.get('last_viewed_set_id', None)
    last_viewed_set = None
    if last_viewed_set_id:
        last_viewed_set = FlashcardSet.objects.filter(user=request.user, set_id=last_viewed_set_id).first()

    return JsonResponse({
        "favorited": favorited,
        "last_viewed_set": last_viewed_set.title if last_viewed_set else None  # Send the last viewed set title to update the dropdown
    })


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

    # Count the number of unlearned flashcards in the set
    remaining_cards = flashcards.filter(is_learned=False).count()

    # Set the last viewed set in the session when entering the study page
    request.session['last_viewed_set_id'] = set_id

    # Retrieve the last viewed set from session
    last_viewed_set_id = request.session.get('last_viewed_set_id', None)
    last_viewed_set = FlashcardSet.objects.filter(user=request.user, set_id=last_viewed_set_id).first() if last_viewed_set_id else None

    # Render the study page (home.html in this case) with the correct context
    return render(request, 'home.html', {
        "flashcard_set": flashcard_set,
        "flashcards": flashcards,
        "favorite_sets": favorite_sets,
        "flashcard_sets": flashcard_sets,
        "last_viewed_set": last_viewed_set,  # Pass last viewed set to the template
        "remaining_cards": remaining_cards,  # Add unlearned flashcards count
    })


def learn_view(request):
    set_id = request.GET.get('set_id')

    try:
        flashcard_set = FlashcardSet.objects.get(set_id=set_id)
    except FlashcardSet.DoesNotExist:
        return render(request, 'learn.html', {
            'error': 'Flashcard set not found'
        })

    # Filter flashcards by flashcard_set and is_learned = False
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set, is_learned=False)

    return render(request, 'learn.html', {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
    })

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json

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
        
        # Return success response
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


import random
from datetime import date
from django.utils import timezone
from django.utils import timezone

@login_required
def review_view(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id, user=request.user)

    # Debugging: Print the flashcard_set details
    print(f"Flashcard Set: {flashcard_set.title}, ID: {flashcard_set.set_id}")

    # Fetch all flashcards for the set that are learned
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set, is_learned=True)

    # Debugging: Log each learned flashcard and its next_review_date
    for flashcard in flashcards:
        print(f"Flashcard ID: {flashcard.card_id}, Next Review Date: {flashcard.next_review_date}")

    # Filter flashcards that are due for review (next_review_date <= now)
    reviewable_cards = flashcards.filter(next_review_date__lte=timezone.now())

    # Debugging: Log the filtered reviewable flashcards
    print(f"Reviewable cards: {reviewable_cards}")  # This will show the cards that are ready for review

    return render(request, "review.html", {"flashcards": reviewable_cards})




from datetime import timedelta
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

