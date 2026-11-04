from decimal import Decimal
from emporio.database import get_connection


def search_products(
    category: str | None = None,
    max_price: Decimal | None = None,
    available_only: bool = True,
) -> list[dict]:

    query = """
        SELECT
            p.product_id,
            p.name,
            c.name AS category,
            p.description,
            p.price_brl,
            p.stock_quantity,
            p.status
        FROM products p
        JOIN categories c
            ON p.category_id = c.category_id
        WHERE 1 = 1
    """

    params = []

    if category is not None:
        query += " AND LOWER(c.name) = LOWER(%s)"
        params.append(category)

    if max_price is not None:
        query += " AND p.price_brl <= %s"
        params.append(max_price)

    if available_only:
        query += """
            AND p.status = 'active'
            AND p.stock_quantity > 0
        """

    query += " ORDER BY p.price_brl ASC LIMIT 20"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()


def get_product_details(product_id: int) -> dict | None:
    query = """
        SELECT
            p.product_id,
            p.name,
            c.name AS category,
            p.description,
            p.price_brl,
            p.stock_quantity,
            p.status,
            p.specs
        FROM products p
        JOIN categories c
            ON p.category_id = c.category_id
        WHERE p.product_id = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (product_id,))
            return cur.fetchone()
