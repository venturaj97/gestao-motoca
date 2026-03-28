from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.abastecimento import AbastecimentoCriar, AbastecimentoResposta
from app.services.abastecimento_service import (
    atualizar_abastecimento,
    criar_abastecimento,
    excluir_abastecimento,
    listar_abastecimentos,
)


router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])


@router.post("", response_model=AbastecimentoResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_abastecimento(
    dados: AbastecimentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return criar_abastecimento(db, dados_com_usuario)
    except ValueError as e:
        erros = {
            "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            "categoria_inativa": (422, "Categoria esta inativa"),
            "categoria_nao_e_despesa": (422, "Categoria do abastecimento deve ser DESPESA"),
            "litros_invalidos": (422, "Quantidade de litros deve ser maior que zero"),
            "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
            "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto"),
            "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
            "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
        }
        codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
        raise HTTPException(status_code=codigo, detail=detalhe)


@router.get("", response_model=list[AbastecimentoResposta])
def rota_listar_abastecimentos(
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    moto_usuario_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return listar_abastecimentos(
        db,
        usuario_id=usuario.id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        moto_usuario_id=moto_usuario_id,
    )


@router.put("/{abastecimento_id}", response_model=AbastecimentoResposta)
def rota_atualizar_abastecimento(
    abastecimento_id: int,
    dados: AbastecimentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return atualizar_abastecimento(db, abastecimento_id, dados_com_usuario)
    except ValueError as e:
        erros = {
            "abastecimento_nao_encontrado": (404, "Abastecimento nao encontrado"),
            "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            "categoria_inativa": (422, "Categoria esta inativa"),
            "categoria_nao_e_despesa": (422, "Categoria do abastecimento deve ser DESPESA"),
            "litros_invalidos": (422, "Quantidade de litros deve ser maior que zero"),
            "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
            "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto"),
            "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
            "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
            "lancamento_nao_encontrado": (404, "Lancamento nao encontrado"),
            "tipo_incompativel_com_categoria": (422, "Tipo do lancamento nao corresponde ao tipo da categoria"),
        }
        codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
        raise HTTPException(status_code=codigo, detail=detalhe)


@router.delete("/{abastecimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_abastecimento(
    abastecimento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_abastecimento(db, abastecimento_id, usuario.id)
    except ValueError as e:
        if str(e) == "abastecimento_nao_encontrado":
            raise HTTPException(status_code=404, detail="Abastecimento nao encontrado")
        raise HTTPException(status_code=400, detail="Erro desconhecido")
