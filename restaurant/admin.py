from django.contrib import admin

# Register your models here.
from .models import MenuItem, OrderItem, Order

# Register your models here.

class MenuItemAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'category', 'price')
  search_fields = ('name', 'description')

admin.site.register(MenuItem, MenuItemAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'quantity', 'placed_at', 'status', 'total_cost')  # Add 'calculate_total_cost'
    #readonly_fields = ('calculate_total_cost',)  # Display 'calculate_total_cost' as read-only

    def calculate_total_cost(self, obj):
        """
        This method is called by the admin to calculate the total cost for each OrderItem.
        It's not part of the OrderItem model itself, but used within the admin class.
        """
        if obj.menu_item.price is not None:
            total_cost = obj.quantity * obj.menu_item.price
            return total_cost
        else:
            return None

admin.site.register(OrderItem, OrderItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('booking', 'placed_at', 'status', 'total_price')  # Add 'calculate_total_price'
  


admin.site.register(Order, OrderAdmin)