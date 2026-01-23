# 🛵 Gestão Motoca

O **Gestão Motoca** é um sistema de gestão financeira inteligente desenvolvido especificamente para motoboys e entregadores que buscam clareza sobre seus ganhos reais. 

O projeto resolve o problema da "falsa percepção de lucro", automatizando a separação de valores para manutenção, financiamento da moto e lucro líquido.

---

## 🚀 O Problema
Muitos entregadores acreditam que o valor bruto recebido no dia é lucro. No entanto, sem uma reserva para pneus, óleo e a parcela da moto, o profissional pode acabar "pagando para trabalhar". O Gestão Motoca automatiza essa conta.

## ✨ Funcionalidades Principais
- **Divisão Automática:** Ao lançar um ganho, o sistema separa automaticamente as porcentagens para Manutenção, Financiamento e Lucro.
- **Alertas de Manutenção:** Monitoramento do KM para trocas de óleo e revisões.
- **Gestão de "Caixinhas":** Saldo individualizado para cada categoria de custo.
- **Templates de Motos:** Configurações pré-definidas para os modelos mais usados (CG 160, Factor, Biz, etc).

## 🛠️ Tecnologias (Tech Stack)
- **Backend:** Python (FastAPI) / PHP (Laravel)
- **Frontend:** Vue.js / React (Quasar Framework)
- **Banco de Dados:** PostgreSQL
- **Infraestrutura:** AWS (Lambda, RDS, Amplify)

---

## 📋 Como funciona a lógica?
O sistema utiliza uma regra de distribuição baseada no perfil do usuário. Exemplo padrão:
* **25%** Reserva de Manutenção (Óleo, pneus, relação)
* **36%** Provisão de Financiamento
* **39%** Lucro Real (Dinheiro livre)

---

## 🛠️ Como Contribuir
Este é um projeto em desenvolvimento por um estudante de Ciência da Computação apaixonado por resolver problemas reais com tecnologia.

1. Faça um **Fork** do projeto.
2. Crie uma **Branch** para sua feature (`git checkout -b feature/NovaFeature`).
3. Dê um **Commit** nas suas alterações (`git commit -m 'Adicionando nova feature'`).
4. Dê um **Push** na sua Branch (`git push origin feature/NovaFeature`).
5. Abra um **Pull Request**.

---
Desenvolvido com ☕ e código.
