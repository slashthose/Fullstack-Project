from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from core.models import *

# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request,"No account found with that username.")
            return render(request,"accounts/login.html")
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.error(request,"Incorrect password.Please try again.")
            return render(request,"accounts/login.html")

    return render(request,'accounts/login.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        #print(username,email)
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'accounts/register.html')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            data = Customer(user=user)
            data.save()
        except Exception as e:
            messages.error(request, "Something went wrong while creating your account. Please try again.")
            return render(request, 'accounts/register.html')

        # account creation confirmed successful at this point
        our_user = authenticate(username=username, password=password)
        if our_user is not None:
            login(request, our_user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('/')

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('user_login')

    return render(request, 'accounts/register.html')

def user_logout(request):
    if request.method == 'POST':
         logout(request)
    return redirect('/')