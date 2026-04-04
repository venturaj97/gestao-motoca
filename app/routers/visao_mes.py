from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.visao_mes import VisaoMesResposta
from app.services.visao_mes_service import obter_visao_mes, obter_visao_periodo
from app.routers._errors import raise_mapped_error

router = APIRouter(prefix="/visao-mes", tags=["visao-mes"])


@router.get("", response_model=VisaoMesResposta)
def rota_visao_mes(
    ano: Optional[int] = Query(default=None, ge=2000, le=2100),
    mes: Optional[int] = Query(default=None, ge=1, le=12),
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    moto_usuario_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    if data_inicio or data_fim:
        try:
            inicio = data_inicio or data_fim
            fim = data_fim or data_inicio
            return obter_visao_periodo(
                db=db,
                usuario_id=usuario.id,
                data_inicio=inicio,
                data_fim=fim,
                moto_usuario_id=moto_usuario_id,
            )
        except ValueError as error:
            raise_mapped_error(
                error,
                {"intervalo_invalido": (422, "data_inicio nao pode ser maior que data_fim")},
            )

    hoje = date.today()
    return obter_visao_mes(
        db=db,
        usuario_id=usuario.id,
        ano=ano or hoje.year,
        mes=mes or hoje.month,
        moto_usuario_id=moto_usuario_id,
    )
