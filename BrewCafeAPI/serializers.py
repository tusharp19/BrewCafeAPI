from rest_framework import serializers
from .models import MenuItem,Cart,OrderItem,Order,Category
from django.contrib.auth.models import User

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=MenuItem
        fields=['id','title','price','category','featured']
        extra_kwargs={
            'price':{'min_value':2}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']

class CartMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=MenuItem
        fields=['id','title','price','category']


class CartSerializer(serializers.ModelSerializer):
    menuitem=CartMenuItemSerializer(read_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(
        source='menuitem', 
        queryset=MenuItem.objects.all(),
        write_only=True
    )
    class Meta:
        model=Cart
        fields=['id','menuitem','menuitem_id','quantity','price']
        read_only_fields=['price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=['menuitem','quantity','unit_price','price']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','slug','title']


class OrderSerializer(serializers.ModelSerializer):
    orderitems=OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    class Meta:
        model=Order
        fields=['id','user','orderitems','delivery_crew','status','total','date']
        read_only_fields=['user','delivery_crew','status','total','date']
