from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserInfo, Activity, UcoinRequest, Present, BalanceHistory
from .store_models import ProductItem, Product, Order, Category


# Add to jwt role field
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['role'] = user.userinfo.role

        return token


# Full user info for personal page
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"


# User info in search
class PublicUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ("user_id", "role", "first_name", "last_name", "patronymic")


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['activity_id', 'name']


# Serializer to create new request or request page
class UcoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UcoinRequest
        fields = "__all__"


# Serializer to balance history list
class BalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceHistory
        fields = "__all__"


# Serializer to request list in history
class UcoinRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UcoinRequest
        fields = ("request_id", "state", "created_date")


# Store models Serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# Serializer to create new product
class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


# Serializer to create new product item
class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = "__all__"


# Serializer to create new present item
class PresentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Present
        fields = "__all__"

# class ProductStoreItemSerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField()
#     product_category = serializers.IntegerField()
#     product_name = serializers.CharField(max_length=)
#     product_price = ...
#     product_photo = ...

#
# class CartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cart
#         fields = "__all__"


# Serializer to create new order or order page info
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


# Serializer to order list history
class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "state", "created_date", "products_list")


# Custom Serializers
class CustomOrdersSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    user_name = serializers.CharField()
    user_id = serializers.IntegerField()
    product_list = serializers.CharField()
    office_address = serializers.CharField(max_length=2)


class CustomUcoinsRequestsSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    activity_id = serializers.IntegerField()
    user_name = serializers.CharField()
    activity_name = serializers.CharField()
    comment = serializers.CharField(max_length=250)
