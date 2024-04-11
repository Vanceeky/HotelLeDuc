from django.urls import path
from . import views

app_name = "restaurant"
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('menu/', views.menu, name='menu'),
    path('orders/', views.orders, name='orders'),

   # ... other URL patterns ...
    path('api/bookings/<int:room_id>/items/', views.items_for_room, name='items_for_booking'),
    path('api/bookings/<int:booking_id>/<int:item_id>/items/', views.add_item_to_booking, name='add_item_to_booking'),

    path('api/menu-items/', views.menu_items_list, name='menu-items-list'),
    path('create-order-item/', views.create_order_item_ajax, name="create-order-item"),

    path('generate-invoice/<int:pk>/', views.generate_invoice, name="generate-invoice")

  ]
