from django.shortcuts import render, get_object_or_404
from .models import Listing


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