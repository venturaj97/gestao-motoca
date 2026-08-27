from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.cofre import CofreCriar, CofreAtualizar, CofreAporte, CofreResposta
from app.services.cofre_service import (
    listar_cofres,
    criar_cofre,
    atualizar_cofre,
    aportar_saldo_cofre,
    excluir_cofre,
)

router = APIRouter(prefix="/cofres", tags=["Cofres"])


@router.get("", response_model=list[CofreResposta])
def api_listar_cofres(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado),
):
    return listar_cofres(db, usuario_atual.id)


@router.post("", response_model=CofreResposta, status_code=status.HTTP_201_CREATED)
def api_criar_cofre(
    dados: CofreCriar,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado),
):
    try:
        return criar_cofre(db, usuario_atual.id, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{cofre_id}", response_model=CofreResposta)
def api_atualizar_cofre(
    cofre_id: int,
    dados: CofreAtualizar,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado),
):
    try:
        return atualizar_cofre(db, cofre_id, usuario_atual.id, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{cofre_id}/aporte", response_model=CofreResposta)
def api_aportar_cofre(
    cofre_id: int,
    dados: CofreAporte,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado),
):
    try:
        return aportar_saldo_cofre(db, cofre_id, usuario_atual.id, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{cofre_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_excluir_cofre(
    cofre_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_cofre(db, cofre_id, usuario_atual.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
