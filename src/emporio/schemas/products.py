from typing import Literal

from pydantic import BaseModel, Field, StrictBool


class SearchProductsInput(BaseModel):
    category: Literal[
        "Guitarras",
        "Baixos",
        "Baterias e Percussão",
        "Teclados e Pianos",
        "Violões",
        "Instrumentos de Sopro (Madeiras)",
        "Instrumentos de Sopro (Metais)",
        "Cordas Orquestrais",
        "Ukuleles",
    ] | None = Field(
        default=None,
        description="Categoria exata do catálogo. Interprete a intenção do cliente e selecione uma das categorias permitidas.",
    )

    max_price: float | None = Field(
        default=None,
        gt=0,
        allow_inf_nan=False,
        description="Preço máximo em reais. Deve ser positivo.",
    )

    available_only: StrictBool = Field(
        default=True,
        description="Se True, retorna somente produtos ativos e com estoque disponível.",
    )

class GetProductDetailsInput(BaseModel):
    product_id: int = Field(
        ...,
        gt=0,
        strict=True,
        description="ID numérico e positivo do produto no catálogo.",
    )