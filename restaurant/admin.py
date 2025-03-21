from django.contrib import admin
from .models import Table, Menu, Order, OrderItem,Staff
from django.utils.safestring import mark_safe

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description', 'image_preview']  # Add 'image_preview' to display in the list view
    readonly_fields = ['image_preview']  # Add this to display the image preview in the admin panel

    def image_preview(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" width="150" height="150" />')
        return "No Image"

    image_preview.short_description = 'Image Preview'

    def image_preview(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" width="150" height="150" />')
        return "No Image"

    image_preview.short_description = 'Image Preview'

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="150" />')
        return "No Image"

    image_preview.short_description = 'Image Preview'

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
