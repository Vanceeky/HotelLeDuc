from django.urls import path
from . import views

app_name = "restaurant"
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('menu/', views.menu, name='menu'),
    path('add-new-menu/', views.add_new_menu, name='add-new-menu'),

    path('orders/', views.orders, name='orders'),

    path('ordered-items/', views.ordered_items, name="ordered-items"),
    path('prepare-order-item/<int:order_item_id>/', views.prepare_order_item, name="prepare-order-item"),
    path('complete-order-item/<int:order_item_id>/', views.complete_order_item, name="complete-order-item"),


   # ... other URL patterns ...
    path('api/bookings/<int:room_id>/items/', views.items_for_room, name='items_for_booking'),
    path('api/bookings/<int:booking_id>/<int:item_id>/items/', views.add_item_to_booking, name='add_item_to_booking'),

    path('api/menu-items/', views.menu_items_list, name='menu-items-list'),
    path('create-order-item/', views.create_order_item_ajax, name="create-order-item"),

    path('generate-invoice/<int:pk>/', views.generate_invoice, name="generate-invoice")

  ]
