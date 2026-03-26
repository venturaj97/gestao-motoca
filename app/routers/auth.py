from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import gerar_token_acesso
from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.auth import LoginEntrada, TokenResposta, UsuarioLogadoResposta
from app.services.usuario_service import autenticar_usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResposta)
def rota_login(dados: LoginEntrada, db: Session = Depends(get_db)):
    try:
        usuario = autenticar_usuario(db, dados.email, dados.senha)
    except ValueError:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")

    token = gerar_token_acesso(usuario.id, usuario.email)
    return TokenResposta(access_token=token)


@router.get("/me", response_model=UsuarioLogadoResposta)
def rota_me(usuario: Usuario = Depends(get_usuario_logado)):
    return UsuarioLogadoResposta(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
    )
