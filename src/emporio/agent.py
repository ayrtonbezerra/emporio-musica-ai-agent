
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from emporio.tools.products import (
    search_products,
    get_product_details,
)

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)

agent = create_agent(
    model=model,
    tools=[search_products, get_product_details],
    system_prompt="""
    Você é o assistente virtual da Empório da Música,
    uma loja especializada em instrumentos musicais.

    Seu tom deve ser amigável, objetivo e profissional.

    Regras:
    - Consulte as ferramentas antes de informar preços,
      estoque ou características de produtos.
    - Nunca invente informações sobre produtos.
    - Se não encontrar um produto, informe ao cliente.
    - Não realize vendas ou reservas.
    - Responda sempre em português brasileiro.
    - A loja comercializa exclusivamente instrumentos musicais.
    - Não ofereça acessórios como cordas, palhetas, cabos,
    pedais ou amplificadores.
    """,
)


def main():
    messages = []

    print("Empório da Música — Assistente Virtual")
    print("Digite 'sair' para encerrar.\n")

    while True:
        user_input = input("Você: ").strip()

        if user_input.lower() == "sair":
            break

        if not user_input:
            continue

        messages.append({
            "role": "user",
            "content": user_input,
        })

        result = agent.invoke({"messages": messages})
        messages = result["messages"]

        print(f"\nAgente: {messages[-1].content}\n")


if __name__ == "__main__":
    main()