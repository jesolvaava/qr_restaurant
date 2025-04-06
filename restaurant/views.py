from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import JsonResponse,HttpResponseForbidden
from restaurant.models import Table, Menu, Order, OrderItem,Staff,Notification
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
import io,re
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import base64
import requests


def home(request):
    return render(request, 'restaurant/home.html')

def about(request):
    return render(request, 'restaurant/about.html')

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
            # Just mark the order as paid without any real processing
            order_id = request.session.get('latest_order_id')
            if not order_id:
                return JsonResponse({'status': 'error', 'message': 'No active order'}, status=400)

            order = Order.objects.get(id=order_id)
            order.is_paid = True
            order.status = 'accepted'
            order.payment_method = request.POST.get('payment_method', 'dummy')
            order.save()

            return JsonResponse({
                'status': 'success', 
                'redirect_url': '/order-submitted/'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # GET request - render payment page
    order_id = request.session.get('latest_order_id')
    if not order_id:
        return redirect('home')
        
    order = Order.objects.get(id=order_id)
    return render(request, 'restaurant/payment.html', {
        'total_amount': order.total_price,
        'order': order
    })


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

            # Verify all items are in stock (frontend should prevent this, but we double-check)
            for item in items:
                menu_item = Menu.objects.get(id=item['item_id'])
                if not menu_item.is_in_stock:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Some items in your cart are no longer available. Please refresh your menu.'
                    }, status=400)

            # Rest of your checkout logic...
            table = Table.objects.get(id=table_id)
            order = Order.objects.create(
                table=table,
                status='pending',
                payment_method=None
            )

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

            request.session['latest_order_id'] = order.id
            return JsonResponse({'status': 'success', 'redirect_url': '/payment/'})
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
            # First try Django's authentication
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                request.session['staff_authenticated'] = True
                return redirect('kitchen')
            
            # Fall back to custom Staff model if Django auth fails
            staff = Staff.objects.get(username=username, password=password, is_active=True)
            request.session['staff_id'] = staff.id
            request.session['staff_authenticated'] = True
            return redirect('kitchen')
            
        except Staff.DoesNotExist:
            return render(request, 'restaurant/login.html', {
                'error_message': 'Invalid credentials or not authorized'
            })
    
    return render(request, 'restaurant/login.html')

def staff_logout(request):
    if 'staff_id' in request.session:
        del request.session['staff_id']  # Remove staff ID from session
    return redirect('staff_login')

def is_staff_authenticated(request):
    return 'staff_id' in request.session

def kitchen(request):
    if not is_staff_authenticated(request):
        return redirect('staff_login')
    
    # Fetch pending orders
    pending_orders = Order.objects.filter(status='pending').prefetch_related('items')
    
    # Fetch payment notifications (last 10)
    payment_notifications = Notification.objects.filter(
        notification_type='payment'
    ).order_by('-created_at')[:10]
    
    return render(request, 'restaurant/kitchen.html', {
        'orders': pending_orders,
        'notifications': payment_notifications
    })


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




@require_http_methods(["GET"])
def generate_qr_code(request):
    # Get order details
    order_id = request.session.get('latest_order_id')
    if not order_id:
        return HttpResponseForbidden("No active order")
    
    order = get_object_or_404(Order, id=order_id)
    
    # Create UPI payment link
    upi_id = "jesol@fam"  # Replace with your actual UPI ID
    amount = str(order.total_price)
    note = f"Payment for Order #{order_id}"
    
    upi_link = f"upi://pay?pa={upi_id}&am={amount}&tn={note}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_link)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return JsonResponse({
        'qr_code': qr_code,
        'amount': amount,
        'upi_id': upi_id
    })

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        try:
            order_id = request.session.get('latest_order_id')
            if not order_id:
                return JsonResponse({'status': 'error', 'message': 'No active order'}, status=400)
            
            order = Order.objects.get(id=order_id)
            
            # In a real app, you would verify with payment gateway
            # For demo, we'll just check if payment_method is set
            if order.payment_method:
                order.is_paid = True
                order.status = 'accepted'
                order.save()
                
                return JsonResponse({
                    'status': 'success',
                    'redirect_url': '/order-submitted/'
                })
            else:
                return JsonResponse({
                    'status': 'pending',
                    'message': 'Payment not yet completed'
                })
                
        except Order.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Order not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)



@csrf_exempt
def notify_kitchen(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method')
            table_number = data.get('table_number')
            order_id = data.get('order_id')
            amount = data.get('amount')
            
            if not all([payment_method, table_number, order_id, amount]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)
            
            try:
                order = Order.objects.get(id=order_id)
                
                # Create notification with all required fields
                notification = Notification.objects.create(
                    notification_type='payment',
                    payment_method=payment_method,
                    table_number=table_number,
                    amount=amount,
                    message=f"{payment_method.capitalize()} payment requested for Table {table_number}",
                    order=order
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Kitchen notified about {payment_method} payment',
                    'notification_id': notification.id
                })
                
            except Order.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Order not found'
                }, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


@csrf_exempt
def process_upi_payment(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            upi_id = data.get('upi_id')
            order_id = data.get('order_id')
            table_number = data.get('table_number')
            amount = data.get('amount')

            # Validate required fields
            if not all([upi_id, order_id, table_number, amount]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)

            # Validate UPI ID format
            if not re.match(r'^[\w.-]+@[\w]+$', upi_id):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid UPI ID format (e.g., name@upi)'
                }, status=400)

            try:
                # Get the order
                order = Order.objects.get(id=order_id)
                
                # In a real implementation, you would:
                # 1. Call UPI payment gateway API here
                # 2. Process the payment request
                # For demo purposes, we'll simulate success after 2 seconds
                
                # Create notification for kitchen
                Notification.objects.create(
                    notification_type='payment',
                    payment_method='upi',
                    table_number=table_number,
                    amount=amount,
                    message=f"UPI payment request for ₹{amount} to {upi_id}",
                    order=order
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment request sent to UPI app'
                })

            except Order.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Order not found'
                }, status=404)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


@csrf_exempt
def mark_notification_complete(request, notification_id):
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id)
            order = notification.order
            
            # Mark order as paid
            order.is_paid = True
            order.payment_method = notification.payment_method
            order.save()
            
            notification.delete()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def check_payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return JsonResponse({
            'status': 'completed' if order.is_paid else 'pending'
        })
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@csrf_exempt
def complete_payment(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.is_paid = True
            order.payment_method = request.POST.get('payment_method', 'cash/card')
            order.save()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)


def food_search(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'No query'}, status=400)
    
    # Get ingredients and nutrition
    response = requests.get(
        'https://api.edamam.com/api/food-database/v2/parser',
        params={
            'app_id': 'YOUR_APP_ID',  # Register at Edamam
            'app_key': 'YOUR_APP_KEY',
            'ingr': query,
            'nutrition-type': 'logging'
        }
    )
    
    data = response.json()
    return JsonResponse({
        'ingredients': data['parsed'][0]['food']['foodContentsLabel'],
        'calories': data['parsed'][0]['food']['nutrients']['ENERC_KCAL']
    })




def food_bot(request, table_id):
    return render(request, 'restaurant/foodbot.html', {'table_id': table_id})
