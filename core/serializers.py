from rest_framework import serializers
from .models import Category, Product, Color, Cart, CartItem, Order, User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'parent']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name_uz', 'name_ru', 'price', 'image']

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    colors = ColorSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name_uz', 'name_ru', 'description_uz', 'description_ru', 'categories', 'image', 'stock', 'colors']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    color = ColorSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'color', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_price', 'status']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_active']