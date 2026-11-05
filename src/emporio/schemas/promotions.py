from pydantic import BaseModel, Field


class GetPromotionsInput(BaseModel):
    product_id: int | None = Field(
        default=None,
        gt=0,
        strict=True,
        description=(
            "ID do produto para consultar promoções específicas. "
            "Se não informado, consulta todas as promoções ativas."
        ),
    )