from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import validar_token_acesso
from app.database.session import get_db
from app.models.usuario import Usuario

auth_scheme = HTTPBearer(auto_error=True)


def get_usuario_logado(
    credenciais: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    token = credenciais.credentials

    try:
        payload = validar_token_acesso(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    sub = payload.get("sub")
    try:
        usuario_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    usuario = db.execute(select(Usuario).where(Usuario.id == usuario_id)).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")

    return usuario


def _usuario_eh_pro(usuario: Usuario) -> bool:
    """Verifica se o usuario tem acesso PRO (plano ativo ou trial de 7 dias)."""
    if usuario.plano == "PRO":
        if usuario.plano_expira_em is None:
            return True
        return usuario.plano_expira_em > datetime.now(timezone.utc)

    # Trial: 7 dias após o cadastro
    if usuario.data_criacao:
        dias_desde_cadastro = (datetime.now(timezone.utc) - usuario.data_criacao.replace(tzinfo=timezone.utc if usuario.data_criacao.tzinfo is None else usuario.data_criacao.tzinfo)).days
        if dias_desde_cadastro <= 7:
            return True

    return False


def requer_plano_pro(
    usuario: Usuario = Depends(get_usuario_logado),
) -> Usuario:
    """Dependency que bloqueia acesso se o usuario nao for PRO."""
    if not _usuario_eh_pro(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recurso exclusivo do plano PRO. Assine para desbloquear.",
        )
    return usuario

