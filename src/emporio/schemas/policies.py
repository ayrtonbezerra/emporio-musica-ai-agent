from typing import Literal

from pydantic import BaseModel, Field


class GetStorePolicyInput(BaseModel):
    topic: Literal[
        "store_info",
        "store_hours",
        "payments",
        "returns_and_exchanges",
        "shipping",
        "promotions",
        "customer_service",
        "warranty",
        "privacy",
        "general_guidelines",
        "document_inconsistencies",
    ] = Field(
        description=(
            "Assunto da política a consultar. "
            "Interprete a pergunta do cliente e selecione "
            "a chave correspondente entre as opções permitidas."
        ),
    )