from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
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
import json

# ======================= Python files ======================= #

from .models import FlashcardSet, Category, Flashcard, FavoriteSet
from .forms import FlashcardForm, ChangePasswordForm

# ======================== Main Pages ======================== #

@login_required  # Home page
def home(request):
    # Get favorite sets for the current user
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related("set")

    # Get Flashcard sets for the current user
    flashcard_sets = FlashcardSet.objects.filter(user=request.user)

    # Retrieve the last viewed set from session
    last_viewed_set_id = request.session.get('last_viewed_set_id', None)
    last_viewed_set = None
    flashcards = []
 
    if last_viewed_set_id:
         # Get the last viewed set for the current user
         last_viewed_set = FlashcardSet.objects.filter(user=request.user, set_id=last_viewed_set_id).first()
         if last_viewed_set:
             # Get the flashcards for the last viewed set
             flashcards = last_viewed_set.flashcard_set.all()
 
             # Calculate the number of unlearned cards
 
    # Render the home page with all necessary context
    return render(
         request,
         "home.html",
        {
             "flashcard_sets": flashcard_sets,
             "favorite_sets": favorite_sets,
             "last_viewed_set": last_viewed_set,
             "flashcards": flashcards  # Pass the flashcards of the last viewed set
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
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
    return render(request, 'about_us.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # Terms and conditions page
def terms(request):
    return render(request, 'terms.html')

@login_required
def settings(request):
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
    return render(request, 'settings.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # Schedule study time page
def schedule(request):
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
    return render(request, 'study_schedule.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # Customization page
def customize(request):
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
    return render(request, 'customize.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

@login_required  # User acount deletion page
def account_delete(request):
    favorite_sets = FavoriteSet.objects.filter(user=request.user).select_related('set')
    return render(request, 'account_delete.html', {
        'favorite_sets': favorite_sets  # Pass favorite sets to the template
    })

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
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')

def custom_logout(request):  # Logs out the user
    logout(request)
    return redirect('login_user')

def signup_user(request):  # Signup page with email verification
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

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

        # Create user but keep inactive until email is verified
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_active=False
        )

        # Send verification email
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

        if title and category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            FlashcardSet.objects.create(
                title=title, category=category, description=description, user=request.user
            )
            messages.success(request, "Flashcard set created successfully!")
            return redirect('library_view')  # Redirect to Library Page with success message
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'create_set.html', {
        'favorite_sets': favorite_sets
    })

@login_required  # View flashcard set details
def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})

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

    if request.method == 'POST':
        if form.is_valid():
            flashcard_set = form.cleaned_data['flashcard_set']
            
            # Ensure the flashcard set belongs to the logged-in user
            if flashcard_set.user == request.user:
                form.save()
                messages.success(request, "Flashcard created successfully!")
                return redirect('create_flashcard')
            else:
                messages.error(request, "You do not have permission to add flashcards to this set.")
        else:
            messages.error(request, "Failed to create flashcard. Please check your input.")

    form.fields['flashcard_set'].queryset = FlashcardSet.objects.filter(user=request.user)

    return render(request, 'create_flashcard.html', {
        'form': form,
        'favorite_sets': favorite_sets # Pass favorite sets to the template
    })

@login_required  # View flashcard deck details
def view_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, set_id=set_id)
    flashcards = Flashcard.objects.filter(flashcard_set=flashcard_set)
    return render(request, 'flashcard_set_detail.html', {'flashcard_set': flashcard_set, 'flashcards': flashcards})

@login_required  # Delete a flashcard
def delete_flashcard(request, card_id):
    flashcard = get_object_or_404(Flashcard, card_id=card_id)
    try:
        flashcard.delete()
        messages.success(request, "Flashcard deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect('view_flashcard_set', set_id=flashcard.flashcard_set.set_id)

@login_required  # Edit a flashcard
def edit_flashcard(request, card_id):
    flashcard = get_object_or_404(Flashcard, card_id=card_id)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()

        if question and answer:
            try:
                flashcard.question = question
                flashcard.answer = answer
                flashcard.save()
                messages.success(request, "Flashcard updated successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Both question and answer fields are required.")

        return redirect('view_flashcard_set', set_id=flashcard.flashcard_set.set_id)

    return render(request, 'flashcard_set_details.html', {'flashcard': flashcard})

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

@csrf_exempt  # You may need to add this to bypass CSRF for AJAX requests (if not using CSRF token)
def update_learned_flashcards(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Get the data sent with the request
        flashcard_ids = data.get('flashcard_ids', [])
        
        # Update the flashcards with the provided IDs
        flashcards = Flashcard.objects.filter(card_id__in=flashcard_ids)
        
        # Set is_learned to True for each flashcard
        flashcards.update(is_learned=True)
        
        # Return success response
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)
