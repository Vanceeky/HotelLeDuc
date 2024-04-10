from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# Create your views here.
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

def dashboard(request):
    return render(request, 'restaurant/dashboard.html')

def menu(request):
    menu_items = MenuItem.objects.all()
    categories = menu_items.values_list('category', flat=True).distinct()  # Get distinct categories
    context = {
        'menu_items': menu_items,
        'categories': categories,  # Add categories to context
    }
    return render(request, 'restaurant/menu.html', context)

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
        booking = Booking.objects.get(pk=booking_id)
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

      # If order exists, add the new OrderItem
      if existing_order:
        order_item = OrderItem.objects.create(
            menu_item=menu_item,
            quantity=quantity,
        )
        existing_order.items.add(order_item)
        existing_order.save()  # Recalculate total price on save

      # If no order exists, create a new order and link it to the booking
      else:
        order = Order.objects.create(booking=booking)
        order_item = OrderItem.objects.create(
            order=order,  # Link to the newly created order
            menu_item=menu_item,
            quantity=quantity,
        )
        order.items.add(order_item)
        order.save()  # Recalculate total price on save
        booking.order = order  # Link order to the booking
        booking.save()

      return JsonResponse({'success': True, 'order_item': str(order_item)})

    except ObjectDoesNotExist:
      return JsonResponse({'error': 'Invalid booking ID.'}, status=400)

  return JsonResponse({'error': 'Method not allowed (test required).'}, status=405)