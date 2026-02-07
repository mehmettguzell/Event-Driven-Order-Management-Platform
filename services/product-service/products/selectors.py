from typing import Optional
from django.db.models import QuerySet, Q
from products.models import Product


def get_all_products(
        *,
        only_active : bool = True,
        min_price : Optional[float] = None,
        max_price : Optional[float] = None,
        search_query : Optional[str] = None,
        sku : Optional[str] = None,
        ordering : str = "-created_at"
) -> QuerySet[Product]:
    
    qs = Product.objects.all()

    if only_active:
        qs = qs.filter(is_active=True)

    if min_price is not None:
        qs = qs.filter(price__gte = min_price)
    
    if max_price is not None:
        qs = qs.filter(price__lte = max_price)

    if sku:
        qs = qs.filter(sku=sku)

    if search_query:
        search_query = search_query[:200].strip() if len(search_query) > 200 else search_query.strip()
        if search_query:
            qs = qs.filter(
                Q(name__icontains = search_query) | Q(description__icontains = search_query)
            )
    qs = qs.order_by(ordering)

    return qs.only(
        "id",
        "sku",
        "name",
        "description",
        "price",
        "is_active",
        "created_at"
    )


def get_product_by_id(product_id: str) -> Optional[Product]:
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
    if not skus:
        return Product.objects.none()
    return Product.objects.filter(sku__in=skus).only(
        "id",
        "sku",
        "name",
        "price",
        "is_active",
    )
