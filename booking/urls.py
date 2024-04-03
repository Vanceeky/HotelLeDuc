from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('booking/', views.booking, name='booking'),
    path('booking-details/<int:pk>/', views.booking_details, name='booking-details'),


    path('reservation/', views.reservation, name='reservation'),
    
    path('rooms/', views.rooms, name='rooms'),


    path('guest/', views.guest, name='guest-list'),
    path('guest-profile/<int:pk>/', views.guest_profile, name='guest-profile'),

    path('api/room-types/', views.room_types_list, name='room-types-list'),
    path('api/available-rooms/<int:room_type_pk>/', views.available_room_list, name='available-rooms-list'),

]
