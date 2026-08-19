from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    if not isinstance(senha, str):
        senha = str(senha)

    b = senha.encode("utf-8")

    if len(b) > 72:
        raise ValueError("senha_maior_que_72_bytes")

    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def gerar_token_acesso(usuario_id: int, email: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_token_exp_minutos)
    payload: dict[str, Any] = {
        "sub": str(usuario_id),
        "email": email,
        "type": "access",
        "exp": exp,
    }
    return jwt.encode(payload, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def gerar_token_refresh(usuario_id: int, email: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=settings.auth_refresh_token_exp_dias)
    payload: dict[str, Any] = {
        "sub": str(usuario_id),
        "email": email,
        "type": "refresh",
        "exp": exp,
    }
    return jwt.encode(payload, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def validar_token_acesso(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    if payload.get("type") and payload.get("type") != "access":
        raise ValueError("token_tipo_invalido")
    return payload


def validar_token_refresh(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    if payload.get("type") != "refresh":
        raise ValueError("token_nao_e_refresh")
    return payload
