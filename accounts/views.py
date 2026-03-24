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
from .models import PasswordResetCode
from django.core.mail import send_mail

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1:
            messages.error(request, 'Please fill all required fields.')
            return redirect('accounts:register')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('accounts:register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, 'Account created! Welcome.')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('listings:home')


def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Please provide an email.')
            return redirect('accounts:forgot_password_request')
            
        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.generate_code(user)
            send_mail(
                'Password Reset for Cradle',
                f'Your verification code is: {reset_code.code}',
                'support@cradle.com',
                [email],
                fail_silently=False,
            )
            # Render the verification form
            return render(request, 'accounts/forgot_password_verify.html', {'email': email})
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email.')
            return render(request, 'accounts/forgot_password.html')
            
    return render(request, 'accounts/forgot_password.html')


def forgot_password_verify(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        try:
            user = User.objects.get(email=email)
            reset_obj = PasswordResetCode.objects.filter(user=user, code=code).first()
            
            if reset_obj and reset_obj.is_valid():
                user.set_password(new_password)
                user.save()
                reset_obj.delete()
                
                login(request, user)
                messages.success(request, 'Password reset successful.')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid or expired code.')
                return render(request, 'accounts/forgot_password_verify.html', {'email': email})
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('accounts:forgot_password_request')
            
    return redirect('accounts:forgot_password_request')


@login_required(login_url='/accounts/login/')
def dashboard(request):
    listings = Listing.objects.filter(agent=request.user)
    profile, _ = AgentProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/dashboard.html', {'listings': listings, 'agent_profile': profile})


@login_required(login_url='/accounts/login/')
def add_listing(request):
    profile, created = AgentProfile.objects.get_or_create(user=request.user)

    if not profile.is_subscribed or profile.subscription_expires < timezone.now():
        messages.error(request, 'You need an active subscription to add listings.')
        return redirect('accounts:subscribe')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        property_type = request.POST.get('property_type')
        price = request.POST.get('price')
        location = request.POST.get('location')
        whatsapp_number = request.POST.get('whatsapp_number')
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
        return redirect('accounts:dashboard')

    return render(request, 'accounts/add_listing.html')


@login_required(login_url='/accounts/login/')
def subscribe(request):
    return render(request, 'accounts/subscribe.html')


@login_required(login_url='/accounts/login/')
def initiate_payment(request):
    profile, created = AgentProfile.objects.get_or_create(user=request.user)

    if profile.is_subscribed and profile.subscription_expires > timezone.now():
        messages.success(request, 'You already have an active subscription.')
        return redirect('accounts:dashboard')

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
        return redirect('accounts:subscribe')


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
        return redirect('accounts:add_listing')
    else:
        messages.error(request, 'Payment failed or was cancelled.')
        return redirect('accounts:subscribe')
