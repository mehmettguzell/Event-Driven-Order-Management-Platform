from django.db import transaction, IntegrityError
from products.models import Product
from products.selectors import get_product_by_id
from products.exceptions import (
    ProductNotFound,
    ProductAlreadyExists,
    InvalidPrice,
)

def create_product(*, sku: str, name: str, description: str, price: float, is_active: bool = True):
    if price <= 0:
        raise InvalidPrice()
    
    if Product.objects.filter(sku__iexact=sku).exists():
        raise ProductAlreadyExists()

    try:
        with transaction.atomic():
            product = Product.objects.create(
                sku=sku.upper(),
                name=name,
                description=description,
                price=price,
                is_active=is_active,
            )
    except IntegrityError:
        raise ProductAlreadyExists()

    return product


def update_product(*, product_id: str, **update_fields):
    product = get_product_by_id(product_id)
    
    if not product:
        raise ProductNotFound()
    
    if "price" in update_fields and update_fields["price"] <= 0:
        raise InvalidPrice()
    
    if "sku" in update_fields:
        if Product.objects.filter(sku__iexact=update_fields["sku"]).exclude(id=product_id).exists():
            raise ProductAlreadyExists()
        update_fields["sku"] = update_fields["sku"].upper()
    
    with transaction.atomic():
        for field, value in update_fields.items():
            setattr(product, field, value)
        product.save(update_fields=list(update_fields.keys()))
    
    return product