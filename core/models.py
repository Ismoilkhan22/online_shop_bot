from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=2, choices=[('uz', 'O‘zbek'), ('ru', 'Русский')], default='uz')

    def __str__(self):
        return f"Profile for {self.user.username}"

class Category(MPTTModel):
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name_uz']

    def __str__(self):
        return self.name_uz

class Color(models.Model):
    name_uz = models.CharField(max_length=50)
    name_ru = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='colors/', null=True, blank=True)

    def __str__(self):
        return f"{self.name_uz} / {self.name_ru}"

class Product(models.Model):
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    colors = models.ManyToManyField(Color, related_name='products')

    def __str__(self):
        return self.name_uz

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name_uz} ({self.color.name_uz})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user}"