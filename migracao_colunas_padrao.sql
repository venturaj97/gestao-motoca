-- Script SQL de Atualização das 4 Colunas Padrão (id, situacao, data, data_criacao)
-- Executar no banco de dados PostgreSQL do Gestão Motoca

DO $$
DECLARE
    t TEXT;
    tabelas TEXT[] := ARRAY[
        'usuarios',
        'motos_usuario',
        'categorias',
        'lancamentos',
        'abastecimentos',
        'manutencoes',
        'metas',
        'recuperacoes_senha'
    ];
BEGIN
    FOR t IN SELECT unnest(tabelas) LOOP
        -- 1. Coluna situacao (Soft Delete: 'ATIVO' / 'INATIVO')
        EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS situacao VARCHAR(20) DEFAULT ''ATIVO'' NOT NULL', t);
        
        -- 2. Coluna data (Timestamp de Alteração/Atualização)
        EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS data TIMESTAMPTZ DEFAULT NOW() NOT NULL', t);

        -- 3. Renomeia data_cadastro para data_criacao se existir na tabela (ex: motos_usuario)
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t AND column_name = 'data_cadastro') THEN
            EXECUTE format('ALTER TABLE %I RENAME COLUMN data_cadastro TO data_criacao', t);
        END IF;

        -- 4. Coluna data_criacao (Timestamp de Criação Inalterável)
        EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS data_criacao TIMESTAMPTZ DEFAULT NOW() NOT NULL', t);
    END LOOP;
END $$;
