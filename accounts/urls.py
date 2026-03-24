from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password_request'),
    path('forgot-password/verify/', views.forgot_password_verify, name='forgot_password_verify'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('listing/add/', views.add_listing, name='add_listing'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
]