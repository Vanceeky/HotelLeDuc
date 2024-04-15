from django.shortcuts import render
from booking.models import *
from django.http import HttpResponseRedirect
from restaurant.models import Order
from django.db.models import Count  # Import Count for room count annotation
from django.db.models import Q
# Create your views here.
from django.http import JsonResponse
from datetime import datetime, timedelta, date
import json
from django.shortcuts import redirect, get_object_or_404
import decimal
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse

def room_types_list(request):
  """API endpoint to retrieve all room types."""

  room_types = RoomType.objects.all()
  data = []
  for room_type in room_types:
    data.append({
      'id': room_type.id,
      'name': room_type.name,
      'description': room_type.description,
      'rate_per_night': float(room_type.rate_per_night),
      'slug': room_type.slug,
      # Add image URL if images field is used
      # 'image_url': room_type.images.url if room_type.images else None,
    })

  return JsonResponse(data, safe=False)

def available_room_list(request, room_type_pk):
  """API endpoint to retrieve available rooms for a specific room type."""

  try:
    room_type = RoomType.objects.get(pk=room_type_pk)
  except RoomType.DoesNotExist:
    return JsonResponse({'error': 'Invalid room type ID'}, status=404)  # Use status code for errors

  available_rooms = Room.objects.filter(room_type=room_type, status='available')
  data = []
  for room in available_rooms:
    data.append({
      'id': room.id,
      'room_number': room.room_number,
      'name': room.name,
      'room_type': room.room_type.name,  # Include room type name
      # Add image URL if images field is used
      # 'image_url': room.images.url if room.images else None,
    })
  return JsonResponse(data, safe=False)



def get_guest_reservation(request, pk):
    reservation = Reservation.objects.get(id=pk, status="confirmed")
    data = {
       # 'room_type': str(reservation.room_type),
        'room': f"{reservation.room_type} - Room #{ reservation.room.room_number} - ({reservation.room.room_type.rate_per_night})",
        'room_id': reservation.room.id,
        'guest_id': reservation.guest.id,
        'guest_name': f"{reservation.guest.firstname} {reservation.guest.lastname}",
        'room_number': reservation.room.room_number,
        'room_rate': reservation.room.room_type.rate_per_night,
        'check_in': reservation.check_in,
        'check_out': reservation.check_out,
        'amount_to_pay': reservation.total_amount,
        'amount_paid': reservation.amount_paid,
        'status': reservation.status,
    }
    print(data)
    return JsonResponse(data, safe=False)




def confirm_reservation2(request, pk):
  reservation = Reservation.objects.get(id = pk)
  room_type = reservation.room_type  # Assuming a room type is selected during reservation

  # Check for available rooms based on room type and date overlap
  available_rooms = Room.objects.filter(
      room_type=room_type,
      status='available',  # Only consider available rooms
  ).annotate(
      num_reservations=Count('reservedroom__reservation', filter=Q(reservedroom__reservation__status='confirmed'))
  ).filter(num_reservations__lt=4)  # Less than 4 confirmed reservations (assuming 4 rooms per type)

  # Check for overlapping reservations for each available room
  for room in available_rooms:
    overlapping_reservations = ReservedRoom.objects.filter(
        room=room,
        reservation__status='confirmed',
        reservation__check_in__lte=reservation.check_in,
        reservation__check_out__gte=reservation.check_out,
    )
    if not overlapping_reservations.exists():
      # No overlapping reservations found, assign this room
      reserved_room = ReservedRoom.objects.create(
          reservation=reservation,
          room=room,
      )
      reservation.status = 'confirmed'
      reservation.room = room
      reservation.save()
      message = "Room assigned successfully and reservation confirmed!"
      return redirect('booking:reservation')

  # No available room found
  message = "No available room found for the selected dates. Please try a different room type or dates."
  return redirect('booking:reservation')


