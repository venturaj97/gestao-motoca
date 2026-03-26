from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCriar
from app.core.security import gerar_hash_senha, verificar_senha


def criar_usuario(db: Session, dados: UsuarioCriar) -> Usuario:
    email_normalizado = dados.email.lower()

    # valida email unico
    existe = db.execute(select(Usuario).where(Usuario.email == email_normalizado)).scalar_one_or_none()
    if existe:
        raise ValueError("email_ja_cadastrado")

    senha_bytes = dados.senha.encode("utf-8")
    if len(senha_bytes) > 72:
        raise ValueError("senha_maior_que_72_bytes")

    usuario = Usuario(
        nome=dados.nome,
        email=email_normalizado,
        senha=gerar_hash_senha(dados.senha),
    )
    
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, senha: str) -> Usuario:
    email_normalizado = email.lower()
    usuario = db.execute(
        select(Usuario).where(Usuario.email == email_normalizado)
    ).scalar_one_or_none()

    if not usuario:
        raise ValueError("credenciais_invalidas")

    if not verificar_senha(senha, usuario.senha):
        raise ValueError("credenciais_invalidas")

    return usuario
