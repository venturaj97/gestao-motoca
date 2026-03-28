from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.routers._errors import raise_mapped_error
from app.schemas.meta import MetaAlertaResposta, MetaAtualizar, MetaCriar, MetaResposta
from app.services.meta_service import (
    atualizar_meta,
    criar_meta,
    excluir_meta,
    listar_alertas_metas,
    listar_metas,
)

router = APIRouter(prefix="/metas", tags=["metas"])


def _tratar_erro_meta(e: ValueError) -> None:
    erros = {
        "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
        "periodo_invalido": (422, "Periodo deve ser SEMANAL ou MENSAL"),
        "meta_nao_encontrada": (404, "Meta nao encontrada"),
    }
    raise_mapped_error(e, erros)


@router.post("", response_model=MetaResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_meta(
    dados: MetaCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return criar_meta(db, usuario.id, dados)
    except ValueError as e:
        _tratar_erro_meta(e)


@router.get("", response_model=list[MetaResposta])
def rota_listar_metas(
    apenas_ativas: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return listar_metas(db, usuario.id, apenas_ativas)


@router.put("/{meta_id}", response_model=MetaResposta)
def rota_atualizar_meta(
    meta_id: int,
    dados: MetaAtualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return atualizar_meta(db, usuario.id, meta_id, dados)
    except ValueError as e:
        _tratar_erro_meta(e)


@router.delete("/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_meta(
    meta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_meta(db, usuario.id, meta_id)
    except ValueError as e:
        _tratar_erro_meta(e)


@router.get("/alertas", response_model=list[MetaAlertaResposta])
def rota_alertas_meta(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return listar_alertas_metas(db, usuario.id)