def confirm_reservation(request, pk):
    reservation = Reservation.objects.get(id=pk)
    room_type = reservation.room_type

    total_rooms = Room.objects.filter(room_type=room_type).count() #remove this
    
    available_rooms = Room.objects.filter(
        room_type=room_type,
        status='available',
    ).annotate(
        num_reservations=Count('reservedroom__reservation', filter=Q(reservedroom__reservation__status='confirmed'))
    ).filter(num_reservations__lt=total_rooms) #less than 4

    for room in available_rooms:
        overlapping_reservations = ReservedRoom.objects.filter(
            room=room,
            reservation__status='confirmed',
            reservation__check_in__lte=reservation.check_in,
            reservation__check_out__gte=reservation.check_out,
        )
        if not overlapping_reservations.exists():
            reserved_room = ReservedRoom.objects.create(
                reservation=reservation,
                room=room,
            )
            reservation.status = 'confirmed'
            reservation.room = room
            reservation.save()

            # Send confirmation email
            subject = 'Reservation Confirmation'
            context = {
                'reservation': reservation,
                'room': room,
            }
            html_message = render_to_string('booking/confirmation_email.html', context)
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER  # Use the configured email address
            to_email = [reservation.guest.email]
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

            return redirect('booking:reservation')

    return redirect('booking:reservation')

def dashboard(request):
    return render(request, 'booking/index.html')

def booking(request):
    bookings = Booking.objects.all()

    today = date.today()
    tomorrow = today + timedelta(days=1)

  # Today's Check-Ins
    today_reservations = Reservation.objects.filter(
        check_in=today,  # Check-in on today only
        status='confirmed'
    ).order_by('check_in')

    # Tomorrow's Check-Ins
    tomorrow_reservations = Reservation.objects.filter(
        check_in=tomorrow,  # Check-in on tomorrow only
        status='confirmed'
    ).order_by('check_in')

    context = {
        'bookings': bookings,
        'today_reservations': today_reservations,
        'tomorrow_reservations': tomorrow_reservations,
        'today': today,
    }

    print(today)
    print(tomorrow)
    return render(request, 'booking/booking.html', context)

def booking_details(request, pk):
    booking = Booking.objects.get(id=pk)
    
    if booking.order:
        room_order = booking.order
    else:
        room_order = None

    context = {
    'booking': booking,
    'order': room_order,
    }
    return render(request, 'booking/booking_details.html', context)




def generate_invoice_booking(request, pk):
  try:
    booking = Booking.objects.get(id=pk)
    orders_list = Order.objects.filter(booking=booking).first()  # Get first order or None
  except Booking.DoesNotExist:
    # Handle case where booking doesn't exist (optional)
    return render(request, 'booking/invoice_error.html', {'message': 'Booking not found'})

  context = {
    'booking': booking,
    'order': orders_list,  # Can be None if no order exists
    'order_list': orders_list.items.all() if orders_list else [],  # Empty list if no order
  }
  return render(request, 'booking/invoice.html', context)

def add_new_booking(request):
    if request.method == 'POST':
       room_type_id = request.POST.get('room_type_id')
       room_id = request.POST.get('room_id')
       check_in = request.POST.get('check_in')
       check_out = request.POST.get('check_out')
       amount_to_pay = request.POST.get('amount_to_pay')
       amount_paid = request.POST.get('amount_paid')

       firstname = request.POST.get('firstname')
       lastname = request.POST.get('lastname')
       email = request.POST.get('email')
       phone_number = request.POST.get('phone_number')
       address = request.POST.get('address')
       guest, created = Guest.objects.get_or_create(
          email=email,  # Use unique field like email
          defaults={
              'firstname': firstname,
              'lastname': lastname,
              'phone_number': phone_number,
              'address': address,
          }
        )
       #guest = Guest.objects.create(firstname=firstname, lastname=lastname, email=email, phone_number=phone_number, address=address)
       guest.save()

       room_type = RoomType.objects.get(id=room_type_id)
       room = Room.objects.get(id=room_id)

       booking = Booking.objects.create(
          #room_type=room_type, 
          room=room, 
          check_in=check_in, 
          check_out=check_out, 
          amount_to_pay=amount_to_pay, 
          amount_paid=amount_paid, 
          guest=guest
        )
        
       room.status = 'occupied'
       room.save()
       booking.save()
       messages.success(request, 'Guest successfully added to the booking!')
       return redirect('booking:booking')
       
