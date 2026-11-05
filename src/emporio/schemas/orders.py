from pydantic import BaseModel, Field, EmailStr


class GetOrderDetailsInput(BaseModel):
    order_id: int = Field(
        gt=0,
        strict=True,
        description="Número inteiro e positivo do pedido.",
    )

    customer_email: EmailStr = Field(
        description="E-mail do cliente associado ao pedido.",
    )