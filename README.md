# 🏍️ Gestão Motoca

Sistema de controle financeiro para motoboys e entregadores.

O projeto ajuda o entregador a registrar ganhos, despesas, abastecimentos e manutenções para entender melhor o **lucro real** do trabalho com a moto.

---

## ✨ Funcionalidades

- **📊 Dashboard** — Visão consolidada do mês com saldo, indicadores e resumo executivo
- **💰 Lançamentos** — Registro de ganhos (diário/corrida) e despesas com categorização
- **⛽ Abastecimentos** — Controle de litros, valor/litro, posto e tipo de combustível
- **🔧 Manutenções** — Registro de serviços, oficina e quilometragem
- **🏍️ Gestão de Motos** — Cadastro por catálogo, placa (API WDAPI) ou manual
- **📁 Categorias** — Categorias personalizadas de ganho/despesa por grupo
- **📈 Indicadores** — Ticket médio, melhor/pior dia da semana, gráfico por dia
- **🎯 Metas** — Metas de ganho/despesa por período (backend pronto, frontend em construção)
- **🔐 Auth** — Cadastro, login com JWT e proteção de rotas
- **🌙 Tema** — Suporte a modo claro/escuro

---

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Python 3.12 · FastAPI · SQLAlchemy · Alembic · Pydantic v2 |
| **Frontend** | Vue 3 · TypeScript · Pinia · Vue Router · Tailwind CSS · Vite |
| **Banco** | PostgreSQL 16 |
| **Infra** | Docker · Docker Compose |
| **Auth** | JWT (python-jose) · bcrypt (passlib) |
| **Testes** | Pytest |

---

## 🚀 Quick Start

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- [Node.js](https://nodejs.org/) 18+

### 1. Clone e configure

```bash
git clone https://github.com/venturaj97/gestao-motoca.git
cd gestao-motoca
cp .env.example .env
# Edite o .env e configure AUTH_SECRET_KEY com uma chave forte
```

### 2. Suba o backend + banco

```bash
docker compose up --build
```

### 3. Rode as migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. (Opcional) Popule o catálogo de motos

```bash
docker compose exec db psql -U motoca -d gestao_motoca -f /app/seed_motos.sql
```

### 5. Suba o frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Acesse

| Serviço | URL |
|---------|-----|
| **App (frontend)** | http://localhost:5173 |
| **API (backend)** | http://localhost:8000 |
| **Swagger UI** | http://localhost:8000/docs |

---

## 📂 Estrutura do Projeto

```
gestao-motoca/
├── app/                    # Backend FastAPI
│   ├── core/               #   Configurações e segurança
│   ├── database/           #   Sessão do banco
│   ├── models/             #   Modelos SQLAlchemy (10 tabelas)
│   ├── schemas/            #   Schemas Pydantic
│   ├── services/           #   Lógica de negócio
│   ├── routers/            #   Endpoints da API
│   ├── dependencies.py     #   Auth dependency
│   └── main.py             #   App FastAPI
├── frontend/               # Frontend Vue 3
│   └── src/
│       ├── api/            #   Módulos HTTP (axios)
│       ├── components/     #   Componentes reutilizáveis
│       ├── router/         #   Vue Router + guards
│       ├── stores/         #   Pinia stores
│       ├── types/          #   Interfaces TypeScript
│       └── views/          #   Páginas
├── alembic/                # Migrations do banco
├── tests/                  # Testes pytest
├── docker-compose.yml      # Infra de desenvolvimento
├── Dockerfile              # Imagem da API
├── requirements.txt        # Dependências Python
└── DOCUMENTACAO.md         # Documentação técnica completa
```

---

## 🔌 API — Endpoints Principais

| Módulo | Prefix | Operações |
|--------|--------|-----------|
| Auth | `/auth` | Login, dados do usuário |
| Usuários | `/usuarios` | Cadastro |
| Motos | `/motos` | CRUD, consulta placa, catálogo |
| Categorias | `/categorias` | CRUD |
| Lançamentos | `/lancamentos` | CRUD, criação em lote |
| Abastecimentos | `/abastecimentos` | CRUD |
| Manutenções | `/manutencoes` | CRUD |
| Indicadores | `/indicadores` | Resumo analítico |
| Metas | `/metas` | CRUD, alertas |
| Visão do Mês | `/visao-mes` | Dashboard consolidado |

> Documentação interativa completa em `/docs` (Swagger UI).

---

## 🧪 Testes

```bash
# Com o banco rodando (docker compose up)
pytest -v
```

| Arquivo | Cobertura |
|---------|-----------|
| `test_fluxo_principal.py` | Fluxo completo: cadastro → login → moto → lançamentos |
| `test_meta_visao_mes.py` | Metas, alertas e visão do mês |
| `test_api_endpoints.py` | Testes HTTP dos endpoints |

---

## ⚙️ Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

| Variável | Obrigatória | Descrição |
|----------|:-----------:|-----------|
| `DB_HOST` | ✅ | Host do PostgreSQL |
| `DB_PORT` | ✅ | Porta do PostgreSQL |
| `DB_NAME` | ✅ | Nome do banco |
| `DB_USER` | ✅ | Usuário do banco |
| `DB_PASSWORD` | ✅ | Senha do banco |
| `AUTH_SECRET_KEY` | ✅ | Chave secreta para JWT |
| `WDAPI_TOKEN` | ❌ | Token para consulta de placa |
| `CORS_ORIGINS` | ❌ | Origens CORS permitidas |

---

## 📖 Documentação

Veja [DOCUMENTACAO.md](DOCUMENTACAO.md) para a documentação técnica completa com:
- Detalhes de todos os módulos e regras de negócio
- Referência completa de endpoints da API
- Diagrama ER do banco de dados
- Fluxo de autenticação e navegação
- Variáveis de ambiente detalhadas

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
