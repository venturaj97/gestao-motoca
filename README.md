# Gestão Motoca

Sistema de controle financeiro para motoboys e entregadores de aplicativo.

O sistema permite o registro e acompanhamento de ganhos, despesas, abastecimentos, manutenções e histórico de quilometragem para cálculo do lucro real do entregador.

---

## Funcionalidades Principais

- Dashboard consolidado com saldo do dia e indicadores de desempenho.
- Central de Histórico em 2 abas: Extrato de Transações e Relatórios com Inteligência.
- Lançamento de ganhos por corrida ou fechamento diário.
- Lançamento de despesas categorizadas (alimentação, manutenção, combustível, impostos).
- Controle de abastecimentos e cálculo de eficiência (KM/L e custo por KM).
- Registro de manutenções com odômetro e alertas de troca preventiva de óleo.
- Gerenciamento de veículos vinculados ao usuário.

---

## Tecnologias Utilizadas

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Pytest.
- **Frontend:** Vue 3 (Composition API), TypeScript, Pinia, Vue Router, Tailwind CSS, Vite.
- **Banco de Dados:** PostgreSQL 16.
- **Infraestrutura:** Docker e Docker Compose.

---

## Como Executar

### Pré-requisitos
- Docker e Docker Compose
- Node.js 18+

### 1. Configurar o ambiente
```bash
git clone https://github.com/venturaj97/gestao-motoca.git
cd gestao-motoca
cp .env.example .env
```

### 2. Iniciar os serviços backend e banco de dados
```bash
docker compose up --build -d
```

### 3. Executar as migrações do banco
```bash
docker compose exec api alembic upgrade head
```

### 4. Iniciar o servidor frontend
```bash
cd frontend
npm install
npm run dev
```

### URLs de Acesso
- **Aplicação Frontend:** http://localhost:5173
- **API Backend:** http://localhost:8000
- **Documentação Swagger:** http://localhost:8000/docs

---

## Estrutura do Projeto

```text
gestao-motoca/
├── app/                    # Backend FastAPI (models, schemas, services, routers)
├── frontend/               # Frontend Vue 3 + TypeScript
├── alembic/                # Migrações do banco de dados
├── tests/                  # Testes automatizados com Pytest
├── docker-compose.yml      # Configuração de contêineres
├── Dockerfile              # Imagem do serviço backend
└── README.md
```

---

## Variáveis de Ambiente

As configurações são definidas no arquivo `.env`:

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `DB_HOST` | Sim | Host do banco PostgreSQL |
| `DB_PORT` | Sim | Porta do banco (padrão: 5432) |
| `DB_NAME` | Sim | Nome do banco de dados |
| `DB_USER` | Sim | Usuário do banco |
| `DB_PASSWORD` | Sim | Senha do banco |
| `AUTH_SECRET_KEY` | Sim | Chave secreta para assinatura dos tokens JWT |
| `CORS_ORIGINS` | Não | Origens autorizadas para requisições cross-origin |

---

## Execução dos Testes

Para executar os testes do backend:

```bash
docker compose exec api pytest -v
```

---

## Licença e Propriedade

Copyright (c) 2026 Gestão Motoca. Todos os direitos reservados.

Este software é um sistema proprietário. A cópia, distribuição, modificação ou uso comercial não autorizado deste código são estritamente proibidos.
