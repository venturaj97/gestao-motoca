from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.lancamento import LancamentoCriar, LancamentoResposta
from app.services.lancamento_service import (
    atualizar_lancamento,
    criar_lancamento,
    excluir_lancamento,
    listar_lancamentos,
)

router = APIRouter(prefix="/lancamentos", tags=["lancamentos"])


def _erros_lancamento_valor(e: ValueError) -> None:
    erros = {
        "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
        "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
        "categoria_inativa": (422, "Categoria esta inativa"),
        "tipo_incompativel_com_categoria": (422, "Tipo do lancamento nao corresponde ao tipo da categoria"),
        "periodo_obrigatorio": (
            422,
            "Para lancamento de GANHO, informe periodo: DIARIO, SEMANAL ou CORRIDA",
        ),
        "periodo_invalido": (422, "periodo invalido"),
        "dados_corrida_obrigatorios": (
            422,
            "Para GANHO por CORRIDA, informe minutos_corrida e km_corrida",
        ),
        "dados_corrida_nao_permitidos": (
            422,
            "minutos_corrida e km_corrida so podem ser informados quando periodo for CORRIDA",
        ),
        "campos_ganho_nao_permitidos_para_despesa": (
            422,
            "Campos de ganho nao sao permitidos quando tipo for DESPESA",
        ),
        "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
        "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto no lancamento"),
        "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
        "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
        "lancamento_nao_encontrado": (404, "Lancamento nao encontrado"),
        "lancamento_vinculado_apenas_despesa": (
            422,
            "Este lancamento esta vinculado a abastecimento ou manutencao: mantenha tipo DESPESA e categoria de despesa",
        ),
    }
    codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
    raise HTTPException(status_code=codigo, detail=detalhe)


@router.post("", response_model=LancamentoResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_lancamento(
    dados: LancamentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return criar_lancamento(db, dados_com_usuario)
    except ValueError as e:
        _erros_lancamento_valor(e)


@router.put("/{lancamento_id}", response_model=LancamentoResposta)
def rota_atualizar_lancamento(
    lancamento_id: int,
    dados: LancamentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return atualizar_lancamento(db, lancamento_id, dados_com_usuario)
    except ValueError as e:
        _erros_lancamento_valor(e)


@router.delete("/{lancamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_lancamento(
    lancamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_lancamento(db, lancamento_id, usuario.id)
    except ValueError as e:
        if str(e) == "lancamento_nao_encontrado":
            raise HTTPException(status_code=404, detail="Lancamento nao encontrado")
        raise HTTPException(status_code=400, detail="Erro desconhecido")


@router.get("", response_model=list[LancamentoResposta])
def rota_listar_lancamentos(
    tipo: Optional[str] = Query(default=None),
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return listar_lancamentos(db, usuario.id, tipo, data_inicio, data_fim)
