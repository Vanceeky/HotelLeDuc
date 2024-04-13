from django.db import IntegrityError
from django.shortcuts import render, redirect
from booking.models import *
from django.db.models import Count, Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def dashboard(request):
    return render(request, 'management/dashboard.html')


def rooms(request):
    amenities = Amenity.objects.all()
    room_types = RoomType.objects.prefetch_related('room_set').annotate(
        available_room_count=Count('room', filter=Q(room__status='available')),
    ).annotate(room_count=Count('room'))

    context = {
        'room_types': room_types,
        'amenities': amenities
    }

    return render(request, 'management/rooms.html', context)

def add_room_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        rate_per_night = request.POST.get('rate_per_night')
        max_occupancy = request.POST.get('max_occupancy')  # Get occupancy (might be empty)
        selected_amenities = request.POST.getlist('category')  # Get list of selected amenities
        room_images = request.FILES.getlist('room_images')  # Get list of uploaded images
        slug = request.POST.get('slug')  # Fix the typo here

        # Validation (you can enhance this further)
        if not name or not description or not rate_per_night:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'management/rooms.html', {'amenities': Amenity.objects.all()})

        try:
            # Attempt to create RoomType object
            room_type = RoomType.objects.create(
                name=name,
                description=description,
                rate_per_night=rate_per_night,
                max_occupancy=max_occupancy,
                slug=slug,
            )

            # Add selected amenities to the room type
            room_type.amenities.add(*selected_amenities)

            # Save uploaded room images
            if room_images:
                for image in room_images:
                    room_image = RoomImage.objects.create(room_type=room_type, image=image)
                    room_image.save()

            messages.success(request, 'Room type added successfully!')
            return redirect('management:rooms')  # Redirect to room type list view

        except IntegrityError:
            # Handle duplicate room type exception
            messages.error(request, 'Room type with that name already exists. Please choose a unique name.')
            return HttpResponseRedirect(reverse('management:rooms'))

    else:
        amenities = Amenity.objects.all()
        return render(request, 'management/rooms.html', {'amenities': amenities})
    
def add_room(request):
    if request.method == 'POST':
        room_type = request.POST.get('category')
        name = request.POST.get('room_name')
        room_number = request.POST.get('room_number')
        room_type = RoomType.objects.get(id=room_type)
        room = Room.objects.create(room_type=room_type, name=name, room_number=room_number)
        room.save()
        return redirect('management:rooms')