def add_reservation_to_booking(request):
    if request.method == 'POST':
        room_id = request.POST.get('reserved_room_id')
        guest_id = request.POST.get('guest_id_reserved')

        check_in = request.POST.get('check_in_reserved')
        check_out = request.POST.get('check_out_reserved')

        amount_to_pay = request.POST.get('amount_to_pay_reserved')
        amount_paid = request.POST.get('amount_paid_reserved')

        print(f"Amount paid: {amount_paid}")
        print(f"Check in: {check_in}")

        if request.POST.get('balance_reserved'):
            balance = request.POST.get('balance_reserved')
            
            balance = decimal.Decimal(balance)
            amount_paid = decimal.Decimal(amount_paid)
            print(f"Balance: {balance}")
            amount_paid += balance
            booking = Booking.objects.create(
                room_id=room_id,
                guest_id=guest_id,
                check_in=check_in,
                check_out=check_out,
                amount_to_pay=amount_to_pay,
                amount_paid=amount_paid
            )
            booking.save()
            messages.success(request, 'Guest successfully added to the booking!')
            return redirect('booking:booking-details', pk=booking.id)
        
        else:
            booking = Booking.objects.create(
                room_id=room_id,
                guest_id=guest_id,
                check_in=check_in,
                check_out=check_out,
                amount_to_pay=amount_to_pay,
                amount_paid=amount_paid
            )
            booking.save()
            messages.success(request, 'Guest successfully added to the booking!')
            return redirect('booking:booking-details', pk=booking.id)
        
    return redirect('booking:booking')
   

def pay_balance(request, pk):
  if request.method == 'POST':
    booking_id = request.POST.get('booking_id')
    balance_str = request.POST.get('balance')

    try:
      balance = decimal.Decimal(balance_str)  # Convert string to decimal
    except ValueError:
      balance = decimal.Decimal('0.0')  # Set balance to 0.0 in case of conversion error

    booking = Booking.objects.get(id=booking_id)
    amount_paid = booking.amount_paid
    booking.status = 'checked-out'

    # Check if balance is a decimal before adding
    if isinstance(balance, decimal.Decimal):
      amount_paid += balance

    booking.amount_paid = amount_paid
    room = booking.room
    room.status = 'cleaning'
    room.save()
    booking.save()

    return redirect('booking:generate-booking-invoice', pk=booking_id)
   
def checkout_guest(request, pk):
  booking = Booking.objects.get(id=pk)
  room = booking.room
  booking.status = 'checked-out'
  room.status = 'cleaning'
  room.save()
  booking.save()

  return redirect('booking:generate-booking-invoice', booking.id)



def rooms(request):
    """Fetches detailed room type information and displays it with associated rooms."""

  # Get all unique room types with details (avoid duplicates)
    room_types = RoomType.objects.prefetch_related('room_set').annotate(
        available_room_count=Count('room', filter=Q(room__status='available'))
    ).annotate(room_count=Count('room'))
    context = {
        'room_types': room_types,
    }
    return render(request, 'booking/rooms.html', context)



def guest(request):
    guests = Guest.objects.all()
    context = {
        'guests': guests
    }
    return render(request, 'booking/guest.html', context)

def guest_profile(request, pk):
    guest = Guest.objects.get(id=pk)
    reservation = Reservation.objects.filter(guest=guest)
    booking = Booking.objects.filter(guest=guest)
    context = {
        'guest': guest,
        'reservation': reservation,
        'booking': booking
    }
    return render(request, 'booking/guest_profile.html', context)


def reservation(request):
    reservations = Reservation.objects.all()
      # List to store unavailable dates
    unavailable_dates = []
    for reservation in reservations:
      try:
          reserved_room = ReservedRoom.objects.get(reservation=reservation)
          room = reserved_room.room
          # Add unavailable dates for this reservation to the list
          unavailable_dates.extend(get_unavailable_dates(reservation.check_in, reservation.check_out))
      except ReservedRoom.DoesNotExist:
          # Handle missing room case (optional)
          pass
      except ReservedRoom.MultipleObjectsReturned:
          # Handle multiple rooms case (log error, display message, etc.)
          print(f"WARNING: Multiple ReservedRoom objects found for reservation {reservation.id}")
          pass
    context = {
        'reservations': reservations
    }
    return render(request, 'booking/reservation.html', context)

