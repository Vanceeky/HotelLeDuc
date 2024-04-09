from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "home"

urlpatterns = [
    path('', views.home, name='home'),
    path('room/', views.room, name='room'),
    path('room/<slug:room_slug>/', views.get_room_details, name='room_detail'),
    path('get_room_reservations/<str:room_slug>/', views.get_room_reservations, name='get_room_reservations'),
    path('guest-reservation/', views.guest_reservation, name='guest-reservation'),
    #path('fetch-room-availability/<int:room_type_id>/<str:start_date>/<str:end_date>/', views.fetch_room_availability, name='fetch_availability'),
    path('fetch-room-availability/<int:room_type_id>/<str:start_date>/<str:end_date>/', views.fetch_room_availability, name='fetch_availability'),


]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
