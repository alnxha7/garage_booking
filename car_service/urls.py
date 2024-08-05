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

    path('garage_index/', views.garage_index, name='garage_index'),
    path('garage_services/', views.garage_services, name='garage_services'),
    path('add-service/', views.add_service, name='add_service'),
    path('delete-service/<int:service_id>/', views.delete_service, name='delete_service'),

    path('my_schedules/', views.my_schedules, name='my_schedules'),
    path('book_service/', views.book_service, name='book_service'),
    path('reserved_bookings/<int:garage_id>/', views.reserved_bookings, name='reserved_bookings'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
