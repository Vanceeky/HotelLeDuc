from django.shortcuts import render
from booking.models import Amenity, RoomType, Room, Reservation, Guest

import datetime
from datetime import date

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

# Create your views here.

def home(request):
    rooms = RoomType.objects.all()
    room_types_with_images = []

    # Iterate over each room type
    for room_type in rooms:
        # Retrieve images for the current room type
        room_images = room_type.images.all()

        # Append the room type and its images to the list
        room_types_with_images.append({'room_type': room_type, 'room_images': room_images})

    guests = Guest.objects.all()
    context = {
        'rooms': rooms,
        'guests': guests,
        'room_types_with_images': room_types_with_images,
    }
    return render(request, 'home/index.html', context)

def room(request):
    return render(request, 'home/room.html')

def get_room_details(request, room_slug):
  

  if not room_slug:
    raise ValueError("room_slug cannot be empty")

  try:
    room_slug = RoomType.objects.get(slug=room_slug)
    room_images = room_slug.images.all()
    rooms = list(room_slug.room_set.all())  # Efficiently retrieve rooms with prefetching
  except Room.DoesNotExist:
    return None

  context = {
     'room_slug': room_slug,
     'rooms': rooms,
     'room_images': room_images
  }

  print(room_slug.rate_per_night)

  return render(request, 'home/room.html', context)



def get_room_reservations(request, room_slug):
    try:
        room_type = RoomType.objects.get(slug=room_slug)
        reservations = Reservation.objects.filter(room__room_type=room_type, is_active=True, status='confirmed')
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
    except RoomType.DoesNotExist:
        return JsonResponse({"error": "Room type not found"}, status=404)

def fetch_room_availability(request, room_type_id, start_date, end_date):
  """
  View function to fetch room availability data and potential overlaps for a specific room type and date range.
  """
  room_type = get_object_or_404(RoomType, pk=room_type_id)
  reservations = Reservation.objects.filter(
      room_type=room_type,
      status='confirmed'
  )

  # Check for all rooms booked and potential overlaps
  available_rooms = Room.objects.filter(room_type=room_type).exclude(
      pk__in=[reservation.room.pk for reservation in reservations]
  )
  overlaps = reservations.filter(
      Q(Q(check_in__lte=end_date) & Q(check_out__gte=start_date)) |  # Overlap with requested dates
      Q(Q(check_in__lt=start_date) & Q(check_out__gt=end_date))  # Requested dates within existing reservation
  )

  # Prepare JSON response data
  response_data = {
      'roomType': room_type.name,
      'allRoomsBooked': not available_rooms.exists(),
      'overlapsExist': overlaps.exists(),
      'events': []  # Optional: Include existing reservations for calendar display
  }

  # ... rest of the logic to populate events (optional)

  return JsonResponse(response_data)

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
