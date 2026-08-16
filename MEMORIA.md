# 🧠 Memória do Projeto — Gestão Motoca

> **Data do registro:** 16 de Agosto de 2026  
> **Status:** Sistema Funcional / Refatorações recentes de UI, Datas, Modo Claro e Validações concluídas com sucesso.  
> **Ramo Git Atual:** `inicio-front` (sincronizado com `main`)

---

## 📌 Visão Geral do Sistema

O **Gestão Motoca** é um sistema web de controle financeiro projetado especificamente para entregadores e motoboys. O objetivo central é fornecer o **lucro real** de trabalho ao contabilizar tanto os ganhos (corridas de apps, entregas particulares) quanto os custos fixos e variáveis da moto (combustível, manutenção, parcelas, seguros, IPVA, multas, alimentação).

### 🛠️ Stack Tecnológica
- **Backend:** Python 3.13 / FastAPI 0.129, SQLAlchemy 2.0, Alembic, Pydantic v2, Pytest 8.4
- **Frontend:** Vue 3.5, TypeScript 5.9, Pinia 3.0, Vue Router 4.6, Tailwind CSS 3.4, Vite 8.0
- **Banco de Dados:** PostgreSQL 16
- **Autenticação:** JWT Bearer (passlib + bcrypt + python-jose)
- **Integrações Externas:** API WDAPI (consulta de placa de veículos com cache local no banco)

---

## 🔍 Onde Paramos & Estado Atual (Memory Snapshot)

### 1. Estado da Suíte de Testes e Build
- **Backend (Pytest):** 100% passando (9 testes executados sem erros via `.venv/bin/pytest`).
- **Frontend (TypeScript & Vue):** 100% passando (`vue-tsc -b && vite build` compila limpo sem erros de tipagem ou bundle).

### 2. Análise dos Commits e Modificações Recentes
Analisando o histórico recente de commits na branch `inicio-front` / `main`:

