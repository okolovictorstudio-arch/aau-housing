from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),
    path('accounts/', include('accounts.urls')),
    path('support/', TemplateView.as_view(template_name='support.html'), name='support'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)