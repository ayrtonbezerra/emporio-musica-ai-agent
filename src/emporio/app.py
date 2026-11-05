
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.checkpoint.postgres import PostgresSaver


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from emporio.agent import build_agent
from emporio.database import get_connection


st.set_page_config(
    page_title="Empório da Música",
    page_icon="🎸",
    layout="centered",
)


def render_text(text: str) -> str:
    return text.replace("$", r"\$")


@st.cache_data(ttl=60)
def list_customers() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    customer_id,
                    name,
                    email
                FROM customers
                ORDER BY name
                """
            )
            return cur.fetchall()


def list_customer_orders(customer_id: int) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    order_id,
                    status
                FROM orders
                WHERE customer_id = %s
                ORDER BY order_date DESC
                """,
                (customer_id,),
            )
            return cur.fetchall()


def get_conninfo() -> str:
    return make_conninfo(
        os.environ["DATABASE_URL"],
        hostaddr="127.0.0.1",
        connect_timeout=5,
    )


def get_thread_config(customer_id: int) -> dict:
    return {
        "configurable": {
            "thread_id": f"customer-{customer_id}",
        }
    }


def render_history(messages: list) -> None:
    for message in messages:
        if isinstance(message, HumanMessage):
            if isinstance(message.content, str):
                with st.chat_message("user"):
                    st.markdown(render_text(message.content))

        elif isinstance(message, AIMessage):
            if message.tool_calls:
                continue

            if isinstance(message.content, str) and message.content:
                with st.chat_message("assistant"):
                    st.markdown(render_text(message.content))


st.title("🎸 Empório da Música")
st.caption("Central de Atendimento Virtual")

customers = list_customers()

if not customers:
    st.warning("Nenhum cliente cadastrado no banco de dados.")
    st.stop()

customers_by_id = {
    customer["customer_id"]: customer
    for customer in customers
}


with st.sidebar:
    st.title("Atendimento")

    customer_id = st.selectbox(
        "Selecione um cliente",
        options=list(customers_by_id.keys()),
        format_func=lambda cid: (
            f"{customers_by_id[cid]['name']} "
            f"— {customers_by_id[cid]['email']}"
        ),
        index=None,
        placeholder="Escolha um perfil...",
    )

    if customer_id is not None:
        customer = customers_by_id[customer_id]

        st.divider()

        st.write(f"**{customer['name']}**")
        st.caption(customer["email"])

        st.success("Perfil selecionado")

        st.caption(
            "Seu histórico de conversa é salvo automaticamente. "
            "Você pode trocar de perfil e voltar depois."
        )

        st.divider()

        with st.expander("Meus pedidos"):
            orders = list_customer_orders(customer_id)

            if not orders:
                st.caption("Nenhum pedido cadastrado.")

            for order in orders:
                st.write(
                    f"**#{order['order_id']}** "
                    f"— {order['status']}"
                )

    st.divider()

    st.caption(
        "Ambiente de demonstração com dados fictícios. "
        "A seleção de perfil não é autenticação real."
    )


if customer_id is None:
    st.info(
        "Selecione um cliente na barra lateral "
        "para iniciar ou continuar um atendimento."
    )
    st.stop()


customer = customers_by_id[customer_id]
config = get_thread_config(customer_id)


with PostgresSaver.from_conn_string(get_conninfo()) as checkpointer:
    agent = build_agent(checkpointer)

    state = agent.get_state(config)
    history = state.values.get("messages", [])

    st.subheader(f"Olá, {customer['name']}!")

    st.caption(
        "Posso ajudar com produtos, preços, promoções, "
        "pedidos e políticas da loja."
    )

    st.divider()

    render_history(history)

    prompt = st.chat_input("Digite sua mensagem...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(render_text(prompt))

        incoming_messages = []

        if not history:
            incoming_messages.append(
                SystemMessage(
                    content=(
                        "Contexto do atendimento de demonstração: "
                        f"o cliente selecionado é {customer['name']}, "
                        f"customer_id={customer_id}, "
                        f"email={customer['email']}. "
                        "Quando uma ferramenta de pedidos exigir "
                        "o e-mail do cliente, utilize o e-mail "
                        "deste perfil, sem solicitá-lo novamente. "
                        "A seleção do perfil é demonstrativa "
                        "e não representa autenticação segura."
                    )
                )
            )

        incoming_messages.append(
            HumanMessage(content=prompt)
        )

        with st.chat_message("assistant"):
            with st.spinner("Consultando..."):
                try:
                    result = agent.invoke(
                        {
                            "messages": incoming_messages
                        },
                        config=config,
                        context={
                            "customer_id": customer_id,
                        },
                    )

                    response = result["messages"][-1].content

                    if isinstance(response, str):
                        st.markdown(render_text(response))
                    else:
                        st.write(response)

                except Exception as exc:
                    st.error(
                        "Não foi possível processar sua mensagem."
                    )
                    st.exception(exc)
                    st.stop()

        st.rerun()
