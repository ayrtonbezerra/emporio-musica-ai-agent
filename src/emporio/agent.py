from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from emporio.tools.products import (
    search_products,
    get_product_details,
)
from emporio.tools.policies import get_store_policy
from emporio.tools.orders import get_order_details

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")

PROMPT_PATH = ROOT / "prompts" / "system.md"

SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)

agent = create_agent(
    model=model,
    tools = [
        search_products,
        get_product_details,
        get_store_policy,
        get_order_details
    ],
    system_prompt = SYSTEM_PROMPT
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