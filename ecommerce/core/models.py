from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):

    user = models.OneToOneField(User,null=False,blank=False,on_delete = models.CASCADE)

    #extra fields will come here
    phone_field = models.CharField(max_length=12,blank=False)

    def __str__(self) -> str:
        return self.user.username

# Category Model where different Categories will be stored
class Category(models.Model):
    category_name = models.CharField(max_length=200)
    def __str__(self):
        return self.category_name


class Product(models.Model):
    name=models.CharField(max_length=100)
    category = models.ManyToManyField(Category)
    desc=models.TextField()
    price=models.FloatField(default=0.0)
    product_available_count=models.IntegerField(default=0)
    img=models.ImageField(upload_to='images/')

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            "pk" : self.pk
        })

    def __str__(self) -> str:
        return self.name

from django.contrib.auth.models import User

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # shipping address — inline fields are fine unless you want a reusable Address model
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)   # snapshot — survives if product is later edited/deleted
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot of price at purchase time
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity
