# 🧠 Memória do Projeto — Gestão Motoca

> **Data do registro:** 18 de Agosto de 2026  
> **Status:** Sistema Funcional / Implementações recentes de Recuperação de Senha por PIN E-mail, Alteração de Senha e Refresh Token Automático (30 dias).  
> **Ramo Git Atual:** `melhoras-back`

---

## 📌 Visão Geral do Sistema

O **Gestão Motoca** é um sistema web de controle financeiro projetado especificamente para entregadores e motoboys. O objetivo central é fornecer o **lucro real** de trabalho ao contabilizar tanto os ganhos (corridas de apps, entregas particulares) quanto os custos fixos e variáveis da moto (combustível, manutenção, parcelas, seguros, IPVA, multas, alimentação).

### 🛠️ Stack Tecnológica
- **Backend:** Python 3.13 / FastAPI 0.129, SQLAlchemy 2.0, Alembic, Pydantic v2, Pytest 8.4
- **Frontend:** Vue 3.5, TypeScript 5.9, Pinia 3.0, Vue Router 4.6, Tailwind CSS 3.4, Vite 8.0
- **Banco de Dados:** PostgreSQL 16
- **Autenticação:** JWT Bearer (passlib + bcrypt + python-jose) com Par de Tokens (`access_token` 24h + `refresh_token` 30d)
- **Serviço de E-mail:** SMTP (Gmail SMTP com Senha de App)
- **Integrações Externas:** API WDAPI (consulta de placa de veículos com cache local no banco)

---

## 🔍 Onde Paramos & Estado Atual (Memory Snapshot)

### 1. Estado da Suíte de Testes e Build
- **Backend (Pytest):** 100% passando (11/11 testes executados sem erros via `.venv/bin/pytest`).
- **Frontend (TypeScript & Vue):** 100% passando (`vue-tsc -b && vite build` compila limpo sem erros).

### 2. Últimas Alterações Implementadas (Branch `melhoras-back`)

1. **🔑 Recuperação de Senha por E-mail (PIN de 6 Dígitos)**
   - Modal responsiva de 2 etapas no [LoginView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/LoginView.vue).
   - Disparo de e-mail HTML estilizado com código PIN de 6 dígitos (validade 15 min) via Gmail SMTP ([email_service.py](file:///home/jv/gm/gestao-motoca/app/core/email_service.py)).
   - Endpoints: `POST /auth/solicitar-recuperacao` e `POST /auth/redefinir-senha`.
   - Migration Alembic: `0007_recuperacao_senha.py`.

2. **🛡️ Alteração de Senha no Perfil**
   - Nova aba **"SENHA"** no painel de [ConfiguracoesView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/ConfiguracoesView.vue).
   - Endpoint protegido: `PUT /auth/alterar-senha` (exige validação da senha atual).

3. **🔄 Renovação Automática de Token (Refresh Token 30 dias)**
   - Login `POST /auth/login` retorna `access_token` e `refresh_token`.
   - Endpoint `POST /auth/refresh` valida o `refresh_token` e emite novo par.
   - Interceptor Axios em [client.ts](file:///home/jv/gm/gestao-motoca/frontend/src/api/client.ts) captura erro `401 Unauthorized` silenciosamente, renova os tokens e re-executa a chamada original sem deslogar o motoboy no celular.

4. **✉️ Validação Estrita & Normalização de E-mail (Unificação Visual)**
   - Backend: Validação Pydantic (`EmailStr`) e normalização automática para minúsculas com remoção de espaços em branco (`strip/lowercase`) em todos os schemas ([usuario.py](file:///home/jv/gm/gestao-motoca/app/schemas/usuario.py), [auth.py](file:///home/jv/gm/gestao-motoca/app/schemas/auth.py), [recuperacao_senha.py](file:///home/jv/gm/gestao-motoca/app/schemas/recuperacao_senha.py)).
   - Frontend: Adicionado `novalidate` nos formulários ([CadastroView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/CadastroView.vue), [LoginView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/LoginView.vue)) para eliminar balões cinzas nativos do navegador e exibir 100% dos erros na tarja tática vermelha do app.

5. **Refatoração Visual e Correções Anteriores**
   - Refatoração do Modo Claro e resolução de bugs de fusos horários em formulários de datas.
   - Obrigatoriedade de seleção de Categoria no cadastro de despesas.

---

## 🗺️ Mapeamento de Módulos

*Para ver a explicação detalhada de cada módulo, consulte o documento **[MODULOS_SISTEMA.md](file:///home/jv/gm/gestao-motoca/MODULOS_SISTEMA.md)**.*

- **Módulo 1: Autenticação & Usuários** (`/auth`, `/usuarios`) — Login, cadastro, refresh token, recuperação por e-mail e alteração de senha.
- **Módulo 2: Gestão de Motos** (`/motos`) — Placa (WDAPI), catálogo, manual e troca de moto ativa.
- **Módulo 3: Categorias** (`/categorias`) — Ganhos/Despesas por grupos com exclusão lógica.
- **Módulo 4: Lançamentos** (`/lancamentos`) — Ganho diário/corrida, despesa obrigatória e lote.
- **Módulo 5: Abastecimentos** (`/abastecimentos`) — Combustível, média de consumo e despesa automática.
- **Módulo 6: Manutenções** (`/manutencoes`) — Oficina, peças e despesa automática.
- **Módulo 7: Dashboard / Visão do Mês** (`/visao-mes`, `/indicadores`) — Lucro Real, ticket médio e gráficos.
- **Módulo 8: Metas** (`/metas`) — Metas de faturamento e limite de gastos (Backend OK, Frontend pendente).

---

## 🚀 Como Executar e Verificar o Projeto

### 1. Com Docker (Recomendado)
```bash
docker compose up --build
```

### 2. Com Python Local (`.venv`)
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
.venv/bin/pytest
```

### 3. Frontend (Vue 3 / Vite)
```bash
cd frontend
npm run dev
npm run build
```

---

*Documento mantido atualizado no método KISS para preservação da memória do projeto.*
