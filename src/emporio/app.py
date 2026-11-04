
import os
import sys
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo
from langgraph.checkpoint.postgres import PostgresSaver

# Configuração dos caminhos e variáveis de ambiente
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

load_dotenv(ROOT / ".env")

from emporio.agent import build_agent


# Configuração da página
st.set_page_config(
    page_title="Empório da Música",
    page_icon="🎸",
    layout="centered",
)


# Inicialização da sessão
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# Barra lateral
with st.sidebar:
    st.title("Atendimentos")

    if st.button("Nova conversa", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()


# Área principal
st.title("🎸 Empório da Música")
st.caption("Assistente virtual especializado em instrumentos musicais")


# Exibição do histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Entrada do usuário
if prompt := st.chat_input("Como posso ajudar?"):

    # Armazena e exibe a mensagem do usuário
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Identifica a conversa no LangGraph
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    # Configuração da conexão com PostgreSQL
    conninfo = make_conninfo(
        os.environ["DATABASE_URL"],
        hostaddr="127.0.0.1",
        connect_timeout=5,
    )

    # Executa o agente e exibe a resposta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):

            with PostgresSaver.from_conn_string(
                conninfo
            ) as checkpointer:

                agent = build_agent(checkpointer)

                result = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ]
                    },
                    config=config,
                )

            response = result["messages"][-1].content

        st.markdown(response)

    # Armazena a resposta na interface
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })