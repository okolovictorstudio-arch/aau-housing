from django.db import models
from django.contrib.auth.models import User


class Listing(models.Model):
    PROPERTY_TYPES = [
        ('self_con', 'Self Contain'),
        ('single_room', 'Single Room'),
        ('flat', 'Flat / Apartment'),
        ('duplex', 'Duplex'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('taken', 'Taken'),
    ]

    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    whatsapp_number = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"


class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_subscribed = models.BooleanField(default=False)
    subscription_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"