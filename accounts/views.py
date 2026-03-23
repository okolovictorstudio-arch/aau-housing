import requests
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from listings.models import Listing, ListingImage, AgentProfile
from django.http import HttpResponse


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, 'Account created! Welcome.')
        return redirect('dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='/accounts/login/')
def dashboard(request):
    listings = Listing.objects.filter(agent=request.user)
    return render(request, 'accounts/dashboard.html', {'listings': listings})


@login_required(login_url='/accounts/login/')
def add_listing(request):
    profile, created = AgentProfile.objects.get_or_create(user=request.user)

    if not profile.is_subscribed or profile.subscription_expires < timezone.now():
        messages.error(request, 'You need an active subscription to add listings.')
        return redirect('subscribe')

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        property_type = request.POST['property_type']
        price = request.POST['price']
        location = request.POST['location']
        whatsapp_number = request.POST['whatsapp_number']
        images = request.FILES.getlist('images')

        listing = Listing.objects.create(
            agent=request.user,
            title=title,
            description=description,
            property_type=property_type,
            price=price,
            location=location,
            whatsapp_number=whatsapp_number,
            is_approved=False,
        )

        for image in images:
            ListingImage.objects.create(listing=listing, image=image)

        messages.success(request, 'Listing submitted! It will go live once approved.')
        return redirect('dashboard')

    return render(request, 'accounts/add_listing.html')


@login_required(login_url='/accounts/login/')
def subscribe(request):
    return render(request, 'accounts/subscribe.html')


@login_required(login_url='/accounts/login/')
def initiate_payment(request):
    profile, created = AgentProfile.objects.get_or_create(user=request.user)

    if profile.is_subscribed and profile.subscription_expires > timezone.now():
        messages.success(request, 'You already have an active subscription.')
        return redirect('dashboard')

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'email': request.user.email,
        'amount': 300000,
        'callback_url': 'https://aau-housing-production.up.railway.app/accounts/payment/verify/',
        'metadata': {
            'user_id': request.user.id,
        }
    }

    response = requests.post(
        'https://api.paystack.co/transaction/initialize',
        headers=headers,
        data=json.dumps(data)
    )

    result = response.json()

    if result['status']:
        return redirect(result['data']['authorization_url'])
    else:
        messages.error(request, 'Payment initialization failed. Try again.')
        return redirect('subscribe')


@login_required(login_url='/accounts/login/')
def verify_payment(request):
    reference = request.GET.get('reference')

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    response = requests.get(
        f'https://api.paystack.co/transaction/verify/{reference}',
        headers=headers
    )

    result = response.json()

    if result['status'] and result['data']['status'] == 'success':
        profile, created = AgentProfile.objects.get_or_create(user=request.user)
        profile.is_subscribed = True
        profile.subscription_expires = timezone.now() + timedelta(days=30)
        profile.save()
        messages.success(request, 'Payment successful! You can now add listings.')
        return redirect('add_listing')
    else:
        messages.error(request, 'Payment failed or was cancelled.')
        return redirect('subscribe')

