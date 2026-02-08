from django.urls import path

from payments.api import views

urlpatterns = [
    path("order/<uuid:order_id>/", views.PaymentByOrderView.as_view(), name="payment-by-order"),
    path("all/", views.PaymentListView.as_view(), name="payment-list"),
]
