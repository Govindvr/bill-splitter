from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def register(request):

    if request.method == 'POST':
        print("Form is validx")

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('app-home')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html',{'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {username}!')
            return redirect('app-dashboard')
        else:
            messages.warning(request, 'Username OR password is incorrect')
            return redirect('login')
    return render(request, 'user/login.html')

def logout_view(request):
    logout(request)
    messages.warning(request, 'You have been logged out!')
    return redirect('app-home')