# 📦 Funcionamento dos Módulos — Gestão Motoca

> **Documentação de Módulos (Método KISS):** Registro direto e simples do funcionamento de todas as áreas e funcionalidades do sistema.

---

## 1. 🔐 Módulo de Autenticação e Usuários

* **Objetivo:** Garantir a segurança do acesso, gestão de perfil, renovação de sessão e criação do ambiente inicial do motoboy.
* **Endpoints principais:**  
  `POST /usuarios`, `POST /auth/login`, `GET /auth/me`, `POST /auth/refresh`, `POST /auth/solicitar-recuperacao`, `POST /auth/redefinir-senha`, `PUT /auth/alterar-senha`, `POST /auth/enviar-confirmacao-email`, `POST /auth/confirmar-email`
* **Funcionamento:**
  1. **Cadastro:** Nome, e-mail e senha. A senha é criptografada com `bcrypt`.
  2. **Categorias Padrão Automáticas:** No cadastro, o sistema gera automaticamente as categorias iniciais (combustível, troca de óleo, refeição, corridas de app, etc.).
  3. **Autenticação (Par de Tokens):**  
     - **`access_token`:** Válido por 24h para autorizar chamadas.
     - **`refresh_token`:** Válido por 30 dias para renovar o acesso sem pedir senha.
  4. **Renovação Automática de Sessão (Refresh Token):** O cliente Axios ([client.ts](file:///home/jv/gm/gestao-motoca/frontend/src/api/client.ts)) intercepta erros `401 Unauthorized` de forma silenciosa, chama `POST /auth/refresh` e re-executa a requisição original sem deslogar o entregador.
  5. **Recuperação de Senha por E-mail (PIN 6 Dígitos):** Na tela de login, o usuário solicita um código PIN de 6 dígitos por e-mail (válido por 15 min) para redefinir a senha via Gmail/SMTP.
  6. **Alteração de Senha (Logado):** Na aba "Senha" das Configurações, o entregador altera sua senha confirmando a senha atual.
  7. **Validação Estrita & Normalização de E-mail:** Validação de formato via Pydantic (`EmailStr`) no backend com conversão para minúsculas e remoção de espaços (`strip/lowercase`), combinada com o atributo `novalidate` nos formulários Vue para eliminar balões cinzas nativos do navegador e exibir 100% dos alertas no estilo visual tático do app.
  8. **Confirmação de E-mail Opcional (Soft Verification):** Ao se cadastrar, o entregador utiliza o app normalmente (`email_confirmado = False`). Um banner amarelo suave no topo do Dashboard ([ConfirmarEmailBanner.vue](file:///home/jv/gm/gestao-motoca/frontend/src/components/ConfirmarEmailBanner.vue)) sugere a confirmação do e-mail via PIN de 6 dígitos sem bloquear o uso. Validado o PIN, `email_confirmado` torna-se `True` e o banner desaparece.
  9. **Proteção de Rotas:** O cabeçalho `Authorization: Bearer <token>` é enviado em todas as chamadas autenticadas.

---

## 2. 🏍️ Módulo de Gestão de Motos

* **Objetivo:** Cadastrar e gerenciar as motos do usuário. É o módulo central, pois todas as movimentações financeiras exigem uma moto associada.
* **Endpoints principais:** `/motos/marcas`, `/motos/modelos`, `/motos/anos`, `/motos/consulta-placa/{placa}`, `/motos/minha`
* **Formas de Cadastro:**
  1. **Por Placa (API WDAPI):** Consulta externa com cache local (`motos_consultas_wdapi`) para economizar chamadas de API.
  2. **Catálogo de Modelos:** Escolha por Marca $\rightarrow$ Modelo $\rightarrow$ Ano/Versão.
  3. **Manual:** Digitação livre de marca, modelo e ano.
* **Regra de Moto Ativa:**
  - O usuário precisa ter **pelo menos 1 moto cadastrada**.
  - Com 2+ motos, uma fica definida como **ativa (`ativa = true`)** e recebe os novos lançamentos.
  - A moto ativa pode ser trocada em Configurações.

---

## 3. 📁 Módulo de Categorias

* **Objetivo:** Classificar e organizar receitas e despesas.
* **Endpoints principais:** `GET /categorias`, `POST /categorias`, `PUT /categorias/{id}`, `DELETE /categorias/{id}`
* **Estrutura:**
  - **Tipo `GANHO`:** Entregas App, Entregas Particulares, Bônus, etc.
  - **Tipo `DESPESA`:** Divididas em grupos obrigatórios: `GERAL`, `ABASTECIMENTO`, `MANUTENCAO`, `IMPOSTO`.
* **Exclusão Lógica:** Categorias com histórico passam para `ativo = false` em vez de serem apagadas do banco.

---

## 4. 💰 Módulo de Lançamentos

* **Objetivo:** Registro financeiro diário de entradas e saídas.
* **Endpoints principais:** `GET /lancamentos`, `POST /lancamentos`, `POST /lancamentos/lote`, `PUT /lancamentos/{id}`, `DELETE /lancamentos/{id}`
* **Regras de Negócio:**
  - **Ganho Diário (`periodo = DIARIO`):** Faturamento total do dia.
  - **Ganho por Corrida (`periodo = CORRIDA`):** Faturamento com minutos e KM rodados.
  - **Despesa:** Requer data, valor e **categoria obrigatória**.
  - **Dia da Semana:** Preenchido automaticamente a partir da data.

---

## 5. ⛽ Módulo de Abastecimentos

* **Objetivo:** Registro detalhado de combustível e consumo.
* **Endpoints principais:** `GET /abastecimentos`, `POST /abastecimentos`, `PUT /abastecimentos/{id}`, `DELETE /abastecimentos/{id}`
* **Funcionamento:**
  - Pede data, KM atual, litros, valor total, preço/litro e posto.
  - **Automação:** Salva o abastecimento, **cria automaticamente a Despesa** em "Combustível" e atualiza o KM da moto ativa.

---

## 6. 🔧 Módulo de Manutenções

* **Objetivo:** Registro de peças, oficina e preventiva da moto.
* **Endpoints principais:** `GET /manutencoes`, `POST /manutencoes`, `PUT /manutencoes/{id}`, `DELETE /manutencoes/{id}`
* **Funcionamento:**
  - Pede data, tipo de serviço (óleo, pneus, relação, freios), descrição, valor, KM atual e oficina.
  - **Automação:** Salva a manutenção e **cria automaticamente a Despesa financeira correspondente**.

---

## 7. 📊 Módulo Dashboard / Visão do Mês

* **Objetivo:** Apresentar os indicadores estratégicos de lucro real.
* **Endpoints principais:** `GET /visao-mes`, `GET /indicadores/resumo`
* **Métricas:**
  - **Lucro Real:** $\text{Faturamento Bruto} - \text{Total de Despesas}$.
  - **Ticket Médio:** Médias por corrida e por dia trabalhado.
  - **Desempenho por Dia da Semana:** Melhor e pior dia de trabalho.
  - **Rendimento da Moto:** Média de km/L e custo por km.
  - **Calendário Visual:** Exibição gráfica dos dias trabalhados no mês.

---

## 8. 🎯 Módulo de Metas

* **Objetivo:** Planejamento de faturamento e limites de gastos.
* **Endpoints principais:** `GET /metas`, `POST /metas`, `PUT /metas/{id}`, `DELETE /metas/{id}`, `GET /metas/alertas`
* **Tipos:** Receita Mensal, Lucro Mensal, Teto de Despesa, Meta Diária.
* **Status:** Backend 100% pronto. Frontend pendente.

---

## ⚙️ Demais Funcionalidades e Utilitários

- **Health Check (`GET /saude`):** Endpoint simples de verificação do status da API.
- **CORS Configurado:** Permite origens do frontend em desenvolvimento e produção.
- **Tema Claro / Escuro (Light & Dark Mode):** Suporte nativo em todas as telas com alternância em 1 clique.
- **Onboarding Automático:** Se o usuário logado não possuir moto, o router bloqueia o acesso e redireciona para `/vincular-moto`.
