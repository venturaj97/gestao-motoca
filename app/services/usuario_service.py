from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCriar
from app.core.security import gerar_hash_senha


def criar_usuario(db: Session, dados: UsuarioCriar) -> Usuario:
    # valida email unico
    existe = db.execute(select(Usuario).where(Usuario.email == dados.email)).scalar_one_or_none()
    if existe:
        raise ValueError("email_ja_cadastrado")

    print("DEBUG senha:", repr(dados.senha))
    print("DEBUG len chars:", len(dados.senha))
    print("DEBUG len bytes:", len(dados.senha.encode("utf-8")))

    senha_bytes = dados.senha.encode("utf-8")
    if len(senha_bytes) > 72:
        raise ValueError("senha_maior_que_72_bytes")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=gerar_hash_senha(dados.senha),
    )
    
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
