from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.manutencao import ManutencaoCriar, ManutencaoResposta
from app.services.manutencao_service import criar_manutencao, listar_manutencoes


router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])


@router.post("", response_model=ManutencaoResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_manutencao(dados: ManutencaoCriar, db: Session = Depends(get_db)):
    try:
        return criar_manutencao(db, dados)
    except ValueError as e:
        erros = {
            "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            "categoria_inativa": (422, "Categoria esta inativa"),
            "categoria_nao_e_despesa": (422, "Categoria da manutencao deve ser DESPESA"),
        }
        codigo, detalhe = erros.get(str(e), (400, "Erro desconhecido"))
        raise HTTPException(status_code=codigo, detail=detalhe)


@router.get("", response_model=list[ManutencaoResposta])
def rota_listar_manutencoes(
    usuario_id: int = Query(..., ge=1),
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    moto_usuario_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    return listar_manutencoes(
        db,
        usuario_id=usuario_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        moto_usuario_id=moto_usuario_id,
    )

