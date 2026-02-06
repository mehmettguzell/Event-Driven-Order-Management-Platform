"""
Product service layer for business logic.
This layer handles complex business rules and orchestrates multiple operations.
"""
from django.db import transaction
from products.models import Product
from products.selectors import get_all_products, get_product_by_id
from products.exceptions import DomainException


class ProductNotFound(DomainException):
    code = "PRODUCT_NOT_FOUND"
    message = "Product not found."


def create_product(*, sku: str, name: str, description: str, price: float, is_active: bool = True):
    """
    Create a new product with business logic validation.
    
    Args:
        sku: Product SKU (must be unique)
        name: Product name
        description: Product description
        price: Product price (must be > 0)
        is_active: Whether product is active
    
    Returns:
        Created Product instance
    
    Raises:
        DomainException: If validation fails
    """
    if price <= 0:
        raise DomainException("Price must be greater than zero.")
    
    if Product.objects.filter(sku__iexact=sku).exists():
        raise DomainException("A product with this SKU already exists.")
    
    with transaction.atomic():
        product = Product.objects.create(
            sku=sku.upper(),
            name=name,
            description=description,
            price=price,
            is_active=is_active,
        )
    
    return product


def update_product(*, product_id: str, **update_fields):
    """
    Update an existing product.
    
    Args:
        product_id: Product UUID
        **update_fields: Fields to update
    
    Returns:
        Updated Product instance
    
    Raises:
        ProductNotFound: If product doesn't exist
        DomainException: If validation fails
    """
    product = get_product_by_id(product_id)
    
    if not product:
        raise ProductNotFound()
    
    if "price" in update_fields and update_fields["price"] <= 0:
        raise DomainException("Price must be greater than zero.")
    
    if "sku" in update_fields:
        # Check SKU uniqueness (excluding current product)
        if Product.objects.filter(sku__iexact=update_fields["sku"]).exclude(id=product_id).exists():
            raise DomainException("A product with this SKU already exists.")
        update_fields["sku"] = update_fields["sku"].upper()
    
    with transaction.atomic():
        for field, value in update_fields.items():
            setattr(product, field, value)
        product.save(update_fields=list(update_fields.keys()))
    
    return product