from sqlalchemy.orm import Session
from sqlalchemy import select, distinct

from app.models.moto_modelo import MotoModelo
from app.models.moto_usuario import MotoUsuario
from app.models.moto_versao import MotoVersao
from app.schemas.moto import MotoUsuarioAtivaAlterar, MotoUsuarioCriar


def listar_marcas(db: Session) -> list[str]:
    marcas = db.execute(
        select(distinct(MotoModelo.marca)).where(MotoModelo.ativo == True)  # noqa: E712
    ).scalars().all()
    return sorted(marcas)


def listar_modelos_por_marca(db: Session, marca: str) -> list[dict]:
    modelos = db.execute(
        select(MotoModelo)
        .where(MotoModelo.ativo == True)  # noqa: E712
        .where(MotoModelo.marca.ilike(marca))
        .order_by(MotoModelo.modelo)
    ).scalars().all()
    return [{"id": m.id, "marca": m.marca, "modelo": m.modelo, "cilindrada_cc": m.cilindrada_cc} for m in modelos]


def listar_anos_por_modelo(db: Session, modelo_id: int) -> list[int]:
    return db.execute(
        select(MotoVersao.ano)
        .where(MotoVersao.moto_modelo_id == modelo_id)
        .where(MotoVersao.ativo == True)  # noqa: E712
        .order_by(MotoVersao.ano.desc())
    ).scalars().all()



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
        ativa=True,
    )

    db.add(moto)
    db.commit()
    db.refresh(moto)

    return moto


def alterar_ativa_moto_usuario(db: Session, dados: MotoUsuarioAtivaAlterar) -> MotoUsuario:
    moto = db.execute(
        select(MotoUsuario).where(
            MotoUsuario.id == dados.moto_usuario_id,
            MotoUsuario.usuario_id == dados.usuario_id,
        )
    ).scalar_one_or_none()
    if not moto:
        raise ValueError("moto_nao_encontrada_ou_nao_sua")

    moto.ativa = dados.ativa
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
                "ativa": moto_usuario.ativa,
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
                "ativa": moto_usuario.ativa,
            })

    return resultado