from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username='aauadmin').exists():
        User.objects.create_superuser('aauadmin', 'admin@cradle.com', 'Aauhousing2026!')
        return HttpResponse('Admin created!')
    return HttpResponse('Admin already exists.')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('setup-admin-x7k2/', create_admin),
    path('', include('listings.urls')),
    path('accounts/', include('accounts.urls')),
    path('support/', TemplateView.as_view(template_name='support.html'), name='support'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)