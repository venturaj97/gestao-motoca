from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.moto_modelo import MotoModelo
from app.models.moto_usuario import MotoUsuario
from app.models.moto_versao import MotoVersao
from app.schemas.moto import MotoUsuarioCriar


def criar_moto_usuario(db: Session, dados: MotoUsuarioCriar) -> MotoUsuario:

    # valida se escolheu versao existente
    if dados.moto_versao_id:
        versao = db.execute(
            select(MotoVersao).where(MotoVersao.id == dados.moto_versao_id)
        ).scalar_one_or_none()

        if not versao:
            raise ValueError("versao_nao_encontrada")

    moto = MotoUsuario(
        usuario_id=dados.usuario_id,
        moto_versao_id=dados.moto_versao_id,
        marca_manual=dados.marca_manual,
        modelo_manual=dados.modelo_manual,
        ano_manual=dados.ano_manual,
        km_atual=dados.km_atual,
        cor=dados.cor,
    )

    db.add(moto)
    db.commit()
    db.refresh(moto)

    return moto


def listar_motos_do_usuario(db: Session, usuario_id: int):
    stmt = (
        select(MotoUsuario, MotoVersao, MotoModelo)
        .outerjoin(MotoVersao, MotoUsuario.moto_versao_id == MotoVersao.id)
        .outerjoin(MotoModelo, MotoVersao.moto_modelo_id == MotoModelo.id)
        .where(MotoUsuario.usuario_id == usuario_id)
        .order_by(MotoUsuario.id.desc())
    )

    rows = db.execute(stmt).all()

    resultado = []
    for moto_usuario, versao, modelo in rows:
        if versao and modelo:
            resultado.append({
                "id": moto_usuario.id,
                "usuario_id": moto_usuario.usuario_id,
                "origem": "catalogo",
                "marca": modelo.marca,
                "modelo": modelo.modelo,
                "ano": versao.ano,
                "moto_versao_id": moto_usuario.moto_versao_id,
                "km_atual": moto_usuario.km_atual,
                "cor": moto_usuario.cor,
            })
        else:
            resultado.append({
                "id": moto_usuario.id,
                "usuario_id": moto_usuario.usuario_id,
                "origem": "manual",
                "marca": moto_usuario.marca_manual,
                "modelo": moto_usuario.modelo_manual,
                "ano": moto_usuario.ano_manual,
                "moto_versao_id": None,
                "km_atual": moto_usuario.km_atual,
                "cor": moto_usuario.cor,
            })

    return resultado