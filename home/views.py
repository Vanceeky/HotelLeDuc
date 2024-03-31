from django.shortcuts import render
from booking.models import Amenity, RoomType, Room, Reservation

import datetime
from datetime import date

from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

def home(request):
    rooms = RoomType.objects.all()
    context = {
        'rooms': rooms
    }
    return render(request, 'home/index.html', context)

def room(request):
    return render(request, 'home/room.html')

def get_room_details(request, room_slug):
  

  if not room_slug:
    raise ValueError("room_slug cannot be empty")

  try:
    room_slug = RoomType.objects.get(slug=room_slug)
    room = Room.objects.get(room_type=room_slug)
  except Room.DoesNotExist:
    return None

  room_details = {
    'room_number': room.room_number,
    'room_type': room.room_type.name,  # Access name from RoomType
    'name': room.name,  # Optional name
    'slug': room_slug.slug,
    'description': room.description,
    'max_occupancy': room.max_occupancy,
    'amenities': [amenity.name for amenity in room.amenities.all()],  # List of amenity names
    'images': room_slug.images,  # Get URLs of existing images
    'status': room.status,
    'room_rate': room.room_type.rate_per_night
  }

  return render(request, 'home/room.html', {'room_details': room_details}) 





def get_room_reservations(request, room_slug):
    try:
        room = Room.objects.get(room_type__slug=room_slug)
        reservations = Reservation.objects.filter(room=room, is_active=True)
        reservation_data = [
            {
                "id": reservation.id,  # Optional for potential updates
                "title": "Reserved",
                "start": reservation.check_in,
                "end": reservation.check_out + datetime.timedelta(days=1),
            }
            for reservation in reservations
        ]
        return JsonResponse(reservation_data, safe=False)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)
