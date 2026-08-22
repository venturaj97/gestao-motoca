from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ComparativoItem(BaseModel):
    label: str
    valor_atual: Decimal
    valor_anterior: Decimal
    variacao_percentual: Optional[float] = None
    positivo: bool = True


class ComparativoMensal(BaseModel):
    faturamento: ComparativoItem
    despesas: ComparativoItem
    lucro: ComparativoItem


class RankingDiaSemana(BaseModel):
    dia_semana: str
    total: Decimal
    quantidade: int
    percentual: float = 0.0


class DespesaCategoria(BaseModel):
    categoria_nome: str
    total: Decimal
    quantidade: int
    percentual: float = 0.0


class EficienciaCombustivel(BaseModel):
    km_por_litro: Optional[float] = None
    custo_por_km: Optional[float] = None
    total_litros: float = 0.0
    total_gasto_combustivel: Decimal = Decimal("0")
    km_rodados_combustivel: int = 0
    dados_suficientes: bool = False


class InteligenciaResumo(BaseModel):
    ano: int
    mes: int
    comparativo: ComparativoMensal
    ranking_dias_ganho: list[RankingDiaSemana]
    ranking_dias_despesa: list[RankingDiaSemana]
    despesas_por_categoria: list[DespesaCategoria]
    maior_vilao: Optional[DespesaCategoria] = None
    ticket_medio_despesa: Decimal = Decimal("0")
    eficiencia_combustivel: EficienciaCombustivel
    insights: list[str]
