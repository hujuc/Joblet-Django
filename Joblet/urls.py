"""
URL configuration for Joblet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='index'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('about/', views.about, name='about'),

    # User
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('edit_profile/<int:user_id>/', views.edit_profile, name='edit_profile'),
    path('services/', views.services, name='services'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('service/<int:service_id>/book/', views.book_service, name='book_service'),
    path('booking/', views.booking, name='booking'),
    path('myorders/', views.myorders, name='myorders'),
    path('myservices/', views.myservices, name='myservices'),
    path('myservices/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('myservices/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('myservices/new/', views.add_service, name='add_service'),
    path('myservices/edit/<int:service_id>/json/', views.get_service_data, name='get_service_data'),

    # Admin
    path('categories/', views.categories, name='categories'),
    path('providers/', views.providers, name='providers'),
    path('pendingservices/', views.pendingservices, name='pendingservices'),
    path('approve-service/<int:service_id>/', views.approve_service, name='approve_service'),
    path('reject-service/<int:service_id>/', views.reject_service, name='reject_service'),
    path('users/', views.users, name='users'),
    path('ban-user/<int:user_id>/', views.ban_user, name='ban_user'),

    # Messages
    path('thread/<int:recipient_id>/', views.message_thread, name='message_thread'),

    path('update-booking-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),

    # Chat
    path('booking/<int:booking_id>/chat/', views.chat_view, name='chat_view'),
    path('chats/', views.user_chats, name='user_chats'),
    path('message/<int:recipient_id>/', views.send_message, name='send_message'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),

    # Bookings
    path('myservices/<int:service_id>/pending_bookings/', views.pending_bookings, name='pending_bookings'),
    path('myservices/<int:service_id>/in_progress_bookings/', views.in_progress_bookings, name='in_progress_bookings'),
    path('booking/<int:booking_id>/accept/', views.accept_booking, name='accept_booking'),
    path('booking/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)