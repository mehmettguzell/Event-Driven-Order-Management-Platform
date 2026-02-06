from typing import Optional
from django.db.models import QuerySet, Q
from products.models import Product


def get_all_products(
    *,
    only_active: bool = True,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search_query: Optional[str] = None,
    sku: Optional[str] = None,
    ordering: str = "-created_at",
) -> QuerySet[Product]:
    """
    Optimized product selector with filtering and ordering.
    
    Args:
        only_active: Filter only active products (default: True)
        min_price: Minimum price filter
        max_price: Maximum price filter
        search_query: Search in name and description (case-insensitive)
        sku: Filter by exact SKU
        ordering: Ordering field (default: "-created_at")
    
    Returns:
        QuerySet of Product objects with optimized queries.
    """
    qs = Product.objects.all()
    
    # Apply filters
    if only_active:
        qs = qs.filter(is_active=True)
    
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    
    if sku:
        qs = qs.filter(sku=sku)
    
    if search_query:
        qs = qs.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    # Apply ordering
    qs = qs.order_by(ordering)
    
    # Optimize query: only fetch needed fields
    # Using only() reduces memory and network transfer
    return qs.only(
        "id",
        "sku",
        "name",
        "description",
        "price",
        "is_active",
        "created_at",
    )


def get_product_by_id(product_id: str) -> Optional[Product]:
    """
    Get a single product by UUID.
    
    Args:
        product_id: Product UUID
    
    Returns:
        Product instance or None if not found
    """
    try:
        return Product.objects.only(
            "id",
            "sku",
            "name",
            "description",
            "price",
            "is_active",
            "created_at",
        ).get(id=product_id)
    except Product.DoesNotExist:
        return None


def get_products_by_skus(skus: list[str]) -> QuerySet[Product]:
    """
    Get multiple products by their SKUs.
    Useful for order processing where you need product details.
    
    Args:
        skus: List of SKU strings
    
    Returns:
        QuerySet of Product objects
    """
    return Product.objects.filter(sku__in=skus).only(
        "id",
        "sku",
        "name",
        "price",
        "is_active",
    )
