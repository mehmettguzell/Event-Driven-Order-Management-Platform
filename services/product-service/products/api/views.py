from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache

from products.api.serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)
from products.common.responses import success_response, error_response
from products.selectors import get_all_products, get_product_by_id
from products.services.product_service import create_product, update_product, ProductNotFound
from products.exceptions import DomainException


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductsView(APIView):
    pagination_class = ProductPagination
    
    def get(self, request):
        only_active = request.query_params.get("only_active", "true").lower() == "true"
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        search_query = request.query_params.get("search", "").strip() or None
        sku = request.query_params.get("sku", "").strip() or None
        ordering = request.query_params.get("ordering", "-created_at")
        
        allowed_orderings = [
            "created_at", "-created_at",
            "price", "-price",
            "name", "-name",
            "sku", "-sku",
        ]
        if ordering not in allowed_orderings:
            ordering = "-created_at"
        
        try:
            min_price = float(min_price) if min_price else None
        except (ValueError, TypeError):
            min_price = None
        
        try:
            max_price = float(max_price) if max_price else None
        except (ValueError, TypeError):
            max_price = None
        
        cache_key = f"products_list_{only_active}_{min_price}_{max_price}_{search_query}_{sku}_{ordering}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(
                success_response(cached_result),
                status=status.HTTP_200_OK,
            )
        
        products = get_all_products(
            only_active=only_active,
            min_price=min_price,
            max_price=max_price,
            search_query=search_query,
            sku=sku,
            ordering=ordering,
        )
        
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)
        
        serializer = ProductSerializer(paginated_products, many=True)
        
        response_data = {
            "products": serializer.data,
            "pagination": {
                "page": paginator.page.number,
                "page_size": paginator.page_size,
                "total_pages": paginator.page.paginator.num_pages,
                "total_items": paginator.page.paginator.count,
                "has_next": paginator.page.has_next(),
                "has_previous": paginator.page.has_previous(),
            },
        }
        
        cache.set(cache_key, response_data, 300)
        
        return Response(
            success_response(response_data),
            status=status.HTTP_200_OK,
        )


class ProductDetailView(APIView):
    """
    Retrieve a single product by UUID.
    """
    
    def get(self, request, product_id):
        # Try cache first
        cache_key = f"product_detail_{product_id}"
        cached_product = cache.get(cache_key)
        if cached_product:
            return Response(
                success_response(cached_product),
                status=status.HTTP_200_OK,
            )
        
        product = get_product_by_id(product_id)
        
        if not product:
            return Response(
                error_response("PRODUCT_NOT_FOUND", "Product not found."),
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ProductSerializer(product)
        
        # Cache for 10 minutes (detail views cached longer)
        cache.set(cache_key, serializer.data, 600)
        
        return Response(
            success_response(serializer.data),
            status=status.HTTP_200_OK,
        )


class ProductCreateView(APIView):
    """
    Create a new product.
    """
    
    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            product = create_product(**serializer.validated_data)
        except DomainException as e:
            return Response(
                error_response(e.code, e.message),
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Invalidate product list cache (clear all list caches)
        # Note: In production with Redis, use cache.delete_pattern or cache versioning
        # For now, we'll clear the entire cache on write operations
        cache.clear()
        
        response_serializer = ProductSerializer(product)
        
        return Response(
            success_response(response_serializer.data),
            status=status.HTTP_201_CREATED,
        )


class ProductUpdateView(APIView):
    """
    Update an existing product (partial update supported).
    """
    
    def put(self, request, product_id):
        serializer = ProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            product = update_product(product_id=product_id, **serializer.validated_data)
        except ProductNotFound:
            return Response(
                error_response("PRODUCT_NOT_FOUND", "Product not found."),
                status=status.HTTP_404_NOT_FOUND,
            )
        except DomainException as e:
            return Response(
                error_response(e.code, e.message),
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Invalidate caches
        cache.delete(f"product_detail_{product_id}")
        # Clear list caches (in production, use cache versioning or delete_pattern)
        cache.clear()
        
        response_serializer = ProductSerializer(product)
        
        return Response(
            success_response(response_serializer.data),
            status=status.HTTP_200_OK,
        )

