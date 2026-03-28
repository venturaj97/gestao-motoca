# Gestao Motoca

Sistema de controle financeiro para motoboys.

O objetivo principal e mostrar quanto o entregador realmente ganha no dia, considerando ganhos, despesas e custos da moto.

## Status do projeto

Projeto em construcao.

Esta versao ainda esta evoluindo e pode mudar estrutura de endpoints, regras e modelagem.

## Objetivo do produto

- Registrar ganhos e despesas de forma rapida.
- Relacionar os lancamentos com a moto usada.
- Ajudar no calculo de lucro real.
- Preparar base para relatorios financeiros e de custo por moto.

## Stack atual

- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker / Docker Compose

## O que ja foi implementado

- Estrutura em camadas:
  - `routers`
  - `services`
  - `models`
  - `schemas`
  - `database`
- CRUD de usuarios.
- Modulo de motos:
  - cadastro por catalogo ou manual
  - listagem de motos do usuario
  - campo `ativa` por moto
  - edicao e exclusao de moto (com validacoes de seguranca)
- Categorias (ganho e despesa) com listagem.
- Lancamentos:
  - criacao
  - listagem
  - edicao
  - exclusao
  - validacoes de tipo/categoria
  - regra de moto obrigatoria no fluxo
- Modulo de abastecimentos:
  - criacao e listagem
  - vinculo com lancamento de despesa
- Modulo de manutencoes:
  - criacao e listagem
  - vinculo com lancamento de despesa

## Regras de negocio importantes hoje

- Todo registro financeiro precisa estar ligado a uma moto do usuario.
- Moto nova entra ativa por padrao.
- Se existir mais de uma moto ativa, o usuario deve informar a moto no lancamento.
- Lancamentos vinculados a abastecimento/manutencao seguem como despesa.

## Proximos passos (roadmap)

- Melhorar relatorios e visao de lucro real.
- Fechamento diario.
- Dashboard financeiro.
- Metas e alertas.
- Evolucao para frontend web/mobile.

## Como rodar localmente (resumo)

1. Subir os containers:
   - `docker compose up -d`
2. Iniciar a API FastAPI.
3. Acessar documentacao Swagger:
   - `http://localhost:8000/docs`

## Migrations com Alembic

- Aplicar todas as migrations:
  - `.venv/bin/alembic upgrade head`
- Criar nova migration (apos alterar models):
  - `.venv/bin/alembic revision --autogenerate -m "descricao_da_mudanca"`
- Em banco ja existente que foi criado sem Alembic:
  - `.venv/bin/alembic stamp head`
  - Depois disso, seguir apenas com migrations.

---

Se voce chegou agora no projeto: considere esta base como MVP tecnico em evolucao.
