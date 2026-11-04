from emporio.database import get_connection


def get_order_details(order_id: int, customer_email: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    o.order_id,
                    o.order_date,
                    o.status,
                    o.total_brl,
                    o.payment_method,
                    o.tracking_code,
                    o.estimated_delivery,
                    o.notes
                FROM orders o
                JOIN customers c
                    ON o.customer_id = c.customer_id
                WHERE o.order_id = %s
                  AND LOWER(c.email) = LOWER(%s)
                """,
                (order_id, customer_email.strip()),
            )

            order = cur.fetchone()

            if order is None:
                return None

            cur.execute(
                """
                SELECT
                    oi.product_id,
                    p.name AS product_name,
                    oi.quantity
                FROM order_items oi
                JOIN products p
                    ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
                """,
                (order_id,),
            )

            order["items"] = cur.fetchall()

            return order