from django.urls import path
from . import views

app_name = "management"
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('room/', views.rooms, name="rooms"),
    path('add-room-type/', views.add_room_type, name="add-room-types"),
    path('add-room/', views.add_room, name="add-room"),
]
