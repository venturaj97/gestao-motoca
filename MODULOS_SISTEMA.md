# 📦 Funcionamento dos Módulos — Gestão Motoca

> **Documentação de Módulos:** Guia explicativo detalhado de como funciona cada módulo do sistema.

---

## 1. 🔐 Módulo de Autenticação e Usuários

* **Objetivo:** Garantir a segurança do acesso, gestão de perfil e criação do ambiente inicial do motoboy.
* **Endpoints principais:** `POST /usuarios`, `POST /auth/login`, `GET /auth/me`, `POST /auth/solicitar-recuperacao`, `POST /auth/redefinir-senha`, `PUT /auth/alterar-senha`
* **Funcionamento:**
  1. **Cadastro:** O usuário informa nome, e-mail e senha. A senha é criptografada com `bcrypt`.
  2. **Categorias Padrão Automáticas:** No momento do cadastro, o sistema gera automaticamente uma lista de categorias iniciais para o usuário (combustível, troca de óleo, refeição, corridas de aplicativo, etc.).
  3. **Autenticação:** Ao realizar login, o backend gera um token **JWT (Bearer Token)** válido por 24 horas.
  4. **Recuperação de Senha por E-mail:** O entregador pode solicitar um código PIN de 6 dígitos via e-mail para redefinir sua senha caso a tenha esquecido.
  5. **Alteração de Senha:** O entregador logado pode alterar sua senha na aba "Senha" das Configurações fornecendo a senha atual.
  6. **Proteção de Rotas:** Todas as chamadas subsequentes ao backend enviam o token no cabeçalho `Authorization: Bearer <token>`, identificando quem é o usuário logado via `Depends(get_usuario_logado)`.

---

## 2. 🏍️ Módulo de Gestão de Motos

* **Objetivo:** Cadastrar e gerenciar as motos do usuário. É o módulo central do sistema, pois todas as movimentações financeiras exigem uma moto associada.
* **Endpoints principais:** `/motos/marcas`, `/motos/modelos`, `/motos/anos`, `/motos/consulta-placa/{placa}`, `/motos/minha`
* **Formas de Cadastro:**
  1. **Por Placa (API WDAPI):** O usuário digita a placa e o sistema consulta a API externa WDAPI. Os resultados são salvos em cache local (`motos_consultas_wdapi`) para evitar consultas repetidas e custos de API.
  2. **Catálogo de Modelos:** O usuário navega pela hierarquia Marca $\rightarrow$ Modelo $\rightarrow$ Ano/Versão cadastrados no banco.
  3. **Manual:** Digitação direta dos dados da moto.
* **Regra de Moto Ativa:**
  - O usuário precisa ter **pelo menos 1 moto cadastrada** para usar o sistema.
  - Se possuir 2 ou mais motos, uma delas fica marcada como **ativa (`ativa = true`)**. Os lançamentos são automaticamente vinculados à moto ativa.
  - O usuário pode alternar a moto ativa a qualquer momento na tela de Configurações.

---

## 3. 📁 Módulo de Categorias

* **Objetivo:** Classificar e organizar todas as receitas e despesas do motoboy.
* **Endpoints principais:** `GET /categorias`, `POST /categorias`, `PUT /categorias/{id}`, `DELETE /categorias/{id}`
* **Estrutura:**
  - **Tipo `GANHO`:** Categorias para faturamento (ex: *Entregas iFood/Uber*, *Entregas Particulares*, *Bônus/Gorjetas*).
  - **Tipo `DESPESA`:** Subdivididas em grupos obrigatórios:
    - `GERAL`: Alimentação (Almoço/Café), Telefone/Internet, Outros.
    - `ABASTECIMENTO`: Combustível.
    - `MANUTENCAO`: Troca de Óleo, Kit Relação, Pneus, Peças.
    - `IMPOSTO`: Parcela da moto, Seguro, IPVA, Licenciamento, Multas.
* **Regra de Exclusão Lógica:** Se uma categoria já possui lançamentos financeiros associados, ela não é excluída fisicamente do banco de dados. O sistema faz uma **exclusão lógica** (`ativo = false`), ocultando a categoria nos seletores mas mantendo a integridade dos relatórios passados.

