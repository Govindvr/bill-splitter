from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'billsplit/home.html')

@login_required(redirect_field_name='login', login_url='login')
def dashboard(request):
    return render(request, 'billsplit/dashboard.html')