from langchain.tools import tool
from emporio.repositories.orders import get_order_details as query_order
from emporio.schemas.orders import GetOrderDetailsInput
from emporio.tools.errors import (
    handle_validation_error,
    tool_error,
    handle_database_errors,
)


@tool(args_schema=GetOrderDetailsInput)
@handle_database_errors
def get_order_details(order_id: int, customer_email: str) -> dict:
    """Consulta os detalhes de um pedido da Empório da Música.

    Utilize quando o cliente perguntar sobre status, produtos
    comprados, previsão de entrega ou rastreamento.

    Solicite o número do pedido e o e-mail associado.
    Nunca consulte pedidos de outros clientes.
    """

    order = query_order(order_id, customer_email)

    if order is None:
        return tool_error(
            code="ORDER_NOT_FOUND",
            message=(
                "Não foi possível localizar um pedido com os dados informados. "
                "Solicite ao cliente que confira o número do pedido e o e-mail."
            ),
        )

    return order


get_order_details.handle_validation_error = handle_validation_error