1. **Refatoração do Modo Claro (`refatorando modo claro` - `6059423`, `843ed05`)**
   - Ajustados componentes visuais e variáveis CSS globais ([style.css](file:///home/jv/gm/gestao-motoca/frontend/src/style.css)) para suporte nativo e elegante ao modo claro.
   - Refatorados estilos nas views: [DashboardView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/DashboardView.vue), [HistoricoView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/HistoricoView.vue), [LancarView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/LancarView.vue), [AbastecerView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/AbastecerView.vue), [ManutencaoView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/ManutencaoView.vue) e [ConfiguracoesView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/ConfiguracoesView.vue).

2. **Resolução de Bug de Datas (`bug da datas no sistema resolvido` - `24eec18`)**
   - Corrigidos problemas de deslocamento de fusos horários e datas nos formulários de abastecimento, manutenção e lançamentos ([AppDateInput.vue](file:///home/jv/gm/gestao-motoca/frontend/src/components/AppDateInput.vue), [AbastecerView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/AbastecerView.vue), [ManutencaoView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/ManutencaoView.vue)).

3. **Regras de Negócio de Despesas & Categorias (`regras nas despesas, categoria obrigatorio` - `5f81e8a`, `ab85537`, `d85ca9e`)**
   - Implementada a obrigatoriedade da escolha de Categoria no cadastro de Despesas tanto no Backend ([categoria_service.py](file:///home/jv/gm/gestao-motoca/app/services/categoria_service.py)) quanto no Frontend ([LancarView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/LancarView.vue)).
   - Reformulada a lógica de lançamento em lote/individual e persistência da categoria selecionada pelo usuário.

4. **Limpeza de Código Morto & Documentação (`785ec1e`, `c3607ed`)**
   - Remoção de assets do Vite/Vue e componentes não utilizados ([HelloWorld.vue](file:///home/jv/gm/gestao-motoca/frontend/src/components/HelloWorld.vue), `hero.png`).
   - Criação da Documentação Técnica ([DOCUMENTACAO.md](file:///home/jv/gm/gestao-motoca/DOCUMENTACAO.md)) e Mapeamento de Arquitetura ([MAPEAMENTO.md](file:///home/jv/gm/gestao-motoca/MAPEAMENTO.md)).

---

## 🗺️ Mapeamento de Módulos e Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND (Vue 3 + TS)                     │
├─────────────────┬─────────────────────────────┬─────────────────┤
│ Views Publicas  │ Views Autenticadas          │ Gerenciamento   │
│ - InicioView    │ - DashboardView             │ - Pinia Stores  │
│ - LoginView     │ - HistoricoView             │   (auth, moto,  │
│ - CadastroView  │ - LancarView                │    theme)       │
│                 │ - AbastecerView             │ - Axios Client  │
│                 │ - ManutencaoView            │   (Bearer JWT)  │
│                 │ - VincularMotoView          │                 │
│                 │ - ConfiguracoesView         │                 │
│                 │ - CadastrarMotoView         │                 │
└─────────────────┴─────────────────────────────┴─────────────────┘
                                │ HTTP / REST API (JWT)
┌───────────────────────────────▼─────────────────────────────────┐
│                       BACKEND (FastAPI + SQLAlchemy)            │
├─────────────────┬─────────────────────────────┬─────────────────┤
│ Routers (API)   │ Services (Regras)           │ Models (ORM)    │
│ - auth          │ - usuario_service           │ - Usuario       │
│ - usuarios      │ - moto_service              │ - MotoUsuario   │
│ - motos         │ - categoria_service         │ - Categoria     │
│ - categorias    │ - lancamento_service        │ - Lancamento    │
│ - lancamentos   │ - abastecimento_service     │ - Abastecimento │
│ - abastecimentos│ - manutencao_service        │ - Manutencao    │
│ - manutencoes   │ - indicador_service         │ - Meta          │
│ - indicadores   │ - meta_service              │ - Catalogos     │
│ - visao_mes     │ - visao_mes_service         │   (WDAPI/Modelo)│
└─────────────────┴─────────────────────────────┴─────────────────┘
                                │ PostgreSQL 16
```

### Detalhes das Telas e Funcionalidades Principais:
1. **Landing Page & Autenticação:**
   - `/inicio` - Apresentação pública da aplicação.
   - `/login` & `/cadastro` - Autenticação JWT e criação de contas com categorias padrão automáticas.
   - `/vincular-moto` - Fluxo obrigatório onboarding de vínculo de moto.
2. **Dashboard & Visão Geral (`/`):**
   - Resumo financeiro do mês (receita bruta, total despesas, lucro líquido, ticket médio por dia/corrida).
   - Calendário visual de dias trabalhados e gráfico mensal.
3. **Lançamentos (`/lancar`):**
   - Entradas de Ganhos (`DIARIO` ou por `CORRIDA` com minutos e km).
   - Entradas de Despesas (obrigatório escolher categoria).
4. **Módulos Especiais (`/abastecer` & `/manutencao`):**
   - Formulários rápidos que salvam o registro específico e automaticamente geram a despesa financeira correspondente.
5. **Histórico & Configurações (`/historico` & `/configuracoes`):**
   - Histórico completo com ordenação, paginação e filtros (período, tipo, categoria, valor).
   - Gerenciamento de motos (adicionar, editar, trocar moto ativa) e categorias personalizadas.

---

## 📋 Lista de Tarefas / Próximos Passos (Backlog)

- [ ] **Módulo de Metas no Frontend (Pendente Alto Priority):**
  - O Backend possui o model `Meta`, service `meta_service.py` e endpoints `/metas` prontos.
  - Criar `frontend/src/api/metas.ts`, store/integração no frontend e tela/componente de metas e progresso no Dashboard.
- [ ] **Migração de Warnings Pydantic v2:**
  - Atualizar os schemas em `app/schemas/` trocando a classe interna `Config` por `model_config = ConfigDict(...)` para remover os warnings do Pytest.
- [ ] **Testes no Frontend:**
  - Adicionar testes unitários/componentes no frontend utilizando Vitest.

---

## 🚀 Como Executar e Verificar o Projeto

### Backend (Python/FastAPI)
```bash
# Ativar venv e rodar o servidor de desenvolvimento
.venv/bin/uvicorn app.main:app --reload --port 8000

# Executar suíte de testes unitários do backend
.venv/bin/pytest
```

### Frontend (Vue 3 / Vite)
```bash
# Entrar na pasta do frontend
cd frontend

# Iniciar servidor de desenvolvimento
npm run dev

# Executar checagem de tipos (TypeScript) e build de produção
npm run build
```

---

*Documento gerado automaticamente para preservação do estado do projeto.*
