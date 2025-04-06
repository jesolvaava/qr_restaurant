# restaurant/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.urls import reverse

class Table(models.Model):
    table_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Table {self.table_number}"

class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(
        upload_to='menu_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Upload food image (JPEG, PNG, WEBP)"
    )
    is_in_stock = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ${self.price}"

    @property
    def image_url(self):
        """
        Returns the image URL with fallback to default image
        Works in both development and production environments
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default_food.jpg'

    def get_absolute_url(self):
        return reverse('menu_item_detail', kwargs={'pk': self.pk})

class Order(models.Model):
    table = models.ForeignKey('Table', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    is_paid = models.BooleanField(default=False)
    
    # Simple payment method field (optional)
    payment_method = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

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
    

    # 
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('payment', 'Payment'),
        ('order', 'Order'),
        ('alert', 'Alert')
    ]
    
    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('cash', 'Cash'),
        ('card', 'Card')
    ]
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True, null=True)
    table_number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.get_notification_type_display()} for Table {self.table_number}"
