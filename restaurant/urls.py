from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),    # Root URL
    path('about/', views.about, name='about'),  # Add this line for the about view
    path('menu/<int:table_id>/', views.menu, name='menu'),
    path('order-submitted/', views.order_submitted, name='order_submitted'),
    path('kitchen/', views.kitchen, name='kitchen'),
    path('get_orders/', views.get_orders, name='get_orders'),
    path('accept_order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('reject_order/<int:order_id>/', views.reject_order, name='reject_order'),
    path('checkout/', views.checkout, name='checkout'),  # Add this line for the checkout view
    path('payment/', views.payment, name='payment'),
    path('mark_completed/<int:order_id>/', views.mark_completed, name='mark_completed'),
    path('get_order_status/<int:order_id>/', views.get_order_status, name='get_order_status'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('staff_login/', views.staff_login, name='staff_login'), 
    path('staff_logout/', views.staff_logout, name='staff_logout'),
    path('stocks/', views.stocks, name='stocks'),  # New URL for stocks management
    path('toggle_stock/<int:item_id>/', views.toggle_stock, name='toggle_stock'),
    path('generate_qr/', views.generate_qr_code, name='generate_qr'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('notify_kitchen/', views.notify_kitchen, name='notify_kitchen'),
    path('process_upi_payment/', views.process_upi_payment, name='process_upi_payment'),
    path('mark_notification_complete/<int:notification_id>/', views.mark_notification_complete, name='mark_notification_complete'),
    path('check_payment_status/<int:order_id>/', views.check_payment_status, name='check_payment_status'),
    path('complete_payment/<int:order_id>/', views.complete_payment, name='complete_payment'),
    path('foodbot/<int:table_id>/', views.food_bot, name='food_bot'),
]
