# Documentacao do Projeto

## Visao geral

Gestao Motoca e um sistema para ajudar motoboys a controlar ganhos, despesas, moto, abastecimentos, manutencoes e indicadores financeiros.

O foco do produto e mostrar o lucro real do trabalho, considerando o dinheiro que entra e os custos ligados a moto.

## Modulos principais

- Autenticacao e usuarios.
- Cadastro e selecao de moto.
- Consulta de placa via WDAPI.
- Categorias de ganho e despesa.
- Lancamentos financeiros.
- Abastecimentos.
- Manutencoes.
- Indicadores e visao mensal.
- Metas, que futuramente devem evoluir para o Cofre.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic e PostgreSQL.
- Frontend: Vue 3, Pinia, Vue Router, Tailwind CSS e Vite.
- Infra local: Docker e Docker Compose.
- Testes: Pytest e FastAPI TestClient.

## Como rodar em desenvolvimento

1. Copie `.env.example` para `.env` e ajuste as variaveis.
2. Suba banco e API:

```bash
docker compose up --build
```

3. Acesse a API:

```text
http://localhost:8000/docs
```

4. Em outro terminal, rode o frontend:

```bash
cd frontend
npm install
npm run dev
```

5. Acesse o app:

```text
http://localhost:5173
```

## Observacoes

- O `docker-compose.yml` atual e de desenvolvimento.
- Para producao, sera necessario configurar dominio, HTTPS, variaveis seguras, CORS do dominio real e um processo sem `--reload`.
- O fluxo futuro desejado e deixar o usuario entrar com baixo atrito, cadastrar nome e moto primeiro, e completar email/cadastro depois.
- O Cofre ainda nao deve ser implementado; a ideia atual e transformar o modulo de Metas na base desse recurso.
