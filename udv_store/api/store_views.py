import io, os

from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes, renderer_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from .models import BalanceHistory, Customer
from .store_models import Product, ProductItem, Size, Cart, Order
from .serializer import OrderListSerializer, ProductsSerializer, CustomOrdersSerializer, \
    OrderSerializer, ProductItemSerializer, ProductInStoreSerializer, ProductInAdminSerializer, \
    ProductItemInAdminSerializer, CustomerCartProductInfoSerializer, \
    ProductInProductPageSerializer, CustomerCartItemSerializer, CartSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_orders_latest(request):
    return Response([
        order.get_info_to_list_to_personal_page() for order in request.user.order_set.all()[:2]
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_orders_full(request):
    return Response([
        order.get_info_to_list_to_personal_page() for order in request.user.order_set.all()
    ])


@api_view(["GET"])
def get_products_to_store(request):
    products = Product.objects.annotate(
        items_count=Count("productitem"), item_sizes_count=Count("productitem__sizes"))\
        .filter(Q(items_count__gt=0) & (Q(item_sizes_count__gt=0) | Q(have_size=False)) & Q(state="Actual"))

    return Response(ProductInStoreSerializer(products, many=True).data)


@api_view(["GET"])
def get_products_to_admin(request):
    return Response(ProductInAdminSerializer(Product.objects.all(), many=True).data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_product(request):
    data = request.data
    # data["category_id"] = Category.objects.get(name=data["category_name"]).id
    serializer = ProductsSerializer(data=data, many=False)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(["POST", "DELETE"])
def manage_product(request, pk):
    product = Product.objects.get(product_id=pk)
    if request.method == "POST":
        data = request.data
        if data.get("change_state"):
            product.change_state(data["change_state"])
        else:
            product.change_product_params(data)

    if request.method == "DELETE":
        product.default_photo.delete(save=True)
        product.delete()

    return Response({"message": "Successfully!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_items_to_product_page(request, pk):
    product_response = ProductInProductPageSerializer(
            Product.objects.get(product_id=pk),
            many=False
        ).data
    return Response(
        {
            "product": product_response,
            "in_cart": "some"
        }
    )


@api_view(["GET"])
def get_items_list_to_admin(request, pk):
    return Response(
        ProductItemInAdminSerializer(
            Product.objects.get(product_id=pk),
            many=False
        ).data
    )


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_item(request):
    data = request.data

    pi = ProductItem.objects.create(
        product_id=Product.objects.get(product_id=data["product_id"]),
        color=data["color"],
        photo=data["photo"]
    )

    if data["set_size"] == "false":
        pi.sizes.add(Size.objects.get(size="No size"))

    return Response(ProductItemSerializer(pi).data)


@api_view(["POST", "DELETE"])
def manage_item(request, pk):
    pi = ProductItem.objects.get(id=pk)

    if request.method == "POST":
        data = request.data

        if data.get("action"):
            if data["action"] == "add":
                pi.add_size(data["size"])
            if data["action"] == "remove":
                pi.remove_size(data["size"])

    if request.method == "DELETE":
        pi.photo.delete(save=True)
        pi.delete()

    return Response({"message": "Successfully!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request, param):
    if param == 'product-info':
        return Response(
            CustomerCartProductInfoSerializer(
                Customer.objects.get(id=request.user.id)
            ).data
        )

    if param == 'product-item':
        return Response(
            CustomerCartItemSerializer(
                Customer.objects.get(id=request.user.id)
            ).data
        )

    return Response({'message': 'Incorrect request, check url, get params may only include '
                                '\"product-info\" or \"product-item\"'}, status=500)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_cart_by_pk(request, pk):
    data = request.data

    if request.method == "POST":
        cart_item = request.user.cart_set.get(id=pk)
        if data.get("action"):
            cart_item.change_count(data["action"])

    if request.method == "DELETE":
        request.user.cart_set.get(id=pk).delete()

    return Response({"message": "Successfully!"})


@api_view(["POST", "DELETE"])
def manage_cart(request):
    data = request.data

    if request.method == "POST":
        cart_item, created = request.user.cart_set.get_or_create(
            product_item_id=ProductItem.objects.get(id=data["product_item_id"]),
            size_id=Size.objects.filter(size=data["size"]).first(),
            defaults={"count": 1}
        )

        return Response(CartSerializer(cart_item, many=False).data)

    if request.method == "DELETE":
        request.user.cart_set.get(
            product_item_id=ProductItem.objects.get(id=data["product_item_id"]),
            size_id=Size.objects.get(size=data["size"])
        ).delete()


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_item_cart(request):
    pass


@api_view(["POST"])
def test_f(request, pk=None):
    if pk:
        return Response({"message": "pk is here"})
    else:
        return Response({"message": "pk isn't here"})


@api_view(["GET"])
def get_orders_to_admin(request):
    orders = Order.objects.filter(state="IR")
    return Response([order.get_info_to_orders_list_to_admin() for order in orders])


@api_view(["GET"])
def get_order_to_admin_by_pk(request, pk):
    order = Order.objects.get(id=pk)

    return Response(order.get_detail_info())


@api_view(["POST"])
def manage_order(request, pk):
    order = Order.objects.get(id=pk)

    if request.data.get("state"):
        order.set_state_completed()

    return Response({"message": "Successfully!"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    product_list = []
    customer = Customer.objects.get(id=request.user.id)


    order = Order.objects.create(
        user_id=request.user,
        products_list=JSONRenderer().render([
            c.get_order_info() for c in customer.cart_set.all()
        ]),
        office_address=request.data["office"]
    )

    BalanceHistory.objects.create(
        user_id=request.user,
        action="EX",
        category="OR",
        category_id=order.id,
        ucoin_count=request.data["totalSum"] if request.data.get("totalSum") else 0
    )

    customer.clear_cart()

    if request.data.get("totalSum"):
        request.user.userinfo.change_balance(request.data["totalSum"], "remove")

    return Response({"order_id": order.id})
