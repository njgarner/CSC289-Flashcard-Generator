from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import Users



def login_user(request):
    return render(request, 'login.html', {}) # login page



def user_login(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Users.userAuth_objects.get(username-username,password-password)
            if user is not None:
                return redirect(request, 'Home.html', {})
            else:
                messages.success(request, ("Failure to login. Please try again. User entered username: {} and password: {}".format(username,password)))

                return redirect('login.html')
        except Exception as identifier:

            return redirect('login.html')
    
    else:
        return render(request, 'login.html') # login page