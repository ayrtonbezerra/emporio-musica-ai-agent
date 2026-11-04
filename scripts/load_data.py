import csv
import os
from pathlib import Path

import psycopg
from psycopg import sql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1] # pega o path da pasta raiz do projeto
DATA_DIR = ROOT / "data" # constrói o path para os CSV com os dados

load_dotenv(ROOT / ".env")

TABLES = [
    "categories",
    "customers",
    "products",
    "orders",
    "order_items",
    "promotions",
]


def load_data():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:

            cur.execute(
                "TRUNCATE TABLE "
                + ", ".join(TABLES)
            )

            for table in TABLES:
                path = DATA_DIR / f"desafio_tecnico_ai_eng - {table}.csv"

                with path.open(encoding="utf-8-sig", newline="") as f:
                    columns = next(csv.reader(f))
                    f.seek(0)

                    query = sql.SQL(
                        "COPY {} ({}) FROM STDIN "
                        "WITH (FORMAT CSV, HEADER TRUE)"
                    ).format(
                        sql.Identifier(table),
                        sql.SQL(", ").join(
                            sql.Identifier(c) for c in columns
                        ),
                    )

                    with cur.copy(query) as copy:
                        while chunk := f.read(65536):
                            copy.write(chunk)

                cur.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    )
                )
                print(f"{table}: {cur.fetchone()[0]} registros")

    print("Importação concluída!")


if __name__ == "__main__":
    load_data()