from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, Garage, GarageService, Booking, BookingHistory, TodayBookingStatus, Vehicle
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.utils import timezone
import json
import uuid
import logging
from decimal import Decimal
from datetime import date, datetime

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index.html')

def login(request):
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

        # Authenticate the user
            user = authenticate(request, email=email, password=password)
        
            if user is not None:
                auth_login(request, user)
                if user.role == 'user':
                    return redirect('user_index')
                else:
                    return redirect('garage_index')  # Adjust this to the correct URL name for 'garage' or other roles
            else:
                messages.error(request, 'Invalid email or password.')
                print(f'Authentication failed for email: {email}')  # Debugging line to check failed attempts

        return render(request, 'login.html')

def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        role = 'user'  # Default role for user registration

        try:
            if phone and phone.isdigit() and len(phone) == 10:
                user = User.objects.create_user(email=email, username=username, password=password, phone=phone, role=role)
                user.save()
                messages.success(request, 'User registered successfully.')
                return redirect('login')
            else:
                return redirect('register_user')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'register_user.html')

def register_centre(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        images = request.FILES.get('images')
        role = 'garage'

        try:
            if phone and phone.isdigit() and len(phone) == 10:
                user = User.objects.create_user(username=username, email=email, password=password, role=role)
                user.save()

                garage = Garage.objects.create(
                    user=user,
                    location=location,
                    phone=phone,
                    images=images,
                    approved=False
                )
                garage.save()
                messages.success(request, 'Garage registration request sent for approval.')
                return redirect('login')
        
        except Exception as e:
            messages.error(request, f'An error occurred while creating the garage request: {e}')
            print(f'An error occurred while creating the garage request: {e}')

    return render(request, 'register_centre.html')

def user_index(request):
    return render(request, 'user_index.html')

@login_required
def view_service_centers(request):
    garages = Garage.objects.filter(approved=True)
    context = {
        'garages': garages,
        'user': request.user,
    }
    return render(request, 'view_service_centers.html', context)

@login_required
def garage_details(request):
    if request.method == 'GET':
        garage_id = request.GET.get('id')
        
        # Using get_object_or_404 for better error handling
        garage = get_object_or_404(Garage, id=garage_id)
        
        # Fetch related services
        services = list(garage.services.values('service_name', 'price', 'max_per_slot'))
        
        data = {
            'location': garage.location,
            'phone': garage.phone,
            'services': services,
        }
        
        return JsonResponse(data)

@login_required
def garage_index(request):
     garage = get_object_or_404(Garage, user=request.user)
     context = {
        'garage': garage,
    }
     return render(request, 'garage_index.html', context)

@login_required
def garage_services(request):
    garage = get_object_or_404(Garage, user=request.user)
    services = GarageService.objects.filter(garage=garage)
    
    if request.method == 'POST':
        if 'edit_service_id' in request.POST:
            service_id = request.POST.get('edit_service_id')
            service_name = request.POST.get('edit_service_name')
            price = request.POST.get('edit_service_price')
            max_per_slot = request.POST.get('edit_service_max_per_slot')

            service = get_object_or_404(GarageService, id=service_id)
            service.service_name = service_name
            service.price = price
            service.max_per_slot = max_per_slot
            service.save()
            return redirect('garage_services')
    
    return render(request, 'garage_services.html', {
        'services': services,
        'garage': garage,  # Ensure this is passed to the template
    })

@login_required
def add_service(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        price = request.POST.get('price')
        max_per_slot = request.POST.get('max_per_slot')

        garage = get_object_or_404(Garage, user=request.user)

        GarageService.objects.create(
            garage=garage,
            service_name=service_name,
            price=price,
            max_per_slot=max_per_slot
        )
        return redirect('garage_services')  # Redirect to the services page

    garage = get_object_or_404(Garage, user=request.user)
    services = GarageService.objects.filter(garage=garage)
    return render(request, 'garage_services.html', {'services': services})

@login_required
def edit_service(request, service_id):
    service = get_object_or_404(GarageService, id=service_id)

    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        price = request.POST.get('price')
        max_per_slot = request.POST.get('max_per_slot')

        service.service_name = service_name
        service.price = price
        service.max_per_slot = max_per_slot
        service.save()

        return redirect('garage_services')  # Redirect to the services page

    return render(request, 'edit_service.html', {'service': service})

@login_required
def delete_service(request, service_id):
    if request.method == 'POST':
        service = GarageService.objects.get(id=service_id)
        service.delete()
        return redirect('garage_services')  # Redirect to the services page

    # Redirect to the services page if not POST
    return redirect('garage_services')

@login_required
def my_schedules(request):
    garage = get_object_or_404(Garage, user=request.user)
    services = GarageService.objects.filter(garage=garage)
    services_json = json.dumps(list(services.values('service_name', 'price')), cls=DjangoJSONEncoder)
    return render(request, 'my_schedules.html', {'garage': garage, 'services_json': services_json})

@csrf_exempt
def book_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Debugging line

            garage_id = data.get('garage_id')
            date = data.get('date')
            slot = data.get('timeSlot')
            service_name = data.get('service')

            # Debugging
            print(f"Garage ID: {garage_id}")
            print(f"Date: {date}")
            print(f"Time Slot: {slot}")
            print(f"Service Name: {service_name}")

            # Fetch service
            try:
                service = GarageService.objects.get(service_name=service_name)
            except GarageService.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Service not found'})

            # Check max_per_slot constraint
            existing_bookings = Booking.objects.filter(
                garage_id=garage_id,
                date=date,
                slot=slot,
                service=service
            ).count()

            if existing_bookings >= service.max_per_slot:
                return JsonResponse({'status': 'error', 'message': 'This slot is fully booked'})

            # Create booking
            booking = Booking(
                garage_id=garage_id,
                date=date,
                slot=slot,
                service=service
            )
            booking.save()
            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging line
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def reserved_bookings(request, garage_id):
    garage = get_object_or_404(Garage, id=garage_id)
    bookings = Booking.objects.filter(garage_id=garage_id)
    context = {
        'bookings': bookings,
        'garage': garage,
    }
    return render(request, 'reserved_bookings.html', context)

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    garage_id = booking.garage_id
    booking.delete()
    return redirect('reserved_bookings', garage_id=garage_id)

@login_required
def garage_booking(request, garage_id):
    garage = get_object_or_404(Garage, id=garage_id)
    services = GarageService.objects.filter(garage_id=garage_id)
    
    context = {
        'garage': garage,
        'garage_id': garage_id,
        'services': services,
    }
    return render(request, 'garage_booking.html', context)

@csrf_exempt
def book_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            garage_id = data.get('garage_id')
            date = data.get('date')
            slot = data.get('timeSlot')
            service_name = data.get('service')

            if not all([garage_id, date, slot, service_name]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

            service = GarageService.objects.get(service_name=service_name)
            existing_bookings = Booking.objects.filter(
                garage_id=garage_id,
                date=date,
                slot=slot,
                service=service
            ).count()

            if existing_bookings >= service.max_per_slot:
                return JsonResponse({'status': 'error', 'message': 'This slot is fully booked'})

            Booking.objects.create(
                garage_id=garage_id,
                date=date,
                slot=slot,
                service=service
            )
            return JsonResponse({'status': 'success'})

        except GarageService.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Service not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def check_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            garage_id = data.get('garage_id')
            date = data.get('date')
            time_slot = data.get('timeSlot')
            selected_service_name = data.get('selected_service_name')

            if not all([garage_id, date, time_slot, selected_service_name]):
                return JsonResponse({'status': 'error', 'message': 'Missing required parameters'})

            # Retrieve the service associated with the garage and the selected service
            service = GarageService.objects.filter(garage_id=garage_id, service_name=selected_service_name).first()
            if not service:
                return JsonResponse({'status': 'error', 'message': 'Service not found'})

            # Get the garage name
            garage_name = service.garage.user.username

            # Check the number of bookings for the selected slot for this service
            existing_bookings = Booking.objects.filter(
                garage_id=garage_id,
                date=date,
                slot=time_slot,
                service=service
            ).count()

            if existing_bookings >= service.max_per_slot:
                return JsonResponse({'status': 'error', 'message': 'This slot is fully booked for the selected service'})
            else:
                # Retrieve all services for the garage
                services = GarageService.objects.filter(garage_id=garage_id)
                services_data = [{'name': svc.service_name, 'price': str(svc.price)} for svc in services]

                return JsonResponse({
                    'status': 'available',
                    'garage_name': garage_name,
                    'date': date,
                    'timeSlot': time_slot,
                    'services': services_data
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def payment(request):
    return render(request, 'payment.html')

@csrf_exempt
@login_required
def confirm_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Received data: {data}")

            user = request.user
            total_amount = Decimal(data.get('totalAmount'))  # Convert to Decimal
            garage_name = data.get('garageName')

            try:
                garage_user = User.objects.get(username=garage_name)  # Assuming the name is stored in the User model
                garage = Garage.objects.get(user=garage_user)
                garage_id = garage.id
            except User.DoesNotExist:
                logger.error(f"User with username '{garage_name}' does not exist.")
                return JsonResponse({'success': False, 'error': f"User with username '{garage_name}' does not exist."})
            except Garage.DoesNotExist:
                logger.error(f"Garage for user '{garage_name}' does not exist.")
                return JsonResponse({'success': False, 'error': f"Garage for user '{garage_name}' does not exist."})

            # Fetch and process services
            service_names = data.get('services', [])
            services = GarageService.objects.filter(service_name__in=service_names)

            if not services.exists():
                logger.error(f"No matching services found for: {service_names}")
                return JsonResponse({'success': False, 'error': 'No matching services found.'})

            # Create a booking instance for each service
            for service in services:
                Booking.objects.create(
                    garage_id=garage_id, 
                    date=data.get('date'),
                    slot=data.get('timeSlot'),
                    service=service
                )

            booking_history = BookingHistory.objects.filter(
                garage_name='dummy_garage',
                user_name=user.username,
                slot_booked='2-4',
                service_selected='dummy_service',
            )

            if not booking_history.exists():
                return JsonResponse({'success': False, 'error': 'No valid booking history found for the user'})

            booking_history.update(
                garage_name=garage_name,
                user_name=user.username,
                date_booked=data.get('date'),
                slot_booked=data.get('timeSlot'),
                total_amount=total_amount,
                service_selected=json.dumps(data.get('services')),
                card_number=data.get('cardNumber'),
                cvv=data.get('cardCVV')
            )

            BookingHistory.objects.filter(
                garage_name='dummy_garage',
                user_name=user.username,
                slot_booked='2-4',
                service_selected='dummy_service',
            ).delete()

            return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def success(request):
    unique_id = str(uuid.uuid4())
    return render(request, 'success.html', {'unique_id': unique_id})

@login_required
def booking_history(request):
    user = request.user
    today = date.today()

    if user.role == 'garage':
        try:
            # Fetch the garage associated with the logged-in user
            garage = Garage.objects.get(user=user)
            garage_name = garage.user.username  # Assuming `location` represents the garage name
            # Fetch booking history for the garage
            booking_history = BookingHistory.objects.filter(garage_name=garage_name)
            context = {
                'booking_history': booking_history,
                'viewing_as': 'garage'
            }
        except Garage.DoesNotExist:
            return HttpResponseForbidden("No associated garage found.")
    elif user.role == 'user':
        # Fetch booking history for the logged-in user
        booking_history = BookingHistory.objects.filter(user_name=user.username)
        context = {
            'booking_history': booking_history,
            'viewing_as': 'user',
            'today': today
        }
    else:
        return HttpResponseForbidden("Access denied.")

    return render(request, 'booking_history.html', context)

@login_required
def todays_bookings(request):
    user = request.user
    today = timezone.now().date()
    try:
        garage = Garage.objects.get(user=user)
        garage_name = garage.user.username  # Assuming location represents the garage name
        bookings = BookingHistory.objects.filter(garage_name=garage_name, date_booked=today)
        # Get the current status for each booking
        statuses = TodayBookingStatus.objects.filter(booking_id__in=bookings.values_list('id', flat=True))
        status_dict = {status.booking_id: status.current_status for status in statuses}
        
        # Add current status to each booking
        for booking in bookings:
            booking.current_status = status_dict.get(booking.id, 'waiting')  # Default to 'waiting'
        
    except Garage.DoesNotExist:
        bookings = []

    return render(request, 'todays_bookings.html', {'bookings': bookings})

@login_required
@require_POST
def update_booking_status(request):
    booking_id = request.POST.get('booking_id')
    status = request.POST.get('status')
    
    try:
        today_status = TodayBookingStatus.objects.get(booking_id=booking_id)
        today_status.current_status = status
        today_status.save()
        
        # Return JSON response for AJAX
        return JsonResponse({'success': True})

    except TodayBookingStatus.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Status not found'})
    
@login_required
def track(request):
    user = request.user.username  # Assuming `user` is represented by their username
    today = timezone.now().date()
    try:
        # Fetch bookings with their statuses for the current user and today's date
        bookings = TodayBookingStatus.objects.filter(booking__user_name=user, booking__date_booked=today)
    except TodayBookingStatus.DoesNotExist:
        bookings = []

    return render(request, 'track.html', {'bookings': bookings})

def cancel_booking(request, booking_id):
    if request.method == "POST":
        booking = BookingHistory.objects.get(id=booking_id)

        # Ensure booking is not already canceled
        if booking.is_canceled:
            messages.error(request, "This booking is already canceled.")
            return redirect('booking_history')

        # Calculate the refund and garage earnings
        refund_amount = booking.total_amount * Decimal('0.80')
        garage_earnings = booking.total_amount * Decimal('0.20')

        # Update the booking
        booking.is_canceled = True
        booking.final_price = refund_amount
        booking.garage_earnings = garage_earnings
        booking.save()

        # Display success message
        messages.success(request, "Booking canceled successfully. 80% of the total amount has been refunded.")
        return redirect('booking_history')

    return redirect('booking_history')


@csrf_exempt
@login_required  # Ensure the user is logged in
def save_vehicle_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            number_plate = data.get('numberPlate')
            model = data.get('model')
            user = request.user


            dummy_date = datetime.strptime('1970-12-12', '%Y-%m-%d').date()
            dummy = BookingHistory(
                garage_name='dummy_garage',
                user_name=user.username,
                date_booked=dummy_date,
                date_of_booking=timezone.now(),
                slot_booked='2-4',
                total_amount=Decimal('100.00'),
                service_selected='dummy_service',
                card_number='1234567890123456',
                cvv='123'
            )
            dummy.save()

            # Fetch the exact dummy BookingHistory record created
            booking_history = BookingHistory.objects.get(id=dummy.id)

            if not booking_history:
                dummy.delete()  # Clean up the dummy record if something went wrong
                return JsonResponse({'success': False, 'error': 'No valid booking history found for the user'})

            # Create the Vehicle instance linked to the correct BookingHistory record
            vehicle = Vehicle.objects.create(
                booking_history=booking_history,  # Link to the correct instance
                number_plate=number_plate,
                model=model
            )
            vehicle.save()
            print(vehicle)
  
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def check_vehicle_details(request):
    if request.method == 'GET':
        user = request.user
        
        # Retrieve the booking history for the current user
        booking_history = BookingHistory.objects.filter(user_name=user.username).first()
        
        if booking_history:
            # Check if a vehicle is associated with the found booking history
            vehicle_exists = Vehicle.objects.filter(booking_history=booking_history).exists()
            return JsonResponse({'vehicleDetailsExists': vehicle_exists})
        else:
            return JsonResponse({'vehicleDetailsExists': False})
        
def emergency_service(request):
    garages = Garage.objects.filter(approved=True)
    return render(request, 'emergency_service.html', {'garages': garages})