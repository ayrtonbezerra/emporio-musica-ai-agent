from emporio.database import get_connection


def get_promotions(product_id: int | None = None) -> list[dict]:
    query = """
        SELECT
            pr.promotion_id,
            pr.product_id,
            p.name AS product_name,
            p.price_brl AS original_price,
            pr.discount_percent,
            ROUND(
                p.price_brl * (1 - pr.discount_percent / 100),
                2
            ) AS promotional_price,
            pr.description,
            p.stock_quantity,
            p.status AS product_status
        FROM promotions pr
        JOIN products p
            ON pr.product_id = p.product_id
        WHERE pr.is_active = TRUE
    """

    params = []

    if product_id is not None:
        query += " AND pr.product_id = %s"
        params.append(product_id)

    query += " ORDER BY pr.discount_percent DESC"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()