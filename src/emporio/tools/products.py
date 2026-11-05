from decimal import Decimal
from langchain.tools import tool
from emporio.repositories.products import (
    search_products as query_products,
    get_product_details as query_product_details,
)
from emporio.schemas.products import (
    SearchProductsInput,
    GetProductDetailsInput,
)
from emporio.tools.errors import (
    handle_validation_error,
    tool_error,
    handle_database_errors,
)


@tool(args_schema=SearchProductsInput)
@handle_database_errors
def search_products(
    category: str | None = None,
    max_price: float | None = None,
    available_only: bool = True,
) -> list[dict]:
    """Busca instrumentos no catálogo por categoria, preço máximo
    e disponibilidade em estoque.
    Utilize quando o cliente quiser encontrar ou comparar produtos.
    """

    price = Decimal(str(max_price)) if max_price is not None else None

    return query_products(
        category=category,
        max_price=price,
        available_only=available_only,
    )


search_products.handle_validation_error = handle_validation_error


@tool(args_schema=GetProductDetailsInput)
@handle_database_errors
def get_product_details(product_id: int) -> dict:
    """Consulta informações detalhadas de um produto específico,
    incluindo descrição, especificações técnicas, preço e estoque.
    """

    product = query_product_details(product_id)

    if product is None:
        return tool_error(
            code="NOT_FOUND",
            message="Produto não encontrado no catálogo.",
        )

    return product


get_product_details.handle_validation_error = handle_validation_error