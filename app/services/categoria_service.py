from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCriar


def listar_categorias(db: Session):
    return db.execute(
        select(Categoria)
        .where(Categoria.ativo == True)  # noqa: E712
        .order_by(Categoria.tipo, Categoria.nome)
    ).scalars().all()


def criar_categoria(db: Session, dados: CategoriaCriar) -> Categoria:
    tipo = dados.tipo.upper()

    if tipo not in ["GANHO", "DESPESA"]:
        raise ValueError("tipo_invalido")

    existe = db.execute(
        select(Categoria).where(
            Categoria.nome == dados.nome,
            Categoria.tipo == tipo
        )
    ).scalar_one_or_none()

    if existe:
        raise ValueError("categoria_ja_existe")

    categoria = Categoria(
        nome=dados.nome,
        tipo=tipo
    )

    db.add(categoria)
    db.commit()
    db.refresh(categoria)

    return categoria