# 🔍 Diagnóstico do Sistema & Plano de Melhorias — Gestão Motoca

> **Análise de Código e UX:** Avaliação completa de todos os módulos existentes, identificando oportunidades de melhoria, gargalos, regras de negócio a aprimorar e novas funcionalidades sugeridas para elevar o nível da aplicação.

---

## 📌 1. Resumo do Diagnóstico

O **Gestão Motoca** possui uma base sólida, com arquitetura limpa (FastAPI no backend, Vue 3 + Pinia no frontend, PostgreSQL como banco de dados) e cobertura de testes unitários no backend. As regras de negócio fundamentais (Lucro Real, vínculo com motos, lançamentos por corrida/dia, aba de manutenção e abastecimento) estão funcionais.

No entanto, através da análise aprofundada de código, foram identificados **pontos de atenção, melhorias de UX para o público entregador, oportunidades de otimização no backend e funcionalidades pendentes** que agregarão enorme valor ao produto.

---

## 🔎 2. Análise Detalhada por Módulo

### 2.1 🔐 Módulo de Autenticação e Usuários
* **Estado Atual:** Funcional (cadastro, login JWT, hash bcrypt, categorias automáticas).
* **Pontos de Melhoria Identificados:**
  1. 🔑 **Troca / Recuperação de Senha:** Não existem endpoints ou telas para alteração de senha ou recuperação caso o usuário esqueça as credenciais.
  2. 🔄 **Renovação de Token (Refresh Token):** O token JWT expira em 24h. Quando expira, o usuário é deslogado bruscamente. Um mecanismo de renovação automática no [client.ts](file:///home/jv/gm/gestao-motoca/frontend/src/api/client.ts) melhoraria muito a experiência no celular.
  3. ✉️ **Validação de Formato de E-mail:** Adicionar validação estrita de formato de e-mail no Pydantic Schema ([usuario.py](file:///home/jv/gm/gestao-motoca/app/schemas/usuario.py)) para evitar cadastros com e-mails inválidos.

---

### 2.2 🏍️ Módulo de Gestão de Motos
* **Estado Atual:** Funcional (cadastro por placa WDAPI com cache, catálogo e manual; gestão de moto ativa).
* **Pontos de Melhoria Identificados:**
  1. ⏱️ **Atualização Rápida de Odômetro (KM):** O `km_atual` da moto é atualizado apenas ao cadastrar abastecimentos/manutenções ou editar a moto. Seria muito útil ter um botão rápido no Dashboard: *"Atualizar KM de hoje"*, permitindo acompanhar a rodagem sem ter que lançar gasto.
  2. 📈 **Histórico de Evolução de Quilometragem:** Criar um histórico/gráfico de evolução da quilometragem da moto ao longo dos meses para ajudar o entregador a prever depreciação e trocas de peças.

---

### 2.3 📁 Módulo de Categorias
* **Estado Atual:** Funcional (categorias por tipo e grupo despesa; exclusão lógica `ativo = false`).
* **Pontos de Melhoria Identificados:**
  1. 🎨 **Personalização Visual (Ícones e Cores):** Permitir que o usuário escolha a cor ou um ícone para suas categorias personalizadas, facilitando a identificação rápida no Dashboard e no Histórico.
  2. 🛠️ **Edição de Lançamentos com Categoria Inativa:** Se uma categoria for desativada (`ativo = false`), tentar editar um lançamento antigo que usa essa mesma categoria gera erro no backend. O backend deve permitir atualizar o lançamento se a categoria mantida for a mesma que ele já possuía originalmente.

---

### 2.4 💰 Módulo de Lançamentos
* **Estado Atual:** Funcional (ganho diário/corrida, despesa obrigatória por categoria, busca, filtros de período e paginação).
* **Pontos de Melhoria Identificados:**
  1. 🔍 **Busca por Texto Livre na Descrição:** Atualmente o filtro por palavra-chave filtra apenas pelo *nome da categoria*. Adicionar o campo `busca` no backend ([lancamento_service.py](file:///home/jv/gm/gestao-motoca/app/services/lancamento_service.py)) para buscar palavras contidas na `descricao` do lançamento (ex: buscar "troca de lâmpada" ou "pneu").
  2. 🗑️ **Ações em Lote no Frontend:** O frontend possui a rota `/lancamentos/lote` para criar em lote, mas na listagem do [HistoricoView.vue](file:///home/jv/gm/gestao-motoca/frontend/src/views/HistoricoView.vue) só é possível excluir um por um. Adicionar caixas de seleção (checkboxes) para **exclusão em lote** facilitaria limpezas no histórico.

---

### 2.5 ⛽ Abastecimentos & 🔧 Manutenções
* **Estado Atual:** Funcional (geração automática de despesa vinculada, cálculo de preço/litro e atualização de KM).
* **Pontos de Melhoria Identificados:**
  1. 🚨 **Alerta de Manutenção Preventiva (Troca de Óleo / Relação):**  
     - O entregador troca o óleo a cada 2.000 km ou 3.000 km.
     - **Sugestão:** Ao salvar a manutenção de "Troca de Óleo" com o KM atual, o sistema pode perguntar ou calcular o próximo KM sugerido para troca (ex: `KM Atual + 3000`). Quando a moto atingir esse KM em novos abastecimentos, o Dashboard exibe um alerta visual:  
       > ⚠️ *"Atenção: Sua moto atingiu 18.200 km. Está na hora da troca de óleo!"*
  2. ⛽ **Cálculo Preciso da Média de Consumo (km/L entre Tanques):**  
     - O cálculo atual da média no [indicador_service.py](file:///home/jv/gm/gestao-motoca/app/services/indicador_service.py) divide o total de km rodados pelo total de litros no mês.
     - **Melhoria:** Calcular o consumo relativo entre abastecimentos consecutivos ($\frac{\text{KM}_{\text{atual}} - \text{KM}_{\text{anterior}}}{\text{Litros}}$) para identificar se a moto está gastando combustível além do normal (alerta de regulagem de motor/carburador/injeção).

---

### 2.6 📊 Dashboard & Indicadores
* **Estado Atual:** Funcional (Lucro Real, Faturamento Bruto, Gastos, Ticket Médio, Calendário Visual).
* **Pontos de Melhoria Identificados:**
  1. 📊 **Comparativo com o Mês Anterior:** Exibir marcadores percentuais de variação em relação ao mês anterior no Dashboard (ex: 🟢 *"+14% de lucro em relação a Julho"* ou 🔴 *"+8% de gastos"*).
  2. 📄 **Exportação de Relatórios (PDF / Excel / CSV):** Adicionar botões para baixar o extrato financeiro do mês em formato **PDF formatado** ou **Planilha Excel/CSV**. Isso é fundamental para motoboys que precisam comprovar renda para bancos, financiamentos ou contadores.

---

### 2.7 🎯 Módulo de Metas
* **Estado Atual:** Backend 100% pronto (`metas.py`, `meta_service.py`), porém sem interface gráfica no Frontend.
* **Pontos de Melhoria Identificados:**
  1. 🖥️ **Implementação no Frontend:** Criar o arquivo `frontend/src/api/metas.ts`, a store Pinia `useMetaStore` e um widget visual de acompanhamento de metas no Dashboard (barra de progresso com porcentagem atingida no mês/dia).

---

## 🛠️ 3. Melhorias Transversais e Técnicas

1. ⚠️ **Atualização dos Schemas Pydantic v2:**
   - Nos arquivos em `app/schemas/`, trocar a sintaxe legada `class Config: from_attributes = True` por `model_config = ConfigDict(from_attributes=True)` para eliminar os avisos de depreciação durante os testes do Pytest.
2. 📱 **Atalhos Rápidos de Acesso (PWA / Mobile Experience):**
   - Como o público principal utiliza o celular ao final ou durante o expediente, transformar a aplicação em uma **PWA (Progressive Web App)** permitindo "Instalar na tela inicial" do celular como um aplicativo nativo.

---

## 📊 4. Matriz de Priorização (Impacto x Esforço)

| Funcionalidade / Melhoria | Impacto para o Motoboy | Esforço Técnico | Prioridade |
|---------------------------|-----------------------|-----------------|------------|
| 🖥️ **Interface do Módulo de Metas no Frontend** | 🔴 Alto | 🟢 Baixo | **P1 (Imediato)** |
| 🚨 **Alerta de Troca de Óleo / Manutenção Preventiva** | 🔴 Alto | 🟡 Médio | **P1 (Imediato)** |
| 📄 **Exportação de Relatório (PDF / CSV)** | 🔴 Alto | 🟡 Médio | **P2 (Alta)** |
| 📊 **Comparativo % com o Mês Anterior no Dashboard** | 🟡 Médio | 🟢 Baixo | **P2 (Alta)** |
| 🔍 **Busca por Texto na Descrição de Lançamentos** | 🟡 Médio | 🟢 Baixo | **P2 (Alta)** |
| ⏱️ **Botão de Atualização Rápida de Odômetro (KM)** | 🟡 Médio | 🟢 Baixo | **P3 (Média)** |
| 🔑 **Fluxo de Troca / Recuperação de Senha** | 🟡 Médio | 🟡 Médio | **P3 (Média)** |
| ⚠️ **Atualização dos Schemas Pydantic v2 (ConfigDict)** | 🟢 Baixo | 🟢 Baixo | **P3 (Técnica)** |

---

## 🗺️ 5. Plano de Ação Recomendado (Próximos Passos)

1. **Etapa 1:** Conectar o **Módulo de Metas** no Frontend (Backend já pronto).
2. **Etapa 2:** Implementar o **Alerta de Manutenção Preventiva** (Troca de Óleo / Kit Relação).
3. **Etapa 3:** Desenvolver o **Módulo Cofre (Caixinha da Moto)** (conforme especificado no [MODULO_COFRE.md](file:///home/jv/gm/gestao-motoca/MODULO_COFRE.md)).
4. **Etapa 4:** Adicionar a **Exportação de Relatórios PDF/Excel** e **Busca de Lançamentos por Texto**.
