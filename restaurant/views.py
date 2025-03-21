from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from restaurant.models import Table, Menu, Order, OrderItem, Staff
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    return render(request, 'restaurant/home.html')

def about(request):
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

    table_id = request.session.get('table_id')
    if not table_id:
        return redirect('home')

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

            if not upi_id.endswith('@upi'):
                return JsonResponse({'status': 'error', 'message': 'Invalid UPI ID'}, status=400)

            order = Order.objects.get(id=order_id)
            order.status = 'pending'
            order.save()

            return JsonResponse({'status': 'success', 'redirect_url': '/order-submitted/'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return render(request, 'restaurant/payment.html')

def order_submitted(request):
    order_id = request.session.get('latest_order_id')
    if not order_id:
        return redirect('home')

    order = Order.objects.get(id=order_id)
    table_id = order.table.id

    return render(request, 'restaurant/order_submitted.html', {'order': {'id': order_id, 'table_id': table_id}})

def menu(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    menu_items = Menu.objects.all()
    request.session['table_id'] = table_id
    return render(request, 'restaurant/menu.html', {'table': table, 'menu_items': menu_items})

# Other views remain unchanged...
