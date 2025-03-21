from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import JsonResponse,HttpResponseForbidden
from restaurant.models import Table, Menu, Order, OrderItem,Staff
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test


def home(request):
    return render(request, 'restaurant/home.html')

def about(request):
    """
    Renders the about page.
    """
    return render(request, 'about.html')

def view_cart(request):
    cart = request.session.get('cart', {})
    menu_items = Menu.objects.filter(id__in=cart.keys())
    cart_items = []
    for item in menu_items:
        cart_items.append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'quantity': cart[str(item.id)],
            'total': item.price * cart[str(item.id)]
        })

    # Retrieve the table_id from the session or request
    table_id = request.session.get('table_id')  # Ensure table_id is stored in the session
    if not table_id:
        return redirect('home')  # Redirect to home if no table_id is found

    return render(request, 'restaurant/view_cart.html', {'cart_items': cart_items, 'table_id': table_id})


@csrf_exempt
def payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            upi_id = data.get('upi_id')
            order_id = request.session.get('latest_order_id')

            if not upi_id or not order_id:
                return JsonResponse({'status': 'error', 'message': 'Missing UPI ID or order ID'}, status=400)

            # Simulate UPI ID validation
            if not upi_id.endswith('@upi'):
                return JsonResponse({'status': 'error', 'message': 'Invalid UPI ID'}, status=400)

            # Update order status to 'pending' (send to kitchen)
            order = Order.objects.get(id=order_id)
            order.status = 'pending'  # Now the order is sent to the kitchen
            order.save()

            return JsonResponse({'status': 'success', 'redirect_url': '/order-submitted/'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return render(request, 'restaurant/payment.html')

def order_submitted(request):
    # Retrieve the latest order ID from the session
    order_id = request.session.get('latest_order_id')
    if not order_id:
        return redirect('home')  # Redirect if no order ID is found

    # Retrieve the order and its associated table
    order = Order.objects.get(id=order_id)
    table_id = order.table.id  # Get the table ID from the order

    # Pass the order ID and table ID to the template
    return render(request, 'restaurant/order_submitted.html', {'order': {'id': order_id, 'table_id': table_id}})

    # Pass the order ID to the template
    return render(request, 'restaurant/order_submitted.html', {'order': {'id': order_id}})

def menu(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    menu_items = Menu.objects.all()
    request.session['table_id'] = table_id
    return render(request, 'restaurant/menu.html', {'table': table, 'menu_items': menu_items})

def kitchen(request):
    # Fetch pending orders
    pending_orders = Order.objects.filter(status='pending').prefetch_related('items')
    return render(request, 'restaurant/kitchen.html', {'orders': pending_orders})

@csrf_exempt
def mark_completed(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.is_completed = True
        order.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def accept_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.status = 'accepted'
        order.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def reject_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.status = 'rejected'
        order.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_id = data.get('table_number')
            items = data.get('items', [])

            if not table_id or not items:
                return JsonResponse({'status': 'error', 'message': 'Missing table number or items'}, status=400)

            table = Table.objects.get(id=table_id)
            order = Order.objects.create(table=table, total_price=0, status='created')  # Status is 'created', not 'pending'

            total_price = 0
            for item in items:
                menu_item = Menu.objects.get(id=item['item_id'])
                quantity = item.get('quantity', 0)
                if quantity <= 0:
                    return JsonResponse({'status': 'error', 'message': 'Invalid quantity'}, status=400)
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
                total_price += menu_item.price * quantity

            order.total_price = total_price
            order.save()

            # Store the order ID in the session for the payment page
            request.session['latest_order_id'] = order.id

            return JsonResponse({'status': 'success', 'redirect_url': '/payment/'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON data: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_orders(request):
    if request.method == 'GET':
        orders = Order.objects.filter(is_completed=False, status='pending')
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'table_number': order.table.table_number,
                'total_price': float(order.total_price),
                'items': [{'name': item.menu_item.name, 'quantity': item.quantity} for item in order.items.all()],
            })
        return JsonResponse({'orders': orders_data})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# New view to fetch the status of a specific order
@csrf_exempt
def get_order_status(request, order_id):
    if request.method == 'GET':
        try:
            order = Order.objects.get(id=order_id)
            return JsonResponse({'status': order.status})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', {})
            request.session['cart'] = cart  # Save the cart in the session
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            cart = request.session.get('cart', {})

            if str(item_id) in cart:
                del cart[str(item_id)]
                request.session['cart'] = cart
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            staff = Staff.objects.get(username=username, password=password, is_active=True)
            request.session['staff_id'] = staff.id  # Store staff ID in session
            return redirect('kitchen')
        except Staff.DoesNotExist:
            return render(request, 'restaurant/login.html', {'error_message': 'Invalid username or password.'})
    return render(request, 'restaurant/login.html')

def staff_logout(request):
    if 'staff_id' in request.session:
        del request.session['staff_id']  # Remove staff ID from session
    return redirect('staff_login')

def is_staff_authenticated(request):
    return 'staff_id' in request.session

def kitchen(request):
    if not is_staff_authenticated(request):
        return redirect('staff_login')  # Redirect to login page if not authenticated
    # Fetch pending orders
    pending_orders = Order.objects.filter(status='pending').prefetch_related('items')
    return render(request, 'restaurant/kitchen.html', {'orders': pending_orders})


@csrf_exempt
def toggle_stock(request, item_id):
    if request.method == 'POST':
        try:
            item = Menu.objects.get(id=item_id)
            item.is_in_stock = not item.is_in_stock  # Toggle stock status
            item.save()
            return JsonResponse({'status': 'success', 'is_in_stock': item.is_in_stock})
        except Menu.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Menu item not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def stocks(request):
    if not request.user.is_staff:  # Ensure the user is a staff member
        return redirect('staff_login')  # Redirect to the staff login page if not authenticated

    menu_items = Menu.objects.all()
    return render(request, 'restaurant/stocks.html', {'menu_items': menu_items})
