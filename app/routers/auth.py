from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import gerar_token_acesso, gerar_token_refresh, validar_token_refresh
from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.auth import LoginEntrada, RefreshEntrada, TokenResposta, UsuarioLogadoResposta
from app.schemas.recuperacao_senha import AlterarSenhaLogado, RedefinirSenha, SolicitarRecuperacao
from app.services.recuperacao_senha_service import (
    alterar_senha_usuario_logado,
    redefinir_senha_com_codigo,
    solicitar_recuperacao_senha,
)
from app.services.usuario_service import autenticar_usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResposta)
def rota_login(dados: LoginEntrada, db: Session = Depends(get_db)):
    try:
        usuario = autenticar_usuario(db, dados.email, dados.senha)
    except ValueError:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")

    access_token = gerar_token_acesso(usuario.id, usuario.email)
    refresh_token = gerar_token_refresh(usuario.id, usuario.email)
    return TokenResposta(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResposta)
def rota_refresh(dados: RefreshEntrada, db: Session = Depends(get_db)):
    try:
        payload = validar_token_refresh(dados.refresh_token)
        usuario_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token invalido ou expirado")

    usuario = db.execute(select(Usuario).where(Usuario.id == usuario_id)).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")

    novo_access = gerar_token_acesso(usuario.id, usuario.email)
    novo_refresh = gerar_token_refresh(usuario.id, usuario.email)
    return TokenResposta(access_token=novo_access, refresh_token=novo_refresh)


@router.get("/me", response_model=UsuarioLogadoResposta)
def rota_me(usuario: Usuario = Depends(get_usuario_logado)):
    return UsuarioLogadoResposta(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
    )


@router.post("/solicitar-recuperacao")
def rota_solicitar_recuperacao(dados: SolicitarRecuperacao, db: Session = Depends(get_db)):
    solicitar_recuperacao_senha(db, dados.email)
    return {"mensagem": "Se o e-mail estiver cadastrado, o código de recuperação foi enviado."}


@router.post("/redefinir-senha")
def rota_redefinir_senha(dados: RedefinirSenha, db: Session = Depends(get_db)):
    try:
        redefinir_senha_com_codigo(db, dados.email, dados.codigo_pin, dados.nova_senha)
        return {"mensagem": "Senha redefinida com sucesso. Faça login com a nova senha."}
    except ValueError as e:
        erro = str(e)
        if erro == "codigo_invalido_ou_expirado":
            raise HTTPException(status_code=400, detail="Código PIN inválido ou expirado.")
        elif erro == "email_ou_codigo_invalido":
            raise HTTPException(status_code=400, detail="E-mail ou código inválido.")
        raise HTTPException(status_code=400, detail="Falha ao redefinir a senha.")


@router.put("/alterar-senha")
def rota_alterar_senha(
    dados: AlterarSenhaLogado,
    usuario: Usuario = Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        alterar_senha_usuario_logado(db, usuario.id, dados.senha_atual, dados.nova_senha)
        return {"mensagem": "Senha alterada com sucesso."}
    except ValueError as e:
        if str(e) == "senha_atual_incorreta":
            raise HTTPException(status_code=400, detail="Senha atual incorreta.")
        raise HTTPException(status_code=400, detail="Falha ao alterar a senha.")

