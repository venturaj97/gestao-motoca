from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.lancamento import Lancamento
from app.schemas.categoria import CategoriaCriar, CategoriaAtualizar

TIPOS_VALIDOS = {"GANHO", "DESPESA"}
GRUPOS_DESPESA_VALIDOS = {"GERAL", "MANUTENCAO", "ABASTECIMENTO", "IMPOSTO"}

CATEGORIAS_PADRAO = [
    {"nome": "Entregas (App)", "tipo": "GANHO", "grupo_despesa": None},
    {"nome": "Entregas Particulares", "tipo": "GANHO", "grupo_despesa": None},
    {"nome": "Outros Ganhos", "tipo": "GANHO", "grupo_despesa": None},
    {"nome": "Almoco", "tipo": "DESPESA", "grupo_despesa": "GERAL"},
    {"nome": "Cafe", "tipo": "DESPESA", "grupo_despesa": "GERAL"},
    {"nome": "Combustivel", "tipo": "DESPESA", "grupo_despesa": "ABASTECIMENTO"},
    {"nome": "Troca de Oleo", "tipo": "DESPESA", "grupo_despesa": "MANUTENCAO"},
    {"nome": "Relacao", "tipo": "DESPESA", "grupo_despesa": "MANUTENCAO"},
    {"nome": "Pecas / Equipamentos", "tipo": "DESPESA", "grupo_despesa": "MANUTENCAO"},
    {"nome": "Financiamento", "tipo": "DESPESA", "grupo_despesa": "IMPOSTO"},
    {"nome": "Seguro da Moto", "tipo": "DESPESA", "grupo_despesa": "IMPOSTO"},
    {"nome": "IPVA", "tipo": "DESPESA", "grupo_despesa": "IMPOSTO"},
    {"nome": "Multas", "tipo": "DESPESA", "grupo_despesa": "IMPOSTO"},
]


def _normalizar_tipo(valor: str) -> str:
    tipo = valor.upper().strip()
    if tipo not in TIPOS_VALIDOS:
        raise ValueError("tipo_invalido")
    return tipo


def _normalizar_grupo_despesa(tipo: str, grupo_despesa: str | None) -> str | None:
    if tipo == "GANHO":
        if grupo_despesa is not None:
            raise ValueError("grupo_despesa_nao_permitido_para_ganho")
        return None

    if grupo_despesa is None:
        raise ValueError("grupo_despesa_obrigatorio")

    grupo = grupo_despesa.upper().strip()
    if grupo not in GRUPOS_DESPESA_VALIDOS:
        raise ValueError("grupo_despesa_invalido")
    return grupo


def garantir_categorias_iniciais_usuario(db: Session, usuario_id: int) -> None:
    existentes = db.execute(
        select(Categoria.nome, Categoria.tipo).where(Categoria.usuario_id == usuario_id)
    ).all()
    chave_existente = {(nome, tipo) for nome, tipo in existentes}

    for cat in CATEGORIAS_PADRAO:
        chave = (cat["nome"], cat["tipo"])
        if chave in chave_existente:
            continue
        db.add(
            Categoria(
                usuario_id=usuario_id,
                nome=cat["nome"],
                tipo=cat["tipo"],
                grupo_despesa=cat["grupo_despesa"],
            )
        )


def listar_categorias(db: Session, usuario_id: int):
    categorias_usuario = db.execute(
        select(Categoria)
        .where(
            Categoria.usuario_id == usuario_id,
            Categoria.ativo == True,  # noqa: E712
        )
        .order_by(Categoria.tipo, Categoria.nome)
    ).scalars().all()

    if categorias_usuario:
        return categorias_usuario

    garantir_categorias_iniciais_usuario(db, usuario_id)
    db.commit()

    return db.execute(
        select(Categoria)
        .where(
            Categoria.usuario_id == usuario_id,
            Categoria.ativo == True,  # noqa: E712
        )
        .order_by(Categoria.tipo, Categoria.nome)
    ).scalars().all()


def criar_categoria(db: Session, usuario_id: int, dados: CategoriaCriar) -> Categoria:
    tipo = _normalizar_tipo(dados.tipo)
    grupo_despesa = _normalizar_grupo_despesa(tipo, dados.grupo_despesa)

    existe = db.execute(
        select(Categoria).where(
            Categoria.usuario_id == usuario_id,
            Categoria.nome == dados.nome,
            Categoria.tipo == tipo,
        )
    ).scalar_one_or_none()

    if existe:
        raise ValueError("categoria_ja_existe")

    categoria = Categoria(
        usuario_id=usuario_id,
        nome=dados.nome,
        tipo=tipo,
        grupo_despesa=grupo_despesa,
    )

    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def atualizar_categoria(db: Session, usuario_id: int, categoria_id: int, dados: CategoriaAtualizar) -> Categoria:
    categoria = db.execute(
        select(Categoria).where(
            Categoria.id == categoria_id,
            Categoria.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not categoria:
        raise ValueError("categoria_nao_encontrada")

    novo_nome = categoria.nome
    if dados.nome is not None:
        novo_nome = dados.nome.strip()
        if not novo_nome:
            raise ValueError("nome_obrigatorio")

    novo_grupo = categoria.grupo_despesa
    if dados.grupo_despesa is not None:
        novo_grupo = _normalizar_grupo_despesa(categoria.tipo, dados.grupo_despesa)
    elif categoria.tipo == "DESPESA" and novo_grupo is None:
        raise ValueError("grupo_despesa_obrigatorio")

    conflito = db.execute(
        select(Categoria).where(
            Categoria.usuario_id == usuario_id,
            Categoria.nome == novo_nome,
            Categoria.tipo == categoria.tipo,
            Categoria.id != categoria.id,
        )
    ).scalar_one_or_none()
    if conflito:
        raise ValueError("categoria_ja_existe")

    categoria.nome = novo_nome
    categoria.grupo_despesa = novo_grupo
    if dados.ativo is not None:
        categoria.ativo = dados.ativo

    db.commit()
    db.refresh(categoria)
    return categoria


def excluir_categoria(db: Session, usuario_id: int, categoria_id: int) -> None:
    categoria = db.execute(
        select(Categoria).where(
            Categoria.id == categoria_id,
            Categoria.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not categoria:
        raise ValueError("categoria_nao_encontrada")

    uso = db.execute(
        select(Lancamento.id).where(
            Lancamento.usuario_id == usuario_id,
            Lancamento.categoria_id == categoria_id,
        ).limit(1)
    ).scalar_one_or_none()

    if uso is not None:
        # Exclusao logica para preservar historico
        categoria.ativo = False
        db.commit()
        return

    db.delete(categoria)
    db.commit()
