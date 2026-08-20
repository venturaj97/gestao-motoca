from datetime import datetime, timedelta, timezone
import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.email_service import enviar_email_codigo_recuperacao
from app.core.security import gerar_hash_senha, verificar_senha
from app.models.recuperacao_senha import RecuperacaoSenha
from app.models.usuario import Usuario


def solicitar_recuperacao_senha(db: Session, email: str) -> None:
    usuario = db.execute(
        select(Usuario).where(Usuario.email == email.strip().lower())
    ).scalar_one_or_none()

    if not usuario:
        # Retorna silenciosamente por segurança (evita enumeração de e-mails)
        return

    # Invalida requisições anteriores não utilizadas
    anteriores = db.execute(
        select(RecuperacaoSenha).where(
            RecuperacaoSenha.usuario_id == usuario.id,
            RecuperacaoSenha.usado == False,  # noqa: E712
        )
    ).scalars().all()
    for ant in anteriores:
        ant.usado = True

    # Gera PIN numérico aleatório de 6 dígitos
    codigo_pin = f"{random.randint(100000, 999999)}"
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=15)

    recuperacao = RecuperacaoSenha(
        usuario_id=usuario.id,
        codigo_pin=codigo_pin,
        expira_em=expira_em,
        usado=False,
    )
    db.add(recuperacao)
    db.commit()

    # Envia e-mail com o código PIN
    enviar_email_codigo_recuperacao(usuario.email, codigo_pin)


def redefinir_senha_com_codigo(db: Session, email: str, codigo_pin: str, nova_senha: str) -> None:
    usuario = db.execute(
        select(Usuario).where(Usuario.email == email.strip().lower())
    ).scalar_one_or_none()

    if not usuario:
        raise ValueError("email_ou_codigo_invalido")

    agora = datetime.now(timezone.utc)
    recuperacao = db.execute(
        select(RecuperacaoSenha).where(
            RecuperacaoSenha.usuario_id == usuario.id,
            RecuperacaoSenha.codigo_pin == codigo_pin.strip(),
            RecuperacaoSenha.usado == False,  # noqa: E712
            RecuperacaoSenha.expira_em >= agora,
        )
    ).scalar_one_or_none()

    if not recuperacao:
        raise ValueError("codigo_invalido_ou_expirado")

    # Atualiza a senha do usuário e confirma o e-mail automaticamente
    usuario.senha = gerar_hash_senha(nova_senha)
    usuario.email_confirmado = True
    recuperacao.usado = True
    db.commit()


def alterar_senha_usuario_logado(
    db: Session, usuario_id: int, senha_atual: str, nova_senha: str
) -> None:
    usuario = db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    ).scalar_one_or_none()

    if not usuario:
        raise ValueError("usuario_nao_encontrado")

    if not verificar_senha(senha_atual, usuario.senha):
        raise ValueError("senha_atual_incorreta")

    usuario.senha = gerar_hash_senha(nova_senha)
    db.commit()


def enviar_codigo_confirmacao_email(db: Session, usuario: Usuario) -> None:
    # Invalida requisições anteriores não utilizadas
    anteriores = db.execute(
        select(RecuperacaoSenha).where(
            RecuperacaoSenha.usuario_id == usuario.id,
            RecuperacaoSenha.usado == False,  # noqa: E712
        )
    ).scalars().all()
    for ant in anteriores:
        ant.usado = True

    codigo_pin = f"{random.randint(100000, 999999)}"
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=15)

    recuperacao = RecuperacaoSenha(
        usuario_id=usuario.id,
        codigo_pin=codigo_pin,
        expira_em=expira_em,
        usado=False,
    )
    db.add(recuperacao)
    db.commit()

    # Reutiliza o serviço de e-mail enviando o PIN
    enviar_email_codigo_recuperacao(usuario.email, codigo_pin)


def confirmar_email_usuario(db: Session, usuario: Usuario, codigo_pin: str) -> None:
    agora = datetime.now(timezone.utc)
    recuperacao = db.execute(
        select(RecuperacaoSenha).where(
            RecuperacaoSenha.usuario_id == usuario.id,
            RecuperacaoSenha.codigo_pin == codigo_pin.strip(),
            RecuperacaoSenha.usado == False,  # noqa: E712
            RecuperacaoSenha.expira_em >= agora,
        )
    ).scalar_one_or_none()

    if not recuperacao:
        raise ValueError("codigo_invalido_ou_expirado")

    usuario.email_confirmado = True
    recuperacao.usado = True
    db.commit()
