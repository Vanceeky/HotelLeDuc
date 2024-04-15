from django.db import models
from booking.models import Guest, Room, Booking

# Create your models here.

class MenuItem(models.Model):
    """
    Model to represent menu items (food and drinks) offered by the restaurant.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=(('food', 'Food'), ('drink', 'Drink')))

    # Optional field to indicate suggested serving size
    serves = models.PositiveIntegerField(blank=True, null=True)
    images = models.ImageField(upload_to='menu_images/', blank=True)
    today_special = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return f"{self.category} - {self.name} (Order: {self.price})"
    


""" class OrderItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Track quantity of each item per order
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('prepared', 'Prepared'),
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')

    def calculate_total_cost(self):
       #Calculates the total cost of the ordered item (quantity * price).
        if self.menu_item.price is not None:
            total_cost = self.quantity * self.menu_item.price
            return total_cost
        else:
            return None  # Return None if menu_item_price is not set

    def __str__(self):
        total_cost = self.calculate_total_cost()  # Call the calculate_total_cost function
        if total_cost is not None:
            return f"{self.quantity} - {self.menu_item.name} (₱{self.menu_item.price}) - Total Cost: ₱{total_cost} - Order: {self.status}"
        else:
            return f"{self.quantity} - {self.menu_item.name} (Price not available) - Order: {self.status}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items" """

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='orderded_items', null = True, blank=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Track quantity of each item per order
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('prepared', 'Prepared'),
        ('delivered', 'Delivered'),
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    placed_at = models.DateTimeField(auto_now_add=True, null = True, blank = True)  # Automatically record order placement time
    def save(self, *args, **kwargs):
        """
        Override save method to calculate total_cost before saving the OrderItem.
        """
        if self.menu_item.price is not None:
            self.total_cost = self.quantity * self.menu_item.price
        else:
            self.total_cost = 0.00
        super().save(*args, **kwargs)  # Call the original save method
    def calculate_total_cost(self):
        total = self.quantity * self.menu_item.price
        return total
    
    def __str__(self):
        total_cost = self.total_cost  # Use the calculated total_cost field
        if total_cost is not None:
            return f"{self.quantity} - {self.menu_item.name} (₱{self.menu_item.price}) - Total Cost: ₱{total_cost} - Order: {self.status}"
        else:
            return f"{self.quantity} - {self.menu_item.name} (Price not available) - Order: {self.status}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
    
class Order(models.Model):
    #guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    #room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null = True, blank = True, related_name="booking")  # Link order to the guest's room
    placed_at = models.DateTimeField(auto_now_add=True)  # Automatically record order placement time
    # Order status (e.g., pending, preparing, delivered)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('prepared', 'Prepared'),
        ('delivered', 'Delivered'),
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    # Many-to-many relationship with OrderItem
    items = models.ManyToManyField(OrderItem, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_total_price(self):
        """Calculates the total price of all OrderItems in this order."""
        total = sum(item.total_cost for item in self.items.all())
        return total

    def __str__(self):
        total_price = self.get_total_price()
        self.total_price = total_price  # Assign the calculated total before returning
        self.save()  # Save the Order model with the updated total_price
        return f"Order #{self.pk} for {self.booking.guest.firstname}, {self.booking.guest.lastname}, (Room: {self.booking.room.room_number}) - {self.placed_at} - {self.status} - Total Price: ₱{total_price}"
    
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
