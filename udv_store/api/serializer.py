from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserInfo, Activity, UcoinRequest, Present, BalanceHistory, Customer
from .store_models import ProductItem, Product, Order, Cart


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


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


# User info in search
class PublicUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ("user_id", "role", "first_name", "last_name", "patronymic")


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['activity_id', 'ucoins_count', 'name']


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


# # Store models Serializers
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = "__all__"


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


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ("id", "product_item_id")


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


class RequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UcoinRequest
        fields = ("request_id", "created_date", "state", "activity_ucoins_count")


class RequestListFullDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UcoinRequest
        fields = "request_id", "comment", "created_date", "user_id", \
                 "user_full_name", "activity_id", "activity_name"


# Present info to generate present in frontend
class PresentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Present
        fields = ("id", "user_from", "sender_full_name", "text", "sign",
                  "ucoin_count", "background", "state")


# Product info to store
class ProductInStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("product_id", "name", "price", "items_list")


# Product info to admin panel
class ProductInAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("product_id", "name", "photo_path", "state",
                  "description", "price", "item_count")


class ProductInProductPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("product_id", "name", "price", "description",
                  "have_size", "product_items_and_sizes")


class CustomerCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["cart_items"]


class ProductItemInAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("items_list", )


class CustomerCartProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['product_cart_info']
