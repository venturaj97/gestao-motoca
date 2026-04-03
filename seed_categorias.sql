-- Script para popular a tabela de categorias com valores padrão
-- Uso: psql -U seu_usuario -d seu_banco -f seed_categorias.sql

INSERT INTO categorias (nome, tipo, ativo, data_criacao) VALUES
-- GANHOS (Entradas)
('Entregas (App)', 'GANHO', true, NOW()),
('Passageiros (App)', 'GANHO', true, NOW()),
('Entregas Particulares', 'GANHO', true, NOW()),
('Venda de Ativos', 'GANHO', true, NOW()),
('Outros Ganhos', 'GANHO', true, NOW()),

-- DESPESAS (Saídas)
('Combustível', 'DESPESA', true, NOW()),
('Troca de Óleo', 'DESPESA', true, NOW()),
('Manutenção Preventiva', 'DESPESA', true, NOW()),
('Manutenção Corretiva', 'DESPESA', true, NOW()),
('Pneus', 'DESPESA', true, NOW()),
('Relação (Cadeia/Coroa/Pinhão)', 'DESPESA', true, NOW()),
('Lavagem / Estética', 'DESPESA', true, NOW()),
('Seguro', 'DESPESA', true, NOW()),
('IPVA / Licenciamento', 'DESPESA', true, NOW()),
('Multas', 'DESPESA', true, NOW()),
('Equipamentos (Capacete/Capa)', 'DESPESA', true, NOW()),
('Acessórios', 'DESPESA', true, NOW()),
('Estacionamento', 'DESPESA', true, NOW()),
('Outras Despesas', 'DESPESA', true, NOW())
ON CONFLICT (nome, tipo) DO NOTHING;
