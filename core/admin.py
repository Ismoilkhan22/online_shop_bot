from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Product, Cart, CartItem, Order, Color

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Color)