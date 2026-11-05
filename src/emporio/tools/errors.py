import json
from pydantic import ValidationError
import logging
from functools import wraps

from psycopg import Error as PsycopgError


def handle_validation_error(exc: ValidationError) -> str:
    issues = []

    for error in exc.errors():
        issue = {
            "field": ".".join(map(str, error["loc"])),
            "reason": error["type"],
            "message": error["msg"],
        }

        if "expected" in error.get("ctx", {}):
            issue["expected"] = error["ctx"]["expected"]

        issues.append(issue)

    fields = {issue["field"] for issue in issues}

    if "category" in fields:
        code = "INVALID_CATEGORY"
    elif "topic" in fields:
        code = "INVALID_TOPIC"
    else:
        code = "INVALID_ARGUMENT"

    return json.dumps(
        {
            "ok": False,
            "error": {
                "code": code,
                "message": "Corrija os argumentos inválidos e tente novamente.",
                "details": issues,
                "retryable": True,
            },
        },
        ensure_ascii=False,
    )

def tool_error(
    code: str,
    message: str,
    retryable: bool = False,
) -> dict:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable,
        },
    }

logger = logging.getLogger(__name__)


def handle_database_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except PsycopgError:
            logger.exception("Erro ao consultar PostgreSQL")

            return tool_error(
                code="SERVICE_UNAVAILABLE",
                message=(
                    "Não foi possível consultar o sistema no momento. "
                    "Oriente o cliente a tentar novamente."
                ),
            )

    return wrapper