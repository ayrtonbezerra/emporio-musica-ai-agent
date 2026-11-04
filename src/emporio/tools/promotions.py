from langchain.tools import tool
from emporio.repositories.promotions import get_promotions as query_promotions


@tool
def get_promotions(product_id: int | None = None) -> list[dict]:
    """Consulta as promoções ativas da Empório da Música.

    Utilize quando o cliente perguntar sobre descontos,
    ofertas ou preços promocionais.

    Parâmetros:
    - product_id: ID do produto específico (opcional).
      Se não informado, retorna todas as promoções ativas.

    Os resultados incluem preço original, desconto percentual,
    preço promocional, estoque e status do produto.

    Não recomende produtos indisponíveis ou sem estoque.
    Para regras de cumulatividade e descontos no PIX,
    consulte a política 'promotions' da loja.
    """
    return query_promotions(product_id)