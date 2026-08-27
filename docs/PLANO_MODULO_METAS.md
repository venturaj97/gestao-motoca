# 🎯 Planejamento do Módulo de Metas Financeiras & Cofres

Este documento serve como referência oficial para o planejamento, regras de negócio e implementação do **Módulo de Metas Financeiras & Cofres** no **Gestão Motoca**.

---

## 📌 Contexto & Propósito

O motoboy/entregador precisa de previsibilidade sobre seus ganhos, limites de gastos e preparação para custos futuros da moto (pneus, relação, seguro, IPVA).

O Módulo de Metas responde a 3 perguntas essenciais:
1. **Quanto preciso faturar por dia considerando meus dias de trabalho?**
2. **Quanto falta exatamente para fechar a semana/mês na meta?**
3. **Quanto já guardei para os objetivos da minha moto (pneus, seguro, manutenção)?**

---

## 💡 Formatos de Metas Suportados (Sem Burocracia)

Manteremos apenas **3 formatos diretos e práticos**:

### 1. Meta de Ganho (Diário, Semanal ou Mensal)
- **Exemplo Semanal:** Meta de R$ 700,00/semana trabalhando **5 dias na semana**.
- **Cálculo de Ritmo:**
  - Meta diária média esperada: `R$ 700 / 5 dias = R$ 140,00/dia`.
  - Se fez R$ 50 no 1º dia: o app exibe: **"Restam R$ 650,00. Você precisa de R$ 162,50/dia nos 4 dias de trabalho restantes."**
  - **Badge de Status:** 🟡 *Levemente abaixo do ritmo* (sem alarmes punitivos em vermelho).

### 2. Teto Máximo de Despesa (Diário, Semanal ou Mensal)
- **Exemplo Mensal:** Limite máximo de R$ 900,00 em despesas no mês.
- **Indicador:** Barra de consumo do teto de gastos (`R$ 350 / R$ 900` - 38%).

### 3. Cofres Táticos por Objetivo (Reservas da Moto)
- Metas de acúmulo com progresso visual para custos essenciais:
  - 🛞 **Cofre do Pneu & Relação** (Ex: R$ 150 / R$ 350 — 42%)
  - 🛡️ **Cofre do IPVA & Seguro** (Ex: R$ 400 / R$ 600 — 66%)
  - 🔧 **Cofre da Manutenção Preventiva** (Ex: R$ 100 / R$ 200 — 50%)
  - ⛽ **Reserva de Emergência / Combustível**

---

## 🧠 Lógica do Motor de Cálculo de Ritmo Proporcional

Para cada meta ativa, o sistema calcula:

$$\text{Meta Diária Ajustada} = \frac{\text{Valor Restante}}{\text{Dias de Trabalho Restantes no Período}}$$

### Diagnóstico de Status Visual

| Status | Condição | Cor / Badge | Exemplo de Mensagem |
|---|---|---|---|
| **META BATIDA** | Realizado ≥ Meta | 🟢 **Meta Atingida** | "Parabéns! Meta semanal de R$ 700 ultrapassada!" |
| **NO RITMO** | Realizado ≥ Ritmo Proporcional | 🟢 **No Ritmo** | "Excelente! Você está dentro do planejamento." |
| **RITMO LEVE** | Realizado < Ritmo (diferença leve) | 🟡 **Ajustar Ritmo** | "Faltam R$ 125/dia nos 4 dias de trampo restantes." |
| **EXIGE ESFORÇO** | Poucos dias de trabalho e saldo alto | 🟡 **Acelerar** | "Faltam 2 dias de trabalho! Meta diária: R$ 210/dia." |
| **TETO EXCEDIDO** | Despesa > Limite | 🔴 **Teto Excedido** | "Atenção: limite de despesas superado em R$ 45." |

---

## 🗺️ Mapa de Alterações no Sistema

### 1. Banco de Dados (Schema & Modelo `Meta`)
Novos campos adicionados na tabela `metas`:
- `dias_trabalho_semana` (`Integer`, default `6`): Quantidade de dias que o usuário trabalha na semana (1 a 7).
- `categoria_cofre` (`String(50)`, opcional): `'PNEU'`, `'SEGURO'`, `'IPVA'`, `'REVISAO'`, `'RESERVA'`, `'OUTROS'`.
- `periodo`: Suporte a `'DIARIO'`, `'SEMANAL'`, `'MENSAL'`, `'OBJETIVO'`.

### 2. Backend (FastAPI)
- `app/models/meta.py`: Atualização do model e check constraints.
- `app/schemas/meta.py`: Atualização dos DTOs de entrada e saída.
- `app/services/meta_service.py`: Recálculo de ritmo com base em `dias_trabalho_semana`.
- `app/routers/metas.py`: Endpoints CRUD `/metas` e `/metas/alertas`.

### 3. Frontend (Vue 3)
- `frontend/src/api/metas.ts`: Serviço Axios para integração.
- `frontend/src/views/MetasView.vue`: View principal de Metas & Cofres.
- `frontend/src/components/AppLayout.vue`: Rota `/manutencao` substituída por `/metas` no menu e bottom nav.
- `frontend/src/router/index.ts`: Configuração da nova rota.

