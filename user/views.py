from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from billsplit.models import Group, GroupMember, Bill, BillParticipant
from django.db import connection
from billsplit.views import dictfetchall

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

@login_required(redirect_field_name='login', login_url='login')
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, 
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    cursor = connection.cursor()
    cursor.execute("""SELECT u.username, SUM(bp.amount) AS amount_owed
                    FROM auth_user u
                    JOIN billsplit_billparticipant bp ON u.id = bp.participant_id
                    JOIN billsplit_bill b ON b.id = bp.bill_id
                    WHERE b.bill_owner_id = %s AND bp.paid = FALSE
                    GROUP BY u.username order by amount_owed desc;""", [request.user.id])
    amount_owed = dictfetchall(cursor)

    cursor = connection.cursor()
    cursor.execute("""SELECT u.username, SUM(bp.amount) AS amount_owed_to
                    FROM auth_user u
                    JOIN billsplit_bill b ON b.bill_owner_id = u.id
                    JOIN billsplit_billparticipant bp ON b.id = bp.bill_id
                    WHERE  bp.paid = False and bp.participant_id = %s
                    GROUP BY u.id
                    ORDER BY amount_owed_to DESC""", [request.user.id])
    amount_owed_to = dictfetchall(cursor)

    

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'amount_owed': amount_owed,
        'amount_owed_to': amount_owed_to
    }

    return render(request, 'user/profile.html', context=context)