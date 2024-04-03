from django.shortcuts import render
from booking.models import *
from restaurant.models import Order
from django.db.models import Count  # Import Count for room count annotation
from django.db.models import Q
# Create your views here.
from django.http import JsonResponse
from datetime import datetime
import json

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