from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# Create your views here.
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Count, Sum, Case, When


def dashboard(request):
    
    top_selling_items = OrderItem.objects.values('menu_item__name', 'menu_item__price', 'menu_item__images').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    
    for item in top_selling_items:
        item['revenue'] = item['total_quantity'] * item['menu_item__price']

    
    context = {'top_selling_items': top_selling_items}
    return render(request, 'restaurant/dashboard.html', context)

def menu(request):
    menu_items = MenuItem.objects.all()
    categories = menu_items.values_list('category', flat=True).distinct()  
    today_special = menu_items.filter(today_special=True).get()
    print(today_special.name)

    context = {
        'menu_items': menu_items,
        'categories': categories,
        'today_special': today_special  
    }
    return render(request, 'restaurant/menu.html', context)

def add_new_menu(request):
  if request.method == 'POST':
       name = request.POST.get('name')
       price = request.POST.get('price')
       category = request.POST.get('category')
       description = request.POST.get('description')
       serving = request.POST.get('serving')
       images = request.FILES.get('images')
       new_item = MenuItem(name=name, price=price, description=description, category = category, serves = serving, images=images)
       new_item.save()

  messages.success(request, f'{name} successfully added to the Menu!')
  return redirect('restaurant:menu')


def ordered_items(request):
   items = OrderItem.objects.all()
   context = {
       'items': items
   }
   return render(request, 'restaurant/ordered_items.html', context)


def orders(request):
    orders_list = Order.objects.select_related('booking__guest').prefetch_related('items').all()

    bookings = Booking.objects.all()
    orders = Order.objects.all()
    menu_items = MenuItem.objects.all()
    order_items = OrderItem.objects.all()
    context = {
        'bookings': bookings,
        'orders': orders,
        'menu_items': menu_items,
        'order_items': order_items,
        'orders_list': orders_list,
    }
    return render(request, 'restaurant/orders.html', context)

def generate_invoice(request, pk):
    orders_list = Order.objects.get(id = pk)
    context = {
       'order': orders_list,
       'order_list': orders_list.items.all()
    }

    return render(request, 'home/test_invoice.html', context)



def items_for_room(request, room_id):

  booking = get_object_or_404(Booking, pk=room_id)


  if not booking or not booking.order:
    return JsonResponse([], safe=False)

  # Get available items from the associated order
  available_items = booking.order.items.all()

  # Prepare the response data as a list of dictionaries
  item_data = []
  for item in available_items:
    item_data.append({
      'id': item.id,
      'name': item.menu_item.name,
      'quantity': item.quantity,
      'total_cost': item.total_cost,

    })

  return JsonResponse(item_data, safe=False)

def menu_items_list(request):

    menu_items = MenuItem.objects.all()


  # Prepare the response data as a list of dictionaries
    item_data = []
    for item in menu_items:
        item_data.append({
        'id': item.id,
        'price': item.price,
        'name': item.name,
        'formatted_price': f"₱{item.price:.2f}"
        })

    return JsonResponse(item_data, safe=False)

def add_item_to_booking2(request, booking_id, item_id):
    """
    Function-based view to add a new item to a booking's order.

    Args:
        request: The Django HTTP request object.
        booking_id: The ID of the booking to add the item to.
        item_id: The ID of the item to be added.

    Returns:
        A JsonResponse with the status of the operation (success or error message).
    """

    # Retrieve the Booking object
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'})

    # Retrieve the MenuItem object
    try:
        item = MenuItem.objects.get(pk=item_id)
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'})

    # Check if the booking has an associated order (optional)
    if not booking.order:
        # Create a new order for the booking
        order = Order.objects.create(booking=booking)

    # Add the item to the booking's order (or create a new order if necessary)
    order, created = OrderItem.objects.get_or_create( menu_item=item)

    # Handle potential creation errors (e.g., unique constraint violation)
    if not created:
        return JsonResponse({'error': 'Item already exists in this order'})

    # Return a success response with more details
    return JsonResponse({
        'message': 'Item added successfully',
        'item': {
            'id': item.id,
            'name': item.name,
            'price': item.price,  # Include item price (assuming a price field in MenuItem)
            'booking': {  # Include booking details (optional)
                'id': booking.id,
                'guest_name': booking.guest.firstname + ' ' + booking.guest.lastname  # Assuming guest first and last name fields
            }
        }
    })

