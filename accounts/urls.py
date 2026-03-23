from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('listing/add/', views.add_listing, name='add_listing'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('setup-admin/', views.create_admin, name='create_admin'),
]