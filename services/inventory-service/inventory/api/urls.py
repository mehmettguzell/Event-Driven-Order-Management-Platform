from django.urls import path

from inventory.api import views

urlpatterns = [
    path("", views.InventoryListCreateView.as_view(), name="inventory-list-create"),
    path("<uuid:product_id>/", views.InventoryDetailView.as_view(), name="inventory-detail"),
]
