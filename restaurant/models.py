# restaurant/models.py
from django.db import models
from django.utils import timezone

class Table(models.Model):
    table_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Table {self.table_number}"


class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.CharField(max_length=500, blank=True, null=True)  # Store the image URL
    is_in_stock = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    table = models.ForeignKey('Table', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} for Table {self.table.table_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
    
class Staff(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # Store hashed passwords in production
    role = models.CharField(max_length=100, blank=True, null=True)  # Make role optional
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
