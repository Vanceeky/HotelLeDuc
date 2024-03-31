from django.shortcuts import render
from booking.models import *
from restaurant.models import Order

# Create your views here.

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
    return render(request, 'booking/rooms.html')

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