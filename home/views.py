from django.shortcuts import render
from booking.models import Amenity, RoomType, Room, Reservation, Guest

import datetime
from datetime import date

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect

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
    'id': room_slug.id,
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

def guest_reservation(request):



  if request.method == 'POST':
    # Extract data from the HTML form
    room_type_id = request.POST.get('room_type')
    guest_firstname = request.POST.get('firstname')
    guest_lastname = request.POST.get('lastname')
    guest_email = request.POST.get('email')
    guest_phone = request.POST.get('phone_number')
    guest_address = request.POST.get('address')
    check_in = request.POST.get('check_in')
    check_out = request.POST.get('check_out')
    amount_paid = request.POST.get('amount_paid')
    receipt = request.FILES.get('receipt')
    # Basic validation (you can improve this further)
    errors = []
    if not room_type_id:
      errors.append("Please select a room type.")

    try:
      check_in_date = date.fromisoformat(check_in)
      check_out_date = date.fromisoformat(check_out)
      if check_in_date > check_out_date:
        errors.append("Check-in date must be before check-out date.")
    except ValueError:
      errors.append("Invalid date format. Please use YYYY-MM-DD.")

        # File validation (optional, but recommended)
      if receipt:
            # Check for allowed file types (e.g., image/jpeg, application/pdf)
          allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
          if receipt.content_type not in allowed_types:
              errors.append("Invalid file type. Please upload a JPEG, PNG, or PDF receipt.")


    # If no errors, process reservation
    if not errors:
            # Create guest object (if not already created)
      guest, created = Guest.objects.get_or_create(
          email=guest_email,  # Use unique field like email
          defaults={
              'firstname': guest_firstname,
              'lastname': guest_lastname,
              'phone_number': guest_phone,
              'address': guest_address,
          }
      )

      room_type = RoomType.objects.get(id=room_type_id)
      reservation = Reservation.objects.create(
                room_type=room_type,
                guest=guest,
                check_in=check_in_date,
                check_out=check_out_date,
                amount_paid=amount_paid,
                images=receipt,  # Assuming you want to save the receipt
      )
      reservation.calculate_total_amount()
 
      reservation.save() 

      return redirect('home:home') 

  else:

    return redirect('home') 
