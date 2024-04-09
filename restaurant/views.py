from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# Create your views here.


def dashboard(request):
    return render(request, 'restaurant/dashboard.html')

def menu(request):
    return render(request, 'restaurant/menu.html')

def orders(request):
    bookings = Booking.objects.all()
    orders = Order.objects.all()
    menu_items = MenuItem.objects.all()
    order_items = OrderItem.objects.all()
    context = {
        'bookings': bookings,
        'orders': orders,
        'menu_items': menu_items,
        'order_items': order_items
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
        })

    return JsonResponse(item_data, safe=False)

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


def add_new_item(request):
    if request.method == 'POST':
        menu_id = request.POST.get('menu')
        quantity = request.POST.get('quantity')
       # new_item = MenuItem(name=name, price=price, description=description)
       # new_item.save()
      #  return redirect('menu')
    else:
        return render(request, 'restaurant/add_new_item.html')