---

## 4. 💰 Módulo de Lançamentos

* **Objetivo:** Registro e controle diário de todas as entradas e saídas de dinheiro.
* **Endpoints principais:** `GET /lancamentos`, `POST /lancamentos`, `POST /lancamentos/lote`, `PUT /lancamentos/{id}`, `DELETE /lancamentos/{id}`
* **Regras de Negócio:**
  - **Lançamento de Ganho:**
    - Pode ser **Diário** (`periodo = DIARIO`), registrando o valor acumulado do dia.
    - Pode ser por **Corrida** (`periodo = CORRIDA`), onde exige obrigatoriamente os minutos de duração (`minutos_corrida`) e os quilômetros rodados (`km_corrida`).
  - **Lançamento de Despesa:** Exige obrigatoriamente a data, o valor e uma **categoria** de despesa válida.
  - **Atribuição de Data:** O dia da semana (`dia_semana`) é calculado e preenchido automaticamente com base na data informada.

---

## 5. ⛽ Módulo de Abastecimentos

* **Objetivo:** Registrar o histórico detalhado de combustível e consumo da moto.
* **Endpoints principais:** `GET /abastecimentos`, `POST /abastecimentos`, `PUT /abastecimentos/{id}`, `DELETE /abastecimentos/{id}`
* **Funcionamento:**
  - O usuário informa: data, quilometragem atual (`km_atual`), litros abastecidos, valor total pago, preço do litro e o nome do posto.
  - **Automação Financeira:** Ao criar um abastecimento, o sistema **gera automaticamente um lançamento de Despesa** no módulo de lançamentos na categoria "Combustível".
  - **Quilometragem:** O `km_atual` informado atualiza automaticamente a quilometragem da moto ativa.

---

## 6. 🔧 Módulo de Manutenções

* **Objetivo:** Controle de oficinas, peças trocadas e preventiva da moto.
* **Endpoints principais:** `GET /manutencoes`, `POST /manutencoes`, `PUT /manutencoes/{id}`, `DELETE /manutencoes/{id}`
* **Funcionamento:**
  - O usuário informa: data, tipo da manutenção (troca de óleo, relação, pneus, freios, etc.), descrição do serviço, valor pago, quilometragem atual (`km_atual`) e local/oficina.
  - **Automação Financeira:** Ao cadastrar uma manutenção, o sistema **cria automaticamente a Despesa financeira correspondente** vinculada à categoria correta.

---

## 7. 📊 Módulo Dashboard / Visão do Mês

* **Objetivo:** Consolidar e apresentar os indicadores chave de desempenho (KPIs) financeiros e operacionais do entregador.
* **Endpoints principais:** `GET /visao-mes`, `GET /indicadores/resumo`
* **Métricas Apresentadas:**
  - **Lucro Real:** $\text{Faturamento Bruto} - \text{Total de Despesas}$.
  - **Ticket Médio:** Valor médio faturado por corrida e por dia trabalhado.
  - **Desempenho por Dia da Semana:** Identificação visual do melhor e do pior dia para trabalhar.
  - **Rendimento da Moto:** Média de km por litro e custo por km rodado.
  - **Calendário Visual:** Exibição gráfica dos dias trabalhados no mês.

---

## 8. 🎯 Módulo de Metas

* **Objetivo:** Definir metas de ganho e limites de gastos para manter o planejamento financeiro em dia.
* **Endpoints principais:** `GET /metas`, `POST /metas`, `PUT /metas/{id}`, `DELETE /metas/{id}`, `GET /metas/alertas`
* **Tipos de Metas:**
  - **Receita Mensal:** Meta de faturamento bruto no mês.
  - **Lucro Mensal:** Meta de lucro líquido no mês.
  - **Teto de Despesa Mensal:** Limite máximo de gastos no mês.
  - **Meta Diária:** Objetivo de faturamento diário.
* **Status:** Backend 100% construído e testado. Frontend pendente de implementação das views/cards.
