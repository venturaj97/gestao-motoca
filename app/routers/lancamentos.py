from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.lancamento import LancamentoCriar, LancamentoResposta
from app.services.lancamento_service import criar_lancamento, listar_lancamentos

router = APIRouter(prefix="/lancamentos", tags=["lancamentos"])


@router.post("", response_model=LancamentoResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_lancamento(dados: LancamentoCriar, db: Session = Depends(get_db)):
    try:
        return criar_lancamento(db, dados)
    except ValueError as e:
        erros = {
            "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
            "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            "categoria_inativa": (422, "Categoria esta inativa"),
            "tipo_incompativel_com_categoria": (422, "Tipo do lancamento nao corresponde ao tipo da categoria"),
            "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
            "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto no lancamento"),
            "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
            "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
        }
        codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
        raise HTTPException(status_code=codigo, detail=detalhe)


@router.get("", response_model=list[LancamentoResposta])
def rota_listar_lancamentos(
    usuario_id: int = Query(..., ge=1),
    tipo: Optional[str] = Query(default=None),
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    return listar_lancamentos(db, usuario_id, tipo, data_inicio, data_fim)
