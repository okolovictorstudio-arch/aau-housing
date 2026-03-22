from django.contrib import admin
from .models import Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 3


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'agent', 'property_type', 'price', 'location', 'status', 'is_approved', 'created_at']
    list_filter = ['property_type', 'status', 'is_approved']
    search_fields = ['title', 'location', 'agent__username']
    list_editable = ['is_approved', 'status']
    inlines = [ListingImageInline]


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'uploaded_at']

from .models import AgentProfile

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_subscribed', 'subscription_expires']