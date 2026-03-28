from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.routers._errors import raise_mapped_error
from app.schemas.usuario import UsuarioCriar, UsuarioResposta
from app.services.usuario_service import criar_usuario

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db)):
    try:
        usuario = criar_usuario(db, dados)
        return usuario
    except ValueError as e:
        raise_mapped_error(
            e,
            {
                "email_ja_cadastrado": (409, "Email ja cadastrado"),
                "senha_maior_que_72_bytes": (422, "Senha nao pode passar de 72 bytes"),
            },
        )
