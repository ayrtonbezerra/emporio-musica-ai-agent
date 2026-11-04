
from langchain.tools import tool
from emporio.repositories.policies import get_policy


@tool
def get_store_policy(topic: str) -> dict:
    """Consulta as políticas e procedimentos da Empório da Música.

    Utilize esta ferramenta para responder perguntas sobre regras,
    funcionamento, pagamentos, entregas e procedimentos da loja.

    Assuntos disponíveis (valores aceitos para 'topic'):
    - store_info: endereço, contatos e informações da empresa.
    - store_hours: horários de funcionamento.
    - payments: formas de pagamento, PIX e parcelamento.
    - returns_and_exchanges: trocas, devoluções e arrependimento.
    - shipping: frete, entrega e rastreamento.
    - promotions: regras de promoções e descontos.
    - customer_service: atendimento e reclamações.
    - warranty: garantias dos produtos.
    - privacy: privacidade e proteção de dados.
    - general_guidelines: orientações gerais da loja.
    - document_inconsistencies: divergências identificadas no manual.

    Informe exatamente uma dessas chaves no parâmetro topic.
    Se a pergunta envolver mais de um assunto, consulte
    as políticas necessárias separadamente.
    """

    policy = get_policy(topic)

    if policy is None:
        return {"error": "Política não encontrada."}

    return policy