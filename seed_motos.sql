-- ============================================================
--  SEED: Catálogo de motos para motoboys
--  Tabelas: motos_modelos + motos_versoes
--  Para rodar: psql -d gestao_motoca -U motoca -f seed_motos.sql
-- ============================================================

-- Garante que não vai duplicar se rodar mais de uma vez
INSERT INTO motos_modelos (marca, modelo, cilindrada_cc, ativo) VALUES
  -- HONDA
  ('Honda', 'CG 160 Start',       160, true),
  ('Honda', 'CG 160 Fan',         160, true),
  ('Honda', 'CG 160 Titan',       160, true),
  ('Honda', 'CG 160 Cargo',       160, true),
  ('Honda', 'CB 300R',            300, true),
  ('Honda', 'Biz 125',            125, true),
  ('Honda', 'Pop 110i',           110, true),

  -- YAMAHA
  ('Yamaha', 'Factor 125',        125, true),
  ('Yamaha', 'Factor 150',        150, true),
  ('Yamaha', 'Fazer 250',         250, true),
  ('Yamaha', 'YBR 125',           125, true),

  -- SUZUKI
  ('Suzuki', 'EN 125',            125, true),

  -- KASINSKI
  ('Kasinski', 'Mirage 150',      150, true),

  -- DAFRA
  ('Dafra', 'Speed 150',          150, true)

ON CONFLICT ON CONSTRAINT uq_motos_modelos_marca_modelo DO NOTHING;


-- ============================================================
--  VERSÕES (anos) por modelo
--  tipo_combustivel: FLEX / GASOLINA
--  consumo_medio_km_l: média de uso real em cidade por motoboy
--  capacidade_tanque_l: litros do tanque
-- ============================================================

