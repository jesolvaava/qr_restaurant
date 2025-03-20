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
]