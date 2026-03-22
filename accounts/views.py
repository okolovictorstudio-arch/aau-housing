from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Listing, ListingImage

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