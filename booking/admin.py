from django.contrib import admin
from .models import *


# Customize the admin display for each model

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rate_per_night', 'max_occupancy', 'description')  # Fields to display in the list view
    search_fields = ('name',)  # Fields to allow searching by
    prepopulated_fields = {'slug': ('name',)}  # Automatically generate slug from name (optional)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_number', 'room_type', 'name', 'status')
    search_fields = ('room_number', 'room_type__name')  # Search by room number and room type name
    list_filter = ('room_type', 'status',)  # Filter by room type and availability
@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_type', 'image_thumbnail')
    readonly_fields = ('image_thumbnail',)

    def image_thumbnail(self, obj):
        if obj.image:
            return '<img src="{}" style="max-width: 200px; max-height: 200px;" />'.format(obj.image.url)
        else:
            return '(No image)'
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = 'Thumbnail'

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'room', 'guest', 'date_created', 'check_in', 'check_out', 'is_active', 'total_amount', 'amount_paid', 'status')  # Include new fields
    list_filter = ('room', 'is_active')  # Filters for the list view
    search_fields = ('guest__firstname', 'guest__lastname', 'room__room_number')  # Fields for searching
    date_hierarchy = 'check_in'  # Group reservations by check-in date

    # Add methods for calculating total and down payment
    def calculate_total_amount(self, obj):
        obj.calculate_total_amount()  # Call the method from the model

    def calculate_down_payment(self, obj):
        obj.calculate_down_payment()  # Call the method from the model

    
    actions = [calculate_total_amount, calculate_down_payment]  

admin.site.register(ReservedRoom)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'phone_number')
    search_fields = ('firstname', 'lastname', 'email')  # Allow searching by name and email

admin.site.register(Guest, GuestAdmin)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'guest', 'room', 'check_in', 'check_out', 'has_order', 'status', 'amount_to_pay', 'amount_paid', 'special_requests')


 
    def has_order(self, obj):
        return bool(obj.order)
    has_order.short_description = 'Has Order'

    def has_order_display(self, obj):
        return self.has_order(obj)  # Pass obj to the method

    has_order_display.admin_order_field = 'order'
