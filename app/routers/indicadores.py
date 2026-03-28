from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.routers._errors import raise_mapped_error
from app.schemas.indicador import IndicadorResumoResposta
from app.services.indicador_service import obter_indicadores_resumo

router = APIRouter(prefix="/indicadores", tags=["indicadores"])


@router.get("/resumo", response_model=IndicadorResumoResposta)
def rota_indicadores_resumo(
    tipo: str = Query(..., description="GANHO ou DESPESA"),
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    moto_usuario_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return obter_indicadores_resumo(
            db=db,
            usuario_id=usuario.id,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            moto_usuario_id=moto_usuario_id,
        )
    except ValueError as e:
        erros = {
            "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
            "intervalo_invalido": (422, "data_inicio nao pode ser maior que data_fim"),
        }
        raise_mapped_error(e, erros)
