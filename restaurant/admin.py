from django.contrib import admin
from .models import Table, Menu, Order, OrderItem,Staff

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'total_price', 'created_at', 'is_completed', 'status', 'is_paid']
    list_filter = ['created_at', 'is_completed', 'status', 'is_paid']
    search_fields = ['table__table_number']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'is_active']
    fields = ['username', 'password', 'role', 'is_active']
