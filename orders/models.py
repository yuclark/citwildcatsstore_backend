# orders/models.py - UPDATED ORDER NUMBER GENERATION
from django.db import models
from django.conf import settings
from products.models import Product
import uuid
import random
from datetime import datetime

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'), 
        ('released', 'Released'),
        ('cancelled', 'Cancelled'),
    )
    
    ORDER_TYPE_CHOICES = (
        ('order', 'Order'),
        ('reservation', 'Reservation'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, blank=True)  # ✅ Make it blank initially
    order_type = models.CharField(max_length=15, choices=ORDER_TYPE_CHOICES, default='reservation')
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.user.full_name}"
    
    def save(self, *args, **kwargs):
        # ✅ IMPROVED ORDER NUMBER GENERATION
        if not self.order_number:
            # Use microseconds and random number for uniqueness
            timestamp = datetime.now().strftime('%m%d%H%M%S%f')[:-3]  # Remove last 3 digits of microseconds
            random_suffix = random.randint(100, 999)
            self.order_number = f"CIT{timestamp}{random_suffix}"
            
            # ✅ ENSURE UNIQUENESS - Keep trying if duplicate exists
            while Order.objects.filter(order_number=self.order_number).exists():
                random_suffix = random.randint(100, 999)
                self.order_number = f"CIT{timestamp}{random_suffix}"
                
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
