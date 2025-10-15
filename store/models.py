from django.db import models
from django.contrib.auth.models import User

# Pesticide Model
class Pesticide(models.Model):
    pest_name = models.CharField(max_length=100)
    pesticide_name = models.CharField(max_length=200)
    usage_instruction = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    image = models.ImageField(upload_to="pesticides/", null=True, blank=True)

    def __str__(self):
        return f"{self.pest_name} - {self.pesticide_name}"

# Cart Model (for logged-in users)
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pesticide = models.ForeignKey(Pesticide, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.pesticide.price

    def __str__(self):
        return f"{self.user.username} - {self.pesticide.pesticide_name} (x{self.quantity})"

# Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pesticide = models.ForeignKey(Pesticide, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15)  # <-- Add this
    pincode = models.CharField(max_length=10)  # <-- Add this
    address = models.TextField()  # <-- Add this
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Shipped", "Shipped"), ("Delivered", "Delivered")],
        default="Pending",
    )

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

# Optional: Order Confirmation model (if used separately from Order)
class OrderConfirmation(models.Model):
    item = models.CharField(max_length=100)
    pest_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, default='Confirmed')

    def __str__(self):
        return f"{self.item} - {self.pest_name}"

# Optional: OrderItem Model (if you want multiple pesticides per order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pesticide = models.ForeignKey(Pesticide, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.pesticide.pesticide_name} - {self.quantity}"

# Optional: Session-based CartItem (for guest users, if needed)
class CartItem(models.Model):
    product = models.ForeignKey(Pesticide, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    session_key = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.pesticide_name} ({self.quantity})"
