from django.contrib import admin
from .models import UserInfo, Activity, UcoinRequest
from .store_models import Product, ProductItem, ProductPhoto, Order


# Register your models here.
@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'balance', 'role')


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    sortable_by = ['-price']


@admin.register(Activity)
class ActivitiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'ucoins_count', 'created_date', 'last_date')


@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    list_display = ("product_id", "color")


# @admin.register(Cart)
# class CartsAdmin(admin.ModelAdmin):
#     list_display = ('user_id', 'product_id', 'count')

@admin.register(UcoinRequest)
class UcoinsRequestsAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'activity_id', 'created_date')
    sortable_by = ['-created_date']
#
#
@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'created_date', 'office_address')


@admin.register(ProductPhoto)
class ProductPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_item', 'photo', 'main_photo', 'created_date')

