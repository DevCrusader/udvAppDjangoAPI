from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import get_user_info, create_request, BalanceAPIView, \
    get_requests_in_progress, process_request, search_user, get_requests_full, get_request_latest, \
    get_unread_present_count, get_unread_present_list, \
    get_present_list, create_present, manage_present_by_pk, \
    get_balance_history, \
    create_user, create_user_by_table, get_moderator_list, manage_moderator, \
    get_activities, manage_activities_admin, manage_activity_by_pk
from .store_views import get_user_orders_latest, get_user_orders_full, create_order, \
    get_products_to_admin, create_product, manage_product, \
    get_items_list_to_admin, manage_item, create_item, \
    get_products_to_store, get_items_to_product_page, \
    get_orders_to_admin, get_order_to_admin_by_pk, manage_order, \
    get_cart, manage_cart_by_pk, manage_cart
from .views import MyTokenObtainPairView

from .views import TableUploadAPI, create_users_by_table

urlpatterns = [
    # Authentication token
    path("token/refresh/", TokenRefreshView.as_view(), name='token-refresh'),
    path("token/", MyTokenObtainPairView.as_view(), name="token-pair"),

    # User personal info
    path("userbalance/", BalanceAPIView.as_view(), name="user-balance"),
    path("userinfo/unread-presents/", get_unread_present_count, name="user-unread-present-count"),
    path("userinfo/", get_user_info, name="user-info"),
    path("userhistory/request/full/", get_requests_full, name="user-requests-full"),
    path("userhistory/order/full/", get_user_orders_full, name="user-orders-full"),
    path("userhistory/present/full/", get_present_list, name="user-presents-full"),
    path("userhistory/balance/", get_balance_history, name="user-balance-history"),
    path("userhistory/request/", get_request_latest, name="user-requests"),
    path("userhistory/order/", get_user_orders_latest, name="user-orders"),
    path("userhistory/present/", get_unread_present_list, name="user-presents-unread"),

    # Creating service objects by common user
    path("activities/", get_activities, name="activities"),
    path("store/create/request/", create_request, name="create-request"),
    path("store/create/order/", create_order, name="create-order"),
    path("store/create/present/", create_present, name="create-present"),

    # Work with service objects by common user
    path("store/presents/<str:pk>/", manage_present_by_pk, name="manage-present-by-pk"),

    path("store/products/<str:pk>/", get_items_to_product_page, name="store-product-item"),
    path("store/products/", get_products_to_store, name="store-products"),

    path("store/cart/items/<str:pk>/", manage_cart_by_pk, name="manage-cart-item-by-index"),
    path("store/cart/items/", manage_cart, name="manage-cart-item"),
    path("store/cart/<str:param>/", get_cart, name="get-cart"),


    # Creating service objects by admin user
    path("admin/create/product/", create_product, name="create-product"),
    path("admin/create/item/", create_item, name="create-item"),
    path("admin/create/user/", create_user, name="create-user"),
    path("admin/create/user_by_file/", TableUploadAPI.as_view()),
    path("admin/create/user_by_file/accept/", create_users_by_table),

    path("admin/products/",
         get_products_to_admin, name="get-products-admin"),
    path("admin/products/<str:pk>/items/",
         get_items_list_to_admin, name="get-product-items"),
    path("admin/products/<str:pk>/", manage_product, name="manage-product"),
    path("admin/items/<str:pk>/", manage_item, name="manage-item"),

    path("admin/activities/<str:pk>/", manage_activity_by_pk),
    path("admin/activities/", manage_activities_admin),

    path("admin/orders/<str:pk>/completed/", manage_order, name="manage-order"),
    path("admin/orders/<str:pk>/", get_order_to_admin_by_pk, name="get-order-by-pk"),
    path("admin/orders/", get_orders_to_admin, name="get-orders"),

    path("admin/requests/<str:pk>/", process_request, name="process-request"),
    path("admin/requests/", get_requests_in_progress, name="get-requests"),

    path("admin/moderators/<str:pk>/", manage_moderator, name="manage-moderator"),
    path("admin/moderators/", get_moderator_list, name="moderators-list"),

    # Util for service
    path("search-user/<str:search_request>/", search_user, name="search_user"),
]