def add_item_to_booking(request, booking_id, item_id):
    """
    Function-based view to add a new item to a booking's order.

    Args:
        request: The Django HTTP request object.
        booking_id: The ID of the booking to add the item to.
        item_id: The ID of the item to be added.

    Returns:
        A JsonResponse with the status of the operation (success or error message).
    """

    # Retrieve the Booking and MenuItem objects
    try:
        booking = Booking.objects.get(pk=booking_id, status = 'checked-in')
        
        item = MenuItem.objects.get(pk=item_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'})
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'})

    # Check if the booking has an associated order
    if not booking.order:
        order = Order.objects.create(booking=booking)

    # Update existing OrderItem or create a new one if necessary
    try:
        order_item, created = OrderItem.objects.get_or_create(
            menu_item=item, order=booking.order
        )
    except IntegrityError:  # Handle potential unique constraint violation
        return JsonResponse({'error': 'Item already exists in this order'})

    # Handle existing item with quantity 0 (update quantity)
    if not created and order_item.quantity == 0:
        order_item.quantity = int(request.POST.get('quantity'))
        order_item.save()
        return JsonResponse({
            'message': 'Item quantity updated successfully',
            'item': {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'booking': {
                    'id': booking.id,
                    'guest_name': booking.guest.firstname + ' ' + booking.guest.lastname
                }
            }
        })

    # New item or updated quantity (created is True)
    order_item.save()  # Save the updated OrderItem object
    return JsonResponse({
        'message': 'Item added successfully' if created else 'Item quantity increased',
        'item': {
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'booking': {
                'id': booking.id,
                'guest_name': booking.guest.firstname + ' ' + booking.guest.lastname
            }
        }
    })

def add_new_item(request):
    if request.method == 'POST':
        menu_id = request.POST.get('menu')
        quantity = request.POST.get('quantity')
       # new_item = MenuItem(name=name, price=price, description=description)
       # new_item.save()
      #  return redirect('menu')
    else:
        return render(request, 'restaurant/add_new_item.html')
    
def create_order_item_ajax2(request):
  if request.method == 'POST':
    menu_item_id = request.POST.get('menu_item')
    quantity = request.POST.get('quantity')
    print(menu_item_id)

    try:
      menu_item = MenuItem.objects.get(id=menu_item_id)
    except MenuItem.DoesNotExist:
      return JsonResponse({'error': 'Invalid menu item.'}, status=400)

    try:
      quantity = int(quantity)
      if quantity <= 0:
        raise ValueError
    except ValueError:
      return JsonResponse({'error': 'Invalid quantity. Please enter a positive integer.'}, status=400)

    order_item = OrderItem.objects.create(
      menu_item=menu_item,
      quantity=quantity,
    )

    # Calculate total cost based on your logic (consider discounts, etc.)
    order_item.total_cost = order_item.calculate_total_cost()  # Use the model method
    order_item.save()

    return JsonResponse({'success': True, 'order_item': str(order_item)})

  return JsonResponse({'error': 'Method not allowed (POST required).'}, status=405)


def create_order_item_ajax(request):
  if request.method == 'POST':
    menu_item_id = request.POST.get('menu_item')
    quantity = request.POST.get('quantity')

    booking_id = request.POST.get('room_id')  

    print(booking_id)# New field for booking ID

    print(menu_item_id, quantity, booking_id)

    try:
      menu_item = MenuItem.objects.get(id=menu_item_id)
    except MenuItem.DoesNotExist:
      return JsonResponse({'error': 'Invalid menu item.'}, status=400)

    try:
      quantity = int(quantity)
      if quantity <= 0:
        raise ValueError
    except ValueError:
      return JsonResponse({'error': 'Invalid quantity. Please enter a positive integer.'}, status=400)

    try:
      # Try to find an existing order for the booking
      booking = Booking.objects.get(id=booking_id)
      existing_order = booking.order

     
      if existing_order:
        order_item = OrderItem.objects.create(
            order = booking.order,
            menu_item=menu_item,
            quantity=quantity,
        )
        existing_order.items.add(order_item)
        existing_order.save() 

      
      else:
        order = Order.objects.create(booking=booking)
        order_item = OrderItem.objects.create(
            order=order,  
            menu_item=menu_item,
            quantity=quantity,
        )
        order.items.add(order_item)
        order.save() 
        booking.order = order  
        booking.save()

      return JsonResponse({'success': True, 'order_item': str(order_item)})

    except ObjectDoesNotExist:
      return JsonResponse({'error': 'Invalid booking ID.'}, status=400)

  return JsonResponse({'error': 'Method not allowed (test required).'}, status=405)


def prepare_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.status = 'preparing'
    order_item.save()
    messages.success(request, f"Order item marked as preparing.")
    return redirect('restaurant:ordered-items')

def complete_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Mark the order item as prepared
    order_item.status = 'prepared'
    messages.success(request, f"Order item marked as prepared.")
    order_item.save()

    # Update order status if all order items are prepared
    order = order_item.order
    all_items_prepared = all(item.status == 'prepared' for item in order.items.all())
    if all_items_prepared:
        order.status = 'prepared'
        order.save()
        messages.success(request, f"Order #{order.pk} marked as prepared!")
    else:
        messages.info(request, f"Order item marked as prepared. Update order status when all items are prepared.")

    return redirect('restaurant:ordered-items')

def complete_order_delivered(request, order_id):
   order = Order.objects.get(id = order_id)
   order.status = 'delivered'
   order.save()
   messages.success(request, f"Order {order} Delivered!")

   return redirect('restaurant:orders')

