from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.visao_mes import VisaoMesResposta
from app.services.visao_mes_service import obter_visao_mes

router = APIRouter(prefix="/visao-mes", tags=["visao-mes"])


@router.get("", response_model=VisaoMesResposta)
def rota_visao_mes(
    ano: Optional[int] = Query(default=None, ge=2000, le=2100),
    mes: Optional[int] = Query(default=None, ge=1, le=12),
    moto_usuario_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    hoje = date.today()
    return obter_visao_mes(
        db=db,
        usuario_id=usuario.id,
        ano=ano or hoje.year,
        mes=mes or hoje.month,
        moto_usuario_id=moto_usuario_id,
    )
