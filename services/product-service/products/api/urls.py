from django.urls import path

from products.api import views

urlpatterns = [
    path("all/", views.ProductsView.as_view()),
    path("<uuid:product_id>/", views.ProductDetailView.as_view()),
    path("create/", views.ProductCreateView.as_view()),
    path("<uuid:product_id>/update/", views.ProductUpdateView.as_view()),
]