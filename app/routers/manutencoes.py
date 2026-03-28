from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.manutencao import ManutencaoCriar, ManutencaoResposta
from app.services.manutencao_service import (
    atualizar_manutencao,
    criar_manutencao,
    excluir_manutencao,
    listar_manutencoes,
)


router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])


@router.post("", response_model=ManutencaoResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_manutencao(
    dados: ManutencaoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return criar_manutencao(db, dados_com_usuario)
    except ValueError as e:
        erros = {
            "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            "categoria_inativa": (422, "Categoria esta inativa"),
            "categoria_nao_e_despesa": (422, "Categoria da manutencao deve ser DESPESA"),
            "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
            "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto"),
            "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
            "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
        }
        codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
        raise HTTPException(status_code=codigo, detail=detalhe)


@router.get("", response_model=list[ManutencaoResposta])
def rota_listar_manutencoes(
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    moto_usuario_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return listar_manutencoes(
        db,
        usuario_id=usuario.id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        moto_usuario_id=moto_usuario_id,
    )


@router.put("/{manutencao_id}", response_model=ManutencaoResposta)
def rota_atualizar_manutencao(
    manutencao_id: int,
    dados: ManutencaoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return atualizar_manutencao(db, manutencao_id, dados_com_usuario)
    except ValueError as e:
        erros = {
            "manutencao_nao_encontrada": (404, "Manutencao nao encontrada"),
            "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            "categoria_inativa": (422, "Categoria esta inativa"),
            "categoria_nao_e_despesa": (422, "Categoria da manutencao deve ser DESPESA"),
            "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
            "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto"),
            "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
            "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
            "lancamento_nao_encontrado": (404, "Lancamento nao encontrado"),
            "tipo_incompativel_com_categoria": (422, "Tipo do lancamento nao corresponde ao tipo da categoria"),
        }
        codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
        raise HTTPException(status_code=codigo, detail=detalhe)


@router.delete("/{manutencao_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_manutencao(
    manutencao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_manutencao(db, manutencao_id, usuario.id)
    except ValueError as e:
        if str(e) == "manutencao_nao_encontrada":
            raise HTTPException(status_code=404, detail="Manutencao nao encontrada")
        raise HTTPException(status_code=400, detail="Erro desconhecido")
