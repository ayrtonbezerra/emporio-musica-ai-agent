
from decimal import Decimal

from langchain.tools import tool

from emporio.repositories.products import (
    search_products as query_products,
    get_product_details as query_product_details,
)


@tool
def search_products(
    category: str | None = None,
    max_price: float | None = None,
    available_only: bool = True,
) -> list[dict]:
    """Search the store catalog by instrument category,
    maximum price and stock availability.
    Use when customers want to discover or compare products.
    """

    price = Decimal(str(max_price)) if max_price is not None else None

    return query_products(
        category=category,
        max_price=price,
        available_only=available_only,
    )


@tool
def get_product_details(product_id: int) -> dict:
    """Retrieve detailed information about a specific product,
    including its description, technical specifications,
    price and stock availability.
    """

    product = query_product_details(product_id)

    if product is None:
        return {"error": "Product not found"}

    return product