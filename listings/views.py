from pyexpat.errors import messages

from django.shortcuts import render, get_object_or_404
from .models import Listing
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    featured = Listing.objects.filter(is_approved=True, status='available')[:6]
    return render(request, 'listings/home.html', {'featured': featured})


def listing_list(request):
    listings = Listing.objects.filter(is_approved=True, status='available')
    
    property_type = request.GET.get('type')
    if property_type:
        listings = listings.filter(property_type=property_type)

    return render(request, 'listings/listing_list.html', {'listings': listings})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_approved=True)
    return render(request, 'listings/listing_detail.html', {'listing': listing})

def support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        send_mail(
            f'Cradle Support Message from {name}',
            f'From: {name}\nEmail: {email}\n\nMessage:\n{message}',
            settings.DEFAULT_FROM_EMAIL,
            ['Okolovictor307@gmail.com'],
            fail_silently=True,
        )
        messages.success(request, 'Message sent! We will get back to you soon.')
        return render(request, 'listings/support.html', {'sent': True})
    
    return render(request, 'listings/support.html')

def about(request):
    return render(request, 'listings/about.html')