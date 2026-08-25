# 🏦 Especificação de Produto — Módulo Cofre (Reserva da Moto)

> **Proposta & Arquitetura:** Documentação funcional e técnica para implementação do novo **Módulo Cofre (Caixinha da Moto / Reserva de Emergência e Manutenção)**.

---

## 1. 💡 Conceito e Objetivo do Produto

Um dos maiores problemas financeiros enfrentados por entregadores e motoboys é a **falta de reserva para custos sazonais e imprevistos**. Quando a moto quebra (pneu fura, relação gasta, freio acaba) ou os impostos anuais vencem (IPVA, Licenciamento, Seguro), o entregador frequentemente precisa recorrer a empréstimos ou parar de trabalhar por falta de capital.

O **Módulo Cofre** funciona como uma **caixinha/reserva financeira virtual** integrada ao fluxo diário do aplicativo. Ele permite que o motoboy separe automaticamente ou manualmente uma fatia do seu faturamento diário para garantir o funcionamento contínuo da sua ferramenta de trabalho.

---

## 2. 🎯 Funcionalidades Principais

### 2.1 Caixinhas (Categorias da Reserva)
O saldo do cofre poderá ser subdividido em 3 objetivos principais:

1. 🔧 **Caixinha de Manutenção & Peças**
   - Destinado a trocas periódicas (óleo, kit relação, pneus, lonas de freio, cabo de embreagem).
2. 📄 **Caixinha de Impostos & Custos Fixos**
   - Destinado a pagamentos anuais ou parcelados (IPVA, Licenciamento, DPVAT, Seguro, Franquia).
3. 🆘 **Caixinha de Emergência & Imprevistos**
   - Fundo de proteção para cobrir dias parado sem trabalhar (doença, chuvas fortes, acidentes) ou custos com guincho/multas.

### 2.2 Regra de Aporte Automático (Porcentagem por Ganho)
- O usuário poderá configurar uma **Regra de Reserva Automática** (ex: *Guardar 10% de todo ganho cadastrado* ou *Guardar R$ 15,00 por dia trabalhado*).
- Ao registrar um novo ganho no [LancarView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/LancarView.vue), o sistema calculará a fatia da reserva e exibirá um alerta:  
  > *"💰 Ganho de R$ 200,00 registrado! R$ 20,00 foram reservados para o seu Cofre."*

### 2.3 Resgate / Uso da Reserva para Pagamento de Despesas
- Ao cadastrar uma **Manutenção** ou um **Abastecimento/Despesa**, o usuário terá um toggle (interruptor):  
  `[x] Usar saldo do Cofre para pagar esta despesa`
- Caso marcado, o saldo é deduzido da caixinha correspondente e o movimento fica registrado no histórico do cofre.

---

## 3. 🗄️ Modelagem de Dados Proposta (Backend)

### 3.1 Tabela `cofres` (Configuração & Saldo Global)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `usuario_id` | Integer (FK) | Vínculo com a tabela `usuarios` |
| `percentual_retencao_auto` | Float | Porcentagem automática de aporte (ex: 10.0 = 10%) |
| `valor_fixo_dia_auto` | Float | Valor fixo opcional por dia trabalhado |
| `ativo_auto` | Boolean | Se o aporte automático está ativado |
| `saldo_manutencao` | Float | Saldo acumulado na caixinha de manutenção |
| `saldo_impostos` | Float | Saldo acumulado na caixinha de impostos |
| `saldo_emergencia` | Float | Saldo acumulado na caixinha de emergência |
| `criado_em` | DateTime | Data de criação |

### 3.2 Tabela `cofres_movimentacoes` (Histórico de Entradas e Saídas)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `cofre_id` | Integer (FK) | Vínculo com a tabela `cofres` |
| `tipo_movimentacao` | Enum | `ENTRADA` (Aporte) ou `SAIDA` (Resgate) |
| `origem` | Enum | `AUTOMATICO_GANHO`, `MANUAL`, `PAGAMENTO_DESPESA` |
| `caixinha` | Enum | `MANUTENCAO`, `IMPOSTOS`, `EMERGENCIA` |
| `valor` | Float | Valor movimentado em R$ |
| `descricao` | String | Motivo ou observação |
| `lancamento_id` | Integer (FK) | Vínculo opcional com o lançamento financeiro |
| `data_movimentacao` | DateTime | Data do registro |

---

## 4. 🌐 Endpoints REST API Propostos

```http
# Obter o resumo do cofre (saldos atuais e configurações)
GET /cofre

# Atualizar as configurações de reserva automática (ex: % de retenção)
PUT /cofre/configuracao

# Realizar um aporte manual no cofre
POST /cofre/aporte

# Realizar um resgate manual ou utilizar saldo do cofre
POST /cofre/resgate

# Listar o histórico de movimentações (entradas/saídas) do cofre
GET /cofre/movimentacoes
```

---

## 5. 🎨 Interface & UX (Frontend)

1. **Card de Saldo no Dashboard:**  
   No topo do [DashboardView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/DashboardView.vue), adicionar um card compacto **"Cofre da Moto"** exibindo o saldo acumulado total com um botão rápido *"Guardar / Ver Caixinhas"*.

2. **Tela Dedicada `/cofre` (ou Modal):**  
   - Exibição das 3 caixinhas (Manutenção, Impostos, Emergência) com barras de progresso visuais.
   - Formulário simples de Aporte Rápido e Resgate.
   - Histórico recente de entradas e saídas.

3. **Integração no Formulário de Lançamento (`LancarView.vue`):**  
   - Ao lançar um ganho, checkbox/toggle pré-selecionado: `[x] Reservar 10% no Cofre`.

---

## 🚀 Plano de Implementação Sugerido

1. **Fase 1 (Backend):** Criar os models SQLAlchemy `Cofre` e `CofreMovimentacao`, migration Alembic, Pydantic Schemas, `cofre_service.py` e router `/cofre`.
2. **Fase 2 (Frontend - API & Store):** Criar `frontend/src/api/cofre.ts` e store Pinia `useCofreStore`.
3. **Fase 3 (Frontend - UI):** Adicionar o Card no Dashboard e a integração no formulário de lançamentos e abastecimentos/manutenções.
