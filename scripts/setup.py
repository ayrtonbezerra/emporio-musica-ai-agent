import getpass
import hashlib
import os
import secrets
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

import psycopg
from dotenv import dotenv_values, set_key
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.conninfo import make_conninfo


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
TABLES = (
    "categories",
    "customers",
    "products",
    "orders",
    "order_items",
    "promotions",
)


def run(*command, env):
    print(f"\nExecutando: {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def find_free_port():
    for port in range(5433, 5500):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("Nenhuma porta disponível entre 5433 e 5499.")


def preflight():
    required = [
        ROOT / "compose.yaml",
        ROOT / "sql" / "001_create_tables.sql",
        ROOT / "scripts" / "load_data.py",
        ROOT / "src" / "emporio" / "app.py",
        *(
            ROOT / "data" / f"desafio_tecnico_ai_eng - {table}.csv"
            for table in TABLES
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Arquivos ausentes:\n- " + "\n- ".join(missing))

    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    if "${POSTGRES_PORT" not in compose:
        raise RuntimeError(
            "Altere a porta em compose.yaml para: "
            "127.0.0.1:${POSTGRES_PORT:-5433}:5432"
        )


def setup_env():
    if not ENV_FILE.exists():
        ENV_FILE.touch()

    saved = {k: v for k, v in dotenv_values(ENV_FILE).items() if v is not None}
    project_hash = hashlib.sha256(str(ROOT).casefold().encode()).hexdigest()[:10]

    existing_port = None
    if saved.get("DATABASE_URL"):
        try:
            existing_port = urlsplit(saved["DATABASE_URL"]).port
        except ValueError:
            pass

    port = int(saved.get("POSTGRES_PORT") or existing_port or find_free_port())
    db_user = saved.get("POSTGRES_USER") or "emporio"
    db_password = saved.get("POSTGRES_PASSWORD") or secrets.token_urlsafe(24)
    db_name = saved.get("POSTGRES_DB") or "emporio"
    project_name = saved.get("COMPOSE_PROJECT_NAME") or f"emporio_demo_{project_hash}"

    api_key = saved.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "SUBSTITUA_PELA_SUA_CHAVE":
        api_key = getpass.getpass("Chave da OpenAI (OPENAI_API_KEY): ").strip()
        if not api_key:
            raise ValueError("A chave da OpenAI é obrigatória.")

    langsmith_key = saved.get("LANGSMITH_API_KEY", "").strip()
    langsmith_project = saved.get("LANGSMITH_PROJECT") or "emporio-musica-demo"
    langsmith_enabled = saved.get("LANGSMITH_TRACING", "").lower() == "true"

    if "LANGSMITH_TRACING" not in saved:
        answer = input("Ativar LangSmith? [s/N]: ").strip().lower()
        langsmith_enabled = answer in ("s", "sim", "y", "yes")

    if langsmith_enabled and not langsmith_key:
        langsmith_key = getpass.getpass("Chave do LangSmith: ").strip()
        if not langsmith_key:
            raise ValueError("Informe a chave do LangSmith ou desative o tracing.")
        langsmith_project = (
            input(f"Projeto LangSmith [{langsmith_project}]: ").strip()
            or langsmith_project
        )

    database_url = (
        f"postgresql://{quote(db_user, safe='')}:{quote(db_password, safe='')}"
        f"@127.0.0.1:{port}/{quote(db_name, safe='')}"
    )

    values = {
        "POSTGRES_USER": db_user,
        "POSTGRES_PASSWORD": db_password,
        "POSTGRES_DB": db_name,
        "POSTGRES_PORT": str(port),
        "COMPOSE_PROJECT_NAME": project_name,
        "DATABASE_URL": database_url,
        "OPENAI_API_KEY": api_key,
        "LANGSMITH_TRACING": str(langsmith_enabled).lower(),
    }
    if langsmith_enabled:
        values["LANGSMITH_API_KEY"] = langsmith_key
        values["LANGSMITH_PROJECT"] = langsmith_project

    for key, value in values.items():
        set_key(str(ENV_FILE), key, value, quote_mode="always")

    if os.name != "nt":
        ENV_FILE.chmod(0o600)

    return {**os.environ, **saved, **values}


def setup_database(env):
    conninfo = make_conninfo(env["DATABASE_URL"], connect_timeout=10)
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                (ROOT / "sql" / "001_create_tables.sql").read_text(encoding="utf-8")
            )
            counts = {}
            for table in TABLES:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]

    if all(count == 0 for count in counts.values()):
        run(sys.executable, str(ROOT / "scripts" / "load_data.py"), env=env)
    elif any(count == 0 for count in counts.values()):
        raise RuntimeError(
            "Banco parcialmente populado. Verifique os dados antes de continuar: "
            f"{counts}"
        )
    else:
        print("Dados já carregados; preservando a base existente.")

    with PostgresSaver.from_conn_string(conninfo) as saver:
        saver.setup()

    print("PostgreSQL, dados e histórico do LangGraph configurados.")


def main():
    preflight()
    env = setup_env()
    run("docker", "compose", "version", env=env)
    run("docker", "info", "--format", "{{.ServerVersion}}", env=env)
    run("docker", "compose", "up", "-d", "--wait", env=env)
    setup_database(env)
    print("\nInstalação concluída. Iniciando Streamlit...\n")
    run(sys.executable, "-m", "streamlit", "run", "src/emporio/app.py", env=env)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, psycopg.Error) as exc:
        print(f"\nFalha na configuração: {exc}", file=sys.stderr)
        sys.exit(1)
