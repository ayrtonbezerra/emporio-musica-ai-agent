from langchain.tools import tool
from emporio.repositories.orders import get_order_details as query_order


@tool
def get_order_details(order_id: int, customer_email: str) -> dict:
    """Consulta os detalhes de um pedido da Empório da Música.

    Utilize quando o cliente perguntar sobre o status de um pedido,
    produtos comprados, previsão de entrega ou rastreamento.

    Parâmetros:
    - order_id: número do pedido informado pelo cliente.
    - customer_email: e-mail associado ao pedido.

    Solicite ambos os dados caso ainda não estejam disponíveis.
    Nunca tente consultar pedidos de outros clientes.
    """

    order = query_order(order_id, customer_email)

    if order is None:
        return {
            "error": "Pedido não encontrado ou e-mail não corresponde ao cadastro."
        }

    return order