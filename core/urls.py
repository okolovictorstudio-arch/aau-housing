from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from listings import views as listing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),
    path('accounts/', include('accounts.urls')),
    path('support/', listing_views.support, name='support'),
    path('about/', listing_views.about, name='about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)