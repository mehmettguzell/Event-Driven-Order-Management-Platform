from django.urls import path

from orders.api import views

app_name = "orders_api"

urlpatterns = [
    path("create-order/", views.CreateOrderView.as_view(), name="create-order"),
    path("<uuid:order_id>/", views.OrderView.as_view(), name="order-detail"),
    path("all/", views.OrderView.as_view(), name="order-list"),
]