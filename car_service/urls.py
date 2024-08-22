"""
URL configuration for car_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from car import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register_user/', views.register_user, name='register_user'),
    path('register_centre/', views.register_centre, name='register_centre'),

    path('user_index/', views.user_index, name='user_index'),
    path('view_service_centers/', views.view_service_centers, name='view_service_centers'),
    path('garage-details/', views.garage_details, name='garage_details'),
    path('garage_booking/<int:garage_id>/', views.garage_booking, name='garage_booking'),

    path('garage_index/', views.garage_index, name='garage_index'),
    path('garage_services/', views.garage_services, name='garage_services'),
    path('add-service/', views.add_service, name='add_service'),
    path('delete-service/<int:service_id>/', views.delete_service, name='delete_service'),

    path('my_schedules/', views.my_schedules, name='my_schedules'),
    path('book_service/', views.book_service, name='book_service'),
    path('reserved_bookings/<int:garage_id>/', views.reserved_bookings, name='reserved_bookings'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),

    path('book-service', views.book_service, name='book_service'),
    path('check_availability/', views.check_availability, name='check_availability'),
    path('payment/', views.payment, name='payment'),
    path('confirm_payment/', views.confirm_payment, name='confirm_payment'),
    path('success/', views.success, name='success'),

    path('booking-history/', views.booking_history, name='booking_history'),
    path('todays_bookings/', views.todays_bookings, name='todays_bookings'),
    path('update_booking_status/', views.update_booking_status, name='update_booking_status'),
    path('track/', views.track, name='track'),

    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('save_vehicle_details/', views.save_vehicle_details, name='save_vehicle_details'),
    path('check_vehicle_details/', views.check_vehicle_details, name='check_vehicle_details'),
    path('emergency_servcie/', views.emergency_service, name='emergency_service'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
