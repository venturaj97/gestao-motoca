# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Motoboys, entregadores de aplicativo (iFood, Rappi, Zé Delivery, Uber Flash, etc.) e autônomos sobre duas rodas que precisam controlar e maximizar o lucro real do seu trabalho diário.

## Product Purpose
Sistema de controle financeiro e gestão operacional para entregadores de aplicativo. Permite o acompanhamento preciso de ganhos por corrida/dia, despesas categorizadas (alimentação, manutenção, combustível, impostos), eficiência de combustível (KM/L e custo por KM), alertas preventivos de manutenção (odômetro/óleo) e controle de assinaturas (Plano PRO).

## Positioning
Controle financeiro descomplicado e hiper-focado na rotina dinâmica do motoboy, transformando dados brutos de rodagem e combustível em lucro líquido real em tempo real.

## Operating Context
Uso prioritariamente móvel e desktop em ambientes dinâmicos e rápidos (paradas entre entregas, postos de gasolina, oficinas), exigindo entradas rápidas de dados, visualização clara em telas pequenas e feedback imediato de métricas essenciais.

## Capabilities and Constraints
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PostgreSQL 16.
- **Frontend**: Vue 3 (Composition API), TypeScript, Vite, Pinia, Vue Router, Tailwind CSS.
- **Funcionalidades**: Dashboard financeiro consolidado, extrato de transações, relatórios inteligentes, lançamentos de ganhos/despesas/abastecimentos/manutenções, gestão de veículos vinculados, gerenciamento de assinaturas e planos PRO.
- **Infraestrutura**: Docker & Docker Compose.

## Brand Commitments
- Interface escura e moderna (Dark Mode prioritário), alto contraste, tipografia altamente legível e elementos interativos acessíveis para uso rápido no smartphone.
- Linguagem direta, amigável e adaptada ao vocabulário de entregadores.

## Evidence on Hand
- Código-fonte completo com Backend FastAPI (`/app`), Frontend Vue 3 + TypeScript (`/frontend`), Suíte de Testes Pytest (`/tests`) e Migrações Alembic (`/alembic`).

## Product Principles
1. **Velocidade de Registro**: Inserção de dados em poucos toques para não interromper a rotina de entregas.
2. **Lucro Real em Destaque**: Foco permanente no valor líquido restante após dedução de combustível, manutenção e custos operacionais.
3. **Clareza Visual & Ergonomia**: Componentes limpos com alto contraste, hierarquia visual objetiva e alvos de toque confortáveis.

## Accessibility & Inclusion
Layout responsivo mobile-first, suporte a alto contraste para visualização sob iluminação externa/luz solar e botões com áreas de clique generosas.
