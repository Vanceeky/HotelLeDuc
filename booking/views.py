from django.shortcuts import render
from booking.models import *
from restaurant.models import Order
from django.db.models import Count  # Import Count for room count annotation
from django.db.models import Q
# Create your views here.
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from django.shortcuts import redirect, get_object_or_404


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
      'description': room.description,
      'room_type': room.room_type.name,  # Include room type name
      # Add image URL if images field is used
      # 'image_url': room.images.url if room.images else None,
    })
  return JsonResponse(data, safe=False)

#def confirm_reservation(request, pk):
  reservation = Reservation.objects.get(id = pk)
  
  # Check room availability using the reservation dates
  available_room = Room.objects.filter(status='available').first()

  if available_room:
    # Assign room and update reservation status
    reserved_room = ReservedRoom.objects.create(
        reservation=reservation,
        room=available_room,
    )
    reservation.status = 'confirmed'
    reservation.room = available_room
    reservation.save()


    
    # Success message (consider using Django messages framework)
    message = "Room assigned successfully and reservation confirmed!"
  else:
    # No available room found
    message = "No available room found for the selected dates. Please try a different room or dates."

  return redirect('booking:reservation')

def confirm_reservation(request, pk):
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


def dashboard(request):
    return render(request, 'booking/index.html')

def booking(request):
    bookings = Booking.objects.all()
    context = {
        'bookings': bookings
    }
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
       
       return redirect('booking:booking')
       


   
    
def reservation(request):
    reservations = Reservation.objects.all()
    context = {
        'reservations': reservations
    }
    return render(request, 'booking/reservation.html', context)

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
  # Convert check_in and check_out to date objects
  check_in_str = check_in.strftime('%Y-%m-%d')
  check_out_str = check_out.strftime('%Y-%m-%d')

  # Use strptime to convert strings to date objects
  start_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
  end_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()


  # Create a list to store unavailable dates
  unavailable_dates = []
  current_date = start_date
  while current_date <= end_date:
      unavailable_dates.append(current_date)
      current_date += timedelta(days=1)

  return unavailable_dates