INSERT INTO motos_versoes (moto_modelo_id, ano, tipo_combustivel, consumo_medio_km_l, capacidade_tanque_l, ativo)
SELECT m.id, v.ano, v.combustivel, v.consumo, v.tanque, true
FROM (VALUES
  -- Honda CG 160 Start
  ('Honda', 'CG 160 Start', 2016, 'FLEX', 38.5, 13.0),
  ('Honda', 'CG 160 Start', 2017, 'FLEX', 38.5, 13.0),
  ('Honda', 'CG 160 Start', 2018, 'FLEX', 38.5, 13.0),
  ('Honda', 'CG 160 Start', 2019, 'FLEX', 38.5, 13.0),
  ('Honda', 'CG 160 Start', 2020, 'FLEX', 40.0, 13.0),
  ('Honda', 'CG 160 Start', 2021, 'FLEX', 40.0, 13.0),
  ('Honda', 'CG 160 Start', 2022, 'FLEX', 40.0, 13.0),
  ('Honda', 'CG 160 Start', 2023, 'FLEX', 41.0, 13.0),
  ('Honda', 'CG 160 Start', 2024, 'FLEX', 41.0, 13.0),

  -- Honda CG 160 Fan
  ('Honda', 'CG 160 Fan',  2016, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Fan',  2017, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Fan',  2018, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Fan',  2019, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Fan',  2020, 'FLEX', 37.5, 13.0),
  ('Honda', 'CG 160 Fan',  2021, 'FLEX', 37.5, 13.0),
  ('Honda', 'CG 160 Fan',  2022, 'FLEX', 37.5, 13.0),
  ('Honda', 'CG 160 Fan',  2023, 'FLEX', 38.0, 13.0),
  ('Honda', 'CG 160 Fan',  2024, 'FLEX', 38.0, 13.0),

  -- Honda CG 160 Titan
  ('Honda', 'CG 160 Titan', 2016, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Titan', 2017, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Titan', 2018, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Titan', 2019, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Titan', 2020, 'FLEX', 36.5, 13.0),
  ('Honda', 'CG 160 Titan', 2021, 'FLEX', 36.5, 13.0),
  ('Honda', 'CG 160 Titan', 2022, 'FLEX', 36.5, 13.0),
  ('Honda', 'CG 160 Titan', 2023, 'FLEX', 37.0, 13.0),
  ('Honda', 'CG 160 Titan', 2024, 'FLEX', 37.0, 13.0),

  -- Honda CG 160 Cargo (muito usada por motoboys)
  ('Honda', 'CG 160 Cargo', 2018, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Cargo', 2019, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Cargo', 2020, 'FLEX', 35.0, 13.0),
  ('Honda', 'CG 160 Cargo', 2021, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Cargo', 2022, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Cargo', 2023, 'FLEX', 36.0, 13.0),
  ('Honda', 'CG 160 Cargo', 2024, 'FLEX', 36.0, 13.0),

  -- Honda CB 300R
  ('Honda', 'CB 300R', 2015, 'GASOLINA', 28.0, 13.5),
  ('Honda', 'CB 300R', 2016, 'GASOLINA', 28.0, 13.5),
  ('Honda', 'CB 300R', 2017, 'GASOLINA', 28.0, 13.5),
  ('Honda', 'CB 300R', 2018, 'GASOLINA', 29.0, 13.5),
  ('Honda', 'CB 300R', 2019, 'GASOLINA', 29.0, 13.5),
  ('Honda', 'CB 300R', 2020, 'GASOLINA', 30.0, 13.5),
  ('Honda', 'CB 300R', 2021, 'GASOLINA', 30.0, 13.5),
  ('Honda', 'CB 300R', 2022, 'GASOLINA', 30.0, 13.5),
  ('Honda', 'CB 300R', 2023, 'GASOLINA', 31.0, 13.5),
  ('Honda', 'CB 300R', 2024, 'GASOLINA', 31.0, 13.5),

  -- Honda Biz 125
  ('Honda', 'Biz 125', 2015, 'FLEX', 42.0, 5.0),
  ('Honda', 'Biz 125', 2016, 'FLEX', 42.0, 5.0),
  ('Honda', 'Biz 125', 2017, 'FLEX', 42.0, 5.0),
  ('Honda', 'Biz 125', 2018, 'FLEX', 42.0, 5.0),
  ('Honda', 'Biz 125', 2019, 'FLEX', 43.0, 5.0),
  ('Honda', 'Biz 125', 2020, 'FLEX', 43.0, 5.0),
  ('Honda', 'Biz 125', 2021, 'FLEX', 43.0, 5.0),
  ('Honda', 'Biz 125', 2022, 'FLEX', 44.0, 5.0),
  ('Honda', 'Biz 125', 2023, 'FLEX', 44.0, 5.0),
  ('Honda', 'Biz 125', 2024, 'FLEX', 44.0, 5.0),

  -- Honda Pop 110i
  ('Honda', 'Pop 110i', 2016, 'FLEX', 45.0, 4.2),
  ('Honda', 'Pop 110i', 2017, 'FLEX', 45.0, 4.2),
  ('Honda', 'Pop 110i', 2018, 'FLEX', 45.0, 4.2),
  ('Honda', 'Pop 110i', 2019, 'FLEX', 46.0, 4.2),
  ('Honda', 'Pop 110i', 2020, 'FLEX', 46.0, 4.2),
  ('Honda', 'Pop 110i', 2021, 'FLEX', 46.0, 4.2),
  ('Honda', 'Pop 110i', 2022, 'FLEX', 47.0, 4.2),
  ('Honda', 'Pop 110i', 2023, 'FLEX', 47.0, 4.2),
  ('Honda', 'Pop 110i', 2024, 'FLEX', 47.0, 4.2),

  -- Yamaha Factor 125
  ('Yamaha', 'Factor 125', 2016, 'FLEX', 40.0, 12.0),
  ('Yamaha', 'Factor 125', 2017, 'FLEX', 40.0, 12.0),
  ('Yamaha', 'Factor 125', 2018, 'FLEX', 40.0, 12.0),
  ('Yamaha', 'Factor 125', 2019, 'FLEX', 40.5, 12.0),
  ('Yamaha', 'Factor 125', 2020, 'FLEX', 40.5, 12.0),
  ('Yamaha', 'Factor 125', 2021, 'FLEX', 40.5, 12.0),
  ('Yamaha', 'Factor 125', 2022, 'FLEX', 41.0, 12.0),
  ('Yamaha', 'Factor 125', 2023, 'FLEX', 41.0, 12.0),
  ('Yamaha', 'Factor 125', 2024, 'FLEX', 41.0, 12.0),

  -- Yamaha Factor 150
  ('Yamaha', 'Factor 150', 2016, 'FLEX', 38.0, 12.0),
  ('Yamaha', 'Factor 150', 2017, 'FLEX', 38.0, 12.0),
  ('Yamaha', 'Factor 150', 2018, 'FLEX', 38.0, 12.0),
  ('Yamaha', 'Factor 150', 2019, 'FLEX', 38.5, 12.0),
  ('Yamaha', 'Factor 150', 2020, 'FLEX', 38.5, 12.0),
  ('Yamaha', 'Factor 150', 2021, 'FLEX', 38.5, 12.0),
  ('Yamaha', 'Factor 150', 2022, 'FLEX', 39.0, 12.0),
  ('Yamaha', 'Factor 150', 2023, 'FLEX', 39.0, 12.0),
  ('Yamaha', 'Factor 150', 2024, 'FLEX', 39.0, 12.0),

  -- Yamaha Fazer 250
  ('Yamaha', 'Fazer 250', 2015, 'FLEX', 25.0, 18.0),
  ('Yamaha', 'Fazer 250', 2016, 'FLEX', 25.0, 18.0),
  ('Yamaha', 'Fazer 250', 2017, 'FLEX', 25.5, 18.0),
  ('Yamaha', 'Fazer 250', 2018, 'FLEX', 25.5, 18.0),
  ('Yamaha', 'Fazer 250', 2019, 'FLEX', 26.0, 18.0),
  ('Yamaha', 'Fazer 250', 2020, 'FLEX', 26.0, 18.0),
  ('Yamaha', 'Fazer 250', 2021, 'FLEX', 26.0, 18.0),
  ('Yamaha', 'Fazer 250', 2022, 'FLEX', 26.5, 18.0),
  ('Yamaha', 'Fazer 250', 2023, 'FLEX', 26.5, 18.0),

  -- Yamaha YBR 125
  ('Yamaha', 'YBR 125', 2015, 'FLEX', 42.0, 11.0),
  ('Yamaha', 'YBR 125', 2016, 'FLEX', 42.0, 11.0),
  ('Yamaha', 'YBR 125', 2017, 'FLEX', 42.0, 11.0),
  ('Yamaha', 'YBR 125', 2018, 'FLEX', 42.5, 11.0),
  ('Yamaha', 'YBR 125', 2019, 'FLEX', 42.5, 11.0),

  -- Suzuki EN 125
  ('Suzuki', 'EN 125', 2015, 'GASOLINA', 38.0, 13.5),
  ('Suzuki', 'EN 125', 2016, 'GASOLINA', 38.0, 13.5),
  ('Suzuki', 'EN 125', 2017, 'GASOLINA', 38.0, 13.5),
  ('Suzuki', 'EN 125', 2018, 'GASOLINA', 38.5, 13.5),
  ('Suzuki', 'EN 125', 2019, 'GASOLINA', 38.5, 13.5),
  ('Suzuki', 'EN 125', 2020, 'GASOLINA', 39.0, 13.5),
  ('Suzuki', 'EN 125', 2021, 'GASOLINA', 39.0, 13.5),
  ('Suzuki', 'EN 125', 2022, 'GASOLINA', 39.0, 13.5),

  -- Kasinski Mirage 150
  ('Kasinski', 'Mirage 150', 2015, 'GASOLINA', 35.0, 10.0),
  ('Kasinski', 'Mirage 150', 2016, 'GASOLINA', 35.0, 10.0),
  ('Kasinski', 'Mirage 150', 2017, 'GASOLINA', 35.0, 10.0),

  -- Dafra Speed 150
  ('Dafra', 'Speed 150', 2015, 'GASOLINA', 33.0, 12.0),
  ('Dafra', 'Speed 150', 2016, 'GASOLINA', 33.0, 12.0),
  ('Dafra', 'Speed 150', 2017, 'GASOLINA', 33.5, 12.0),
  ('Dafra', 'Speed 150', 2018, 'GASOLINA', 33.5, 12.0)

) AS v(marca, modelo, ano, combustivel, consumo, tanque)
JOIN motos_modelos m
  ON m.marca = v.marca AND m.modelo = v.modelo
ON CONFLICT ON CONSTRAINT uq_motos_versoes_modelo_ano DO NOTHING;

-- Verificação rápida
SELECT
  m.marca,
  m.modelo,
  COUNT(v.id) AS total_anos,
  MIN(v.ano)  AS ano_min,
  MAX(v.ano)  AS ano_max
FROM motos_modelos m
LEFT JOIN motos_versoes v ON v.moto_modelo_id = m.id
GROUP BY m.marca, m.modelo
ORDER BY m.marca, m.modelo;
