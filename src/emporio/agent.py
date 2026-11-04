import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver

from emporio.tools.products import search_products, get_product_details
from emporio.tools.policies import get_store_policy
from emporio.tools.orders import get_order_details
from emporio.tools.promotions import get_promotions
from psycopg.conninfo import make_conninfo


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

PROMPT_PATH = ROOT / "prompts" / "system.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)


def main():
    with PostgresSaver.from_conn_string(
        make_conninfo(
            os.environ["DATABASE_URL"],
            hostaddr="127.0.0.1",
            connect_timeout=5,
        )
    ) as checkpointer:

        agent = create_agent(
            model=model,
            tools=[
                search_products,
                get_product_details,
                get_store_policy,
                get_order_details,
                get_promotions,
            ],
            system_prompt=SYSTEM_PROMPT,
            checkpointer=checkpointer,
        )

        config = {
            "configurable": {
                "thread_id": "cli-demo"
            }
        }

        print("Empório da Música — Assistente Virtual")
        print("Digite 'sair' para encerrar.\n")

        while True:
            user_input = input("Você: ").strip()

            if user_input.lower() == "sair":
                break

            if not user_input:
                continue

            result = agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": user_input}
                    ]
                },
                config=config,
            )

            print(f"\nAgente: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()