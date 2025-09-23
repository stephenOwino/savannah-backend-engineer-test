from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models, transaction


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def has_sufficient_stock(self, quantity):
        """Checks if there is enough stock for a given quantity."""
        return self.stock >= quantity


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.username}"

    @transaction.atomic
    def update_total_amount(self):
        """Calculates and saves the total amount from all its order items using Decimal."""
        total = sum(
            (item.subtotal for item in self.orderitem_set.all()), Decimal("0.00")
        )
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "product")

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    @property
    def subtotal(self):
        """Calculates the subtotal for this line item."""
        return self.product.price * self.quantity