def reservations_test(request):
  # Fetch all active reservations
  reservations = Reservation.objects.filter(is_active=True)

  # List to store unavailable dates
  unavailable_dates = []

  for reservation in reservations:
      try:
          reserved_room = ReservedRoom.objects.get(reservation=reservation)
          room = reserved_room.room
          # Add unavailable dates for this reservation to the list
          unavailable_dates.extend(get_unavailable_dates(reservation.check_in, reservation.check_out))
      except ReservedRoom.DoesNotExist:
          # Handle missing room case (optional)
          pass
      except ReservedRoom.MultipleObjectsReturned:
          # Handle multiple rooms case (log error, display message, etc.)
          print(f"WARNING: Multiple ReservedRoom objects found for reservation {reservation.id}")
          pass

  context = {'reservations': reservations, 'unavailable_dates': unavailable_dates}
  return render(request, 'booking/test.html', context)




def get_unavailable_dates(check_in, check_out):

  check_in_str = check_in.strftime('%Y-%m-%d')
  check_out_str = check_out.strftime('%Y-%m-%d')


  start_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
  end_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()


  unavailable_dates = []
  current_date = start_date
  while current_date <= end_date:
      unavailable_dates.append(current_date)
      current_date += timedelta(days=1)

  return unavailable_dates



def function_hall(request):
   return render(request, 'booking/function_hall.html')



def check_availability_view2(request, room_slug):

  if request.method == 'POST':

    check_in_str = request.POST.get('checkIn_check')
    check_out_str = request.POST.get('checkOut_check')


    try:
      check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
      check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:

      error_message = "Invalid date format. Please use YYYY-MM-DD."
      return render(request, 'home/room.html', {'room_slug': room_slug, 'error_message': error_message})

    
    try:
      room_type = RoomType.objects.get(slug=room_slug)
    except RoomType.DoesNotExist:
    
      error_message = "Room type not found."
      return render(request, 'home/room.html', {'room_slug': room_slug, 'error_message': error_message})

  
    total_rooms = Room.objects.filter(room_type=room_type).count()

 
    overlapping_reservations = False
    for room in Room.objects.filter(room_type=room_type):
      reservations = Reservation.objects.filter(
          room=room,
         
          check_out__gte=check_in,
          check_in__lte=check_out
      )

 
      if reservations.exists():
        overlapping_reservations = True
        break 


    context = {
      'room_slug': room_slug,
      'check_in': check_in.strftime('%Y-%m-%d'),  
      'check_out': check_out.strftime('%Y-%m-%d'),
    }


    if not overlapping_reservations:
        context['available_message'] = f"{total_rooms} rooms of this type are available for your selected dates."
    else:
        context['no_availability_message'] = "No rooms of this type are available for the selected dates."

    return render(request, 'home/room.html', context)
  


  else:

    try:
      room_type = RoomType.objects.get(slug=room_slug)
    except RoomType.DoesNotExist:
 
      error_message = "Room type not found."
      return render(request, 'home/room.html', {'room_slug': room_slug, 'error_message': error_message})


    context = {'room_slug': room_slug}
    return render(request, 'home/room.html',  context)
  

def check_availability_view(request, room_slug):
    if request.method == 'POST':
      
        check_in_str = request.POST.get('checkIn_check')
        check_out_str = request.POST.get('checkOut_check')

    
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        except ValueError:
          
            return JsonResponse({'error_message': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

   
        try:
            room_type = RoomType.objects.get(slug=room_slug)
        except RoomType.DoesNotExist:
        
            return JsonResponse({'error_message': 'Room type not found.'}, status=404)

 
        overlapping_reservations = Reservation.objects.filter(
            room__room_type=room_type,
            check_out=check_out,
            check_in=check_in
        ).exists()

        if overlapping_reservations:
            return JsonResponse({'no_availability_message': 'No rooms of this type are available for the selected dates.'})

 
        available_rooms = Room.objects.filter(
            room_type=room_type,
            status='available'
        ).count()


        response_data = {
            'room_slug': room_slug,
            'check_in': check_in.strftime('%Y-%m-%d'),
            'check_out': check_out.strftime('%Y-%m-%d'),
        }


        if available_rooms > 0:
            response_data['available_message'] = f"There is an available room of this type for your selected dates."
        else:
            response_data['no_availability_message'] = "No rooms of this type are available for the selected dates."

        return JsonResponse(response_data)


    return JsonResponse({'error_message': 'Method not allowed.'}, status=405)