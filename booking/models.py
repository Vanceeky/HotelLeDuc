from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.


class Amenity(models.Model):
    """
    Model to represent hotel amenities.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    rate_per_night = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    slug = models.SlugField(max_length=100, blank=True, unique=True)  # Add the slug field
    images = models.ImageField(upload_to='room_images/', blank=True)  # Upload images to a directory
    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"

    def __str__(self):
        return self.name

class Room(models.Model):
    """
    Model to represent individual hotel rooms.
    """
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)  # Optional room name (e.g., "Honeymoon Suite")
    description = models.TextField(blank=True)


    # Additional fields:
    max_occupancy = models.PositiveIntegerField(blank=True, null=True)  # Non-negative integer
    amenities = models.ManyToManyField('Amenity', blank=True)  # Relationship with Amenities model

    # **New status field with choices**
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('cleaning', 'Cleaning'), 
        ('maintenance', 'Maintenance')
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='available')


    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"
    

        

    
class Guest(models.Model):
    """
    Model to represent hotel guests.
    """
    firstname = models.CharField(max_length=255, null = True, blank = True)
    lastname = models.CharField(max_length=255, null = True, blank = True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='guest_avatars/', default='/guest_avatars/avatar-default-icon.png')
    class Meta:
        verbose_name = "Guest"
        verbose_name_plural = "Guests"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Reservation(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, null = True, blank = True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null = True, blank = True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    is_active = models.BooleanField(default=True)

    # New fields for payment
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    images = models.ImageField(upload_to='reservation_receipt/', blank=True)  # Upload images to a directory
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('pending', 'pending'),
        ('cancelled', 'Cancelled'),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    def __str__(self):
        return f"{self.guest} - {self.room} ({self.check_in} - {self.check_out})"

    def calculate_total_amount(self):
        # Calculate the total amount based on room rate and number of days
        num_days = (self.check_out - self.check_in).days  # Include both check-in and check-out days
        self.total_amount = num_days * self.room_type.rate_per_night
        self.save()  # Update the model instance with the calculated total amount

    def calculate_down_payment(self):
        # Calculate the 50% down payment
        self.amount_paid = self.total_amount * 0.5
        self.save()  # Update the model instance with the calculated down payment

class ReservedRoom(models.Model):
  """
  Model to represent the association between a reservation and a specific room.
  """
  reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
  room = models.ForeignKey(Room, on_delete=models.CASCADE)

  date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
  STATUS_CHOICES = (
      ('pending', 'Pending Confirmation'),
      ('confirmed', 'Confirmed'),
      ('cancelled', 'Cancelled'),
  )

  status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')

  class Meta:
    verbose_name = "Reserved Room"
    verbose_name_plural = "Reserved Rooms"

  def __str__(self):
    return f"ReservedRoom: {self.reservation} - Room: {self.room}"
  

class Booking(models.Model):
    """
    Model to represent guest bookings (can include room reservation and order).
    """
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)

    # Room reservation
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    check_in = models.DateField(blank=True, null=True) 
    check_out = models.DateField(blank=True, null=True) 

   
    order = models.OneToOneField(
        'restaurant.Order', on_delete = models.CASCADE, blank=True, null=True, related_name="orders"
    )  

    
    STATUS_CHOICES = (
        ('checked-in', 'Checked In'),
        ('checked-out', 'Checked Out'),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='checked-in')

    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default="0.00") #total amount including additional orders
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default="0.00") #amount paid by guest

    special_requests = models.TextField(blank=True)  # Guest's special requests

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        guest_name = f"{self.guest.firstname} {self.guest.lastname}" if self.guest else "Unknown Guest"
        room_info = f"{self.room.room_number}" if self.room else "No Room Assigned"
        return f"Booking #{self.pk} for {guest_name} (Room: {room_info}) - {self.status}"
    
    