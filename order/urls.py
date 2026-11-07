from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    CheckoutView,
    OrderDetailView,
    OrderListView,
    PaymentView,
    ReceiptUploadView,
    RemoveCartItemView,
    UpdateCartItemView,
)

app_name = "order"

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart"),
    path("cart/add/<str:slug>/", AddToCartView.as_view(), name="add_to_cart"),
    path(
        "cart/update/<int:product_id>/",
        UpdateCartItemView.as_view(),
        name="update_cart_item",
    ),
    path(
        "cart/remove/<int:product_id>/",
        RemoveCartItemView.as_view(),
        name="remove_cart_item",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path(
        "payment/<str:order_number>/",
        PaymentView.as_view(),
        name="payment",
    ),
    path(
        "payment/<str:order_number>/receipt/",
        ReceiptUploadView.as_view(),
        name="upload_receipt",
    ),
    path("orders/", OrderListView.as_view(), name="order_list"),
    path(
        "orders/<str:order_number>/",
        OrderDetailView.as_view(),
        name="order_detail",
    ),
]
