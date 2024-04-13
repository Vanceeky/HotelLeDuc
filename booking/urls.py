from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('booking/', views.booking, name='booking'),
    path('booking-details/<int:pk>/', views.booking_details, name='booking-details'),
    path('generate-booking-invoice/<int:pk>/', views.generate_invoice_booking, name="generate-booking-invoice"),
    path('pay-balance/<int:pk>/', views.pay_balance, name="pay-balance"),
    path('checkout-guest/<int:pk>/', views.checkout_guest, name="checkout-guest"),


    path('add-new-booking/', views.add_new_booking, name='add-new-booking'),

    path('reservation/', views.reservation, name='reservation'),
    path('reservations/<int:pk>/confirm/', views.confirm_reservation, name='confirm_reservation'),
    path('get-reservation-details/<int:pk>/', views.get_guest_reservation, name='get-reservation-details'),
    path('add-reservation-to-booking/', views.add_reservation_to_booking, name="add-reservation-to-booking"),
    path('rooms/', views.rooms, name='rooms'),


    path('guest/', views.guest, name='guest-list'),
    path('guest-profile/<int:pk>/', views.guest_profile, name='guest-profile'),

    path('api/room-types/', views.room_types_list, name='room-types-list'),
    path('api/available-rooms/<int:room_type_pk>/', views.available_room_list, name='available-rooms-list'),

    path('test/', views.reservations_test, name="test"),



]
