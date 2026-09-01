# 🚀 Plano de Monetização & Reestruturação SaaS – Gestão Motoca

Este documento detalha o planejamento estratégico, a nova arquitetura de navegação e o modelo de negócios Freemium/SaaS para o aplicativo **Gestão Motoca**.

---

## 🎯 1. Visão Geral do Produto & Estratégia

O **Gestão Motoca** evolui de um organizador financeiro simples para um **SaaS de Alta Performance para Entregadores de Aplicativo (Motoboys)**.

### **Proposta de Valor:**
- **Gratuito:** O motorista/entregador organiza a rotina diária sem fricção (lança ganhos e despesas em 5 segundos).
- **Pago (PRO):** O motorista ganha inteligência financeira para rodar mais barato, economizar na manutenção da moto e multiplicar seu lucro líquido.

---

## 📱 2. Nova Arquitetura de Navegação (UX/UI)

Para otimizar o fluxo de uso no trânsito e destacar os módulos de valor comercial, a estrutura de navegação foi reformulada:

### **Barra de Navegação Principal (Bottom Nav & Sidebar):**
1. 🏠 **Início (Dashboard):** Visão geral do dia, saldo rápido, metas diárias e atalhos.
2. 📜 **Histórico:** Extrato completo de lançamentos, busca por data, filtros e edição rápida.
3. ➕ **Lançar:** Tela única de lançamento rápido (Ganhos ou Despesas por categoria).
4. 🎯 **Metas & Cofres:** Metas financeiras + Caixinhas automáticas (Pneu, IPVA, Manutenção).
5. 📊 **Relatórios (PRO 👑):** Painel Inteligente de BI (Lucro R$/h, R$/km, comparativo iFood vs Rappi vs Uber).

### **Rodapé da Sidebar (Desktop) / Topbar (Mobile):**
- ⚙️ **Config:** Dados do perfil, cadastro de moto e preferências do sistema.
- 🌙 **Tema:** Alternância entre Modo Escuro e Modo Claro.
- 🚪 **Sair:** Encerramento seguro de sessão.

---

## 💎 3. Modelo Freemium & Planos de Assinatura

### **Tabela Comparativa de Planos:**

| Funcionalidade | Plano Gratuito (Free) | Plano PRO (Premium 👑) |
| :--- | :---: | :---: |
| **Lançamentos diários (Ganhos/Despesas)** | Ilimitado | Ilimitado |
| **Histórico e Extrato de Transações** | Completo | Completo |
| **Categorização Automática** | Sim | Sim |
| **Dashboard Diário Basico** | Sim | Sim |
| **Metas Financeiras Básico** | Até 1 meta ativa | Metas Ilimitadas |
| **Módulo Cofres / Autoguarda (Caixinhas)** | Bloqueado 🔒 | **Ilimitado + Autoguarda %** ⚡ |
| **Relatórios Avançados & Análise BI** | Bloqueado 🔒 | **Completo (R$/h, R$/km, Gráficos)** 📊 |
| **Comparativo de Rendimento por App** | Bloqueado 🔒 | **Liberado** 🚗🛵 |
| **Exportação PDF / Excel para Contador** | Bloqueado 🔒 | **Liberado** 📑 |
| **Benefícios & Descontos em Parceiros** | Padrão | **Exclusivo (Desconto Óleo/Pneu)** 🔧 |

---

## 💰 4. Estratégia de Preço & Monetização B2B

### **4.1 Preço do Plano PRO:**
- **Assinatura Mensal:** **R$ 9,90 / mês**
- **Assinatura Anual:** **R$ 89,90 / ano** *(25% de desconto - R$ 7,49/mês)*

> 💡 **Gatilho de Vendas:** *"Assine o PRO por apenas R$ 9,90/mês — o equivalente a menos de 2 corridas curtas por mês para ter o controle total do seu dinheiro!"*

### **4.2 Monetização B2B & Afiliados (Receita Secundária):**
1. **Peças e Manutenção:** Parcerias com distribuidoras e oficinas (comissão por compra de óleo, pneus e pastilhas via app).
2. **Proteção Veicular & Seguros:** Indicação de proteção veicular contra roubo/furto com comissão por contratação.
3. **Equipamentos & Acessórios:** Afiliado Magalu/Shopee/Mercado Livre para capacetes, suportes de celular e capas de chuva.

---

## 🔒 5. Estratégia de Conversão & UX Paywall

1. **Aba Visível com Badge PRO:** As abas de **Relatórios** e **Cofres** continuam visíveis no menu com o selo `👑 PRO`.
2. **Degustação Visual (Preview):** Ao clicar sem ser assinante, a tela exibe uma demonstração interativa ou desfocada dos gráficos com o banner de upgrade.
3. **Checkout Rápido Pix / Cartão:** Integração com gateway (Mercado Pago ou Asaas) para liberação instantânea via Pix.

---

## 📋 6. Roadmap de Implementação

- [ ] **Fase 1:** Mover botão de `Config` para o rodapé da Sidebar ao lado do Tema e Sair.
- [ ] **Fase 2:** Criar visualização dedicada `/relatorios` separada da `/historico`.
- [ ] **Fase 3:** Integrar os **Cofres / Caixinhas** dentro da view `/metas`.
- [ ] **Fase 4:** Adicionar atributo `plano` no modelo de usuário no backend (`GRATUITO` vs `PRO`).
- [ ] **Fase 5:** Desenvolver a Modal Paywall de Upgrade com Preview dos recursos PRO.
- [ ] **Fase 6:** Implementar a Landing Page de divulgação do aplicativo.

---

## 🖼️ 7. Capturas de Tela Reais do Aplicativo

As imagens a seguir foram capturadas diretamente da aplicação em funcionamento local (`http://localhost:5173`) com dados reais autenticados:

1. **Dashboard Principal (Início):** `saas/tela_real_dashboard.png`
2. **Relatórios & Painel Inteligente (Recurso PRO):** `saas/tela_real_relatorios.png`
3. **Metas & Cofres (Recurso PRO):** `saas/tela_real_metas.png`
4. **Histórico de Transações & Extrato:** `saas/tela_real_historico_extrato.png`
5. **Tela de Lançamento Rápido:** `saas/tela_real_lancar.png`
6. **Configurações & Perfil da Moto:** `saas/tela_real_configuracoes.png`
7. **Página Inicial Pública (Divulgação / Landing):** `saas/tela_real_inicio_landing.png`

