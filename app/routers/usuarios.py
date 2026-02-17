from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.usuario import UsuarioCriar, UsuarioResposta
from app.services.usuario_service import criar_usuario

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db)):
    print("DEBUG ROTA /usuarios FOI CHAMADA")

    try:
        usuario = criar_usuario(db, dados)
        return usuario
    except ValueError as e:
        if str(e) == "email_ja_cadastrado":
            raise HTTPException(status_code=409, detail="Email ja cadastrado")
        if str(e) == "senha_maior_que_72_bytes":
            raise HTTPException(status_code=422, detail="Senha nao pode passar de 72 bytes")
        raise

