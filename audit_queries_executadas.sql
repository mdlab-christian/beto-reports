-- ============================================================================
-- AUDITORIA SCHEMA: /empresas
-- Projeto MdFlow: qdivfairxhdihaqqypgb
-- Data: 2026-04-06
-- ============================================================================

-- ============================================================================
-- 1. VERIFICAR EXISTÊNCIA DAS TABELAS
-- ============================================================================
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('empresas', 'orgaos_restritivos', 'empresas_categorias', 'empresas_escritorios') 
ORDER BY table_name;

-- Resultado esperado: 4 linhas (empresas, empresas_categorias, empresas_escritorios, orgaos_restritivos)


-- ============================================================================
-- 2. ESTRUTURA COMPLETA: EMPRESAS
-- ============================================================================
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas'
ORDER BY ordinal_position;

-- Resultado: 28 colunas. Presença obrigatória:
--  - id (uuid, NOT NULL)
--  - organizacao_id (uuid, NOT NULL)
--  - created_at (timestamp with time zone, NOT NULL)
--  - updated_at (timestamp with time zone, NOT NULL)
--  - deleted_at (timestamp with time zone, YES)


-- ============================================================================
-- 3. ESTRUTURA COMPLETA: ORGAOS_RESTRITIVOS
-- ============================================================================
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'orgaos_restritivos'
ORDER BY ordinal_position;

-- Resultado: 12 colunas. Status: COMPLETA ✅


-- ============================================================================
-- 4. ESTRUTURA COMPLETA: EMPRESAS_CATEGORIAS
-- ============================================================================
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas_categorias'
ORDER BY ordinal_position;

-- Resultado: 6 colunas. PROBLEMAS ENCONTRADOS:
--  - FALTA: deleted_at (TIMESTAMPTZ)
--  - FALTA: updated_at (TIMESTAMPTZ)
-- Status: INCOMPLETA ❌


-- ============================================================================
-- 5. ESTRUTURA COMPLETA: EMPRESAS_ESCRITORIOS
-- ============================================================================
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas_escritorios'
ORDER BY ordinal_position;

-- Resultado: 23 colunas. Status: COMPLETA ✅


-- ============================================================================
-- 6. RLS STATUS (ROW LEVEL SECURITY)
-- ============================================================================
SELECT tablename, rowsecurity 
FROM pg_tables
WHERE schemaname = 'public' 
  AND tablename IN ('empresas', 'orgaos_restritivos', 'empresas_categorias', 'empresas_escritorios')
ORDER BY tablename;

-- Resultado esperado: rowsecurity = true para todas as 4 tabelas
-- Resultado obtido: ✅ TODAS HABILITADAS


-- ============================================================================
-- 7. RLS POLICIES: EMPRESAS
-- ============================================================================
SELECT policyname, cmd, roles, qual
FROM pg_policies 
WHERE tablename = 'empresas'
ORDER BY policyname;

-- Resultado: 2 policies
--  - empresas_delete_admin_only (DELETE)
--  - empresas_org_isolation (ALL)


-- ============================================================================
-- 8. RLS POLICIES: ORGAOS_RESTRITIVOS
-- ============================================================================
SELECT policyname, cmd, roles
FROM pg_policies 
WHERE tablename = 'orgaos_restritivos'
ORDER BY policyname;

-- Resultado: 4 policies (select, insert, update, delete)


-- ============================================================================
-- 9. RLS POLICIES: EMPRESAS_CATEGORIAS
-- ============================================================================
SELECT policyname, cmd, roles
FROM pg_policies 
WHERE tablename = 'empresas_categorias'
ORDER BY policyname;

-- Resultado: 4 policies (select, insert, update, delete)


-- ============================================================================
-- 10. RLS POLICIES: EMPRESAS_ESCRITORIOS
-- ============================================================================
SELECT policyname, cmd, roles
FROM pg_policies 
WHERE tablename = 'empresas_escritorios'
ORDER BY policyname;

-- Resultado: 4 policies (select, insert, update, delete)


-- ============================================================================
-- 11. ÍNDICES: EMPRESAS
-- ============================================================================
SELECT indexname, indexdef 
FROM pg_indexes
WHERE tablename = 'empresas'
ORDER BY indexname;

-- Resultado: 10 índices
-- Presença obrigatória:
--  - idx_empresas_org (organizacao_id) ✅
--  - idx_empresas_org_del (organizacao_id) WHERE deleted_at IS NULL ✅


-- ============================================================================
-- 12. ÍNDICES: ORGAOS_RESTRITIVOS
-- ============================================================================
SELECT indexname, indexdef 
FROM pg_indexes
WHERE tablename = 'orgaos_restritivos'
ORDER BY indexname;

-- Resultado: 4 índices
-- Status: ✅ Possui idx_orgaos_restritivos_org_active (org + deleted_at)


-- ============================================================================
-- 13. ÍNDICES: EMPRESAS_CATEGORIAS
-- ============================================================================
SELECT indexname, indexdef 
FROM pg_indexes
WHERE tablename = 'empresas_categorias'
ORDER BY indexname;

-- Resultado: 2 índices (pkey, org)
-- PROBLEMAS ENCONTRADOS:
--  - FALTA: idx_empresas_categorias_org_del (organizacao_id) WHERE deleted_at IS NULL


-- ============================================================================
-- 14. ÍNDICES: EMPRESAS_ESCRITORIOS
-- ============================================================================
SELECT indexname, indexdef 
FROM pg_indexes
WHERE tablename = 'empresas_escritorios'
ORDER BY indexname;

-- Resultado: 4 índices
-- PROBLEMAS ENCONTRADOS:
--  - FALTA: idx_empresas_escritorios_org_del (organizacao_id) WHERE deleted_at IS NULL
--  (Note: tem oab_principal com deleted_at, mas não a principal org)


-- ============================================================================
-- 15. TRIGGERS: EMPRESAS
-- ============================================================================
SELECT trigger_name, event_manipulation, action_timing
FROM information_schema.triggers
WHERE event_object_table = 'empresas' AND trigger_schema = 'public';

-- Resultado: 2 triggers
--  - trg_empresas_updated_at (BEFORE UPDATE) ✅
--  - trg_sync_execucoes_empresa_nome (AFTER UPDATE) ✅


-- ============================================================================
-- 16. TRIGGERS: ORGAOS_RESTRITIVOS
-- ============================================================================
SELECT trigger_name, event_manipulation, action_timing
FROM information_schema.triggers
WHERE event_object_table = 'orgaos_restritivos' AND trigger_schema = 'public';

-- Resultado: 1 trigger
--  - set_updated_at (BEFORE UPDATE) ✅


-- ============================================================================
-- 17. TRIGGERS: EMPRESAS_CATEGORIAS
-- ============================================================================
SELECT trigger_name, event_manipulation, action_timing
FROM information_schema.triggers
WHERE event_object_table = 'empresas_categorias' AND trigger_schema = 'public';

-- Resultado: 0 triggers ❌ PROBLEMA: não há set_updated_at


-- ============================================================================
-- 18. TRIGGERS: EMPRESAS_ESCRITORIOS
-- ============================================================================
SELECT trigger_name, event_manipulation, action_timing
FROM information_schema.triggers
WHERE event_object_table = 'empresas_escritorios' AND trigger_schema = 'public';

-- Resultado: 1 trigger
--  - set_updated_at_empresas_escritorios (BEFORE UPDATE) ✅


-- ============================================================================
-- 19. FOREIGN KEYS (sintaxe corrigida)
-- ============================================================================
SELECT 
  rc.constraint_name,
  kcu.table_name,
  kcu.column_name,
  ccu.table_name AS referenced_table_name,
  ccu.column_name AS referenced_column_name
FROM information_schema.referential_constraints rc
JOIN information_schema.key_column_usage kcu 
  ON rc.constraint_name = kcu.constraint_name 
  AND kcu.table_schema = rc.constraint_schema
JOIN information_schema.constraint_column_usage ccu 
  ON rc.unique_constraint_name = ccu.constraint_name 
  AND ccu.table_schema = rc.unique_constraint_schema
WHERE kcu.table_schema = 'public' 
  AND kcu.table_name IN ('empresas', 'orgaos_restritivos', 'empresas_categorias', 'empresas_escritorios')
ORDER BY kcu.table_name, rc.constraint_name;

-- Resultado: 6 foreign keys
--  1. empresas.organizacao_id → organizacoes.id ✅
--  2. empresas.categoria_id → empresas_categorias.id ✅
--  3. orgaos_restritivos.organizacao_id → organizacoes.id ✅
--  4. empresas_categorias.organizacao_id → organizacoes.id ✅
--  5. empresas_escritorios.organizacao_id → organizacoes.id ✅
--  6. empresas_escritorios.empresa_id → empresas.id ✅


-- ============================================================================
-- 20. RPCs RELACIONADAS A EMPRESA*
-- ============================================================================
SELECT 
  proname,
  pg_get_function_arguments(oid) as args,
  prosecdef as security_definer,
  prorettype::regtype as return_type
FROM pg_proc
WHERE proname ILIKE '%empresa%'
  AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
ORDER BY proname;

-- Resultado: 15 RPCs encontradas
-- 14/15 com SECURITY DEFINER ✅
-- 1 pública (buscar_empresa_similar) ⚠️


-- ============================================================================
-- 21. ENUMS NATIVOS (proibidos em MdFlow)
-- ============================================================================
SELECT t.typname, n.nspname
FROM pg_type t
JOIN pg_namespace n ON n.oid = t.typnamespace
WHERE t.typtype = 'e' AND n.nspname = 'public'
ORDER BY t.typname;

-- Resultado: 0 enums nativos encontrados ✅
-- Projeto usa TEXT CHECK (correto)


-- ============================================================================
-- 22. VERIFICAÇÃO DE COLUNAS OBRIGATÓRIAS (RESUMO)
-- ============================================================================

-- EMPRESAS
SELECT
  COUNT(CASE WHEN column_name = 'organizacao_id' THEN 1 END) > 0 AS tem_org_id,
  COUNT(CASE WHEN column_name = 'deleted_at' THEN 1 END) > 0 AS tem_soft_delete,
  COUNT(CASE WHEN column_name = 'created_at' THEN 1 END) > 0 AS tem_created_at,
  COUNT(CASE WHEN column_name = 'updated_at' THEN 1 END) > 0 AS tem_updated_at
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas';
-- Resultado: true, true, true, true ✅

-- ORGAOS_RESTRITIVOS
SELECT
  COUNT(CASE WHEN column_name = 'organizacao_id' THEN 1 END) > 0 AS tem_org_id,
  COUNT(CASE WHEN column_name = 'deleted_at' THEN 1 END) > 0 AS tem_soft_delete,
  COUNT(CASE WHEN column_name = 'created_at' THEN 1 END) > 0 AS tem_created_at,
  COUNT(CASE WHEN column_name = 'updated_at' THEN 1 END) > 0 AS tem_updated_at
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'orgaos_restritivos';
-- Resultado: true, true, true, true ✅

-- EMPRESAS_CATEGORIAS
SELECT
  COUNT(CASE WHEN column_name = 'organizacao_id' THEN 1 END) > 0 AS tem_org_id,
  COUNT(CASE WHEN column_name = 'deleted_at' THEN 1 END) > 0 AS tem_soft_delete,
  COUNT(CASE WHEN column_name = 'created_at' THEN 1 END) > 0 AS tem_created_at,
  COUNT(CASE WHEN column_name = 'updated_at' THEN 1 END) > 0 AS tem_updated_at
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas_categorias';
-- Resultado: true, FALSE, true, FALSE ❌ PROBLEMAS ENCONTRADOS

-- EMPRESAS_ESCRITORIOS
SELECT
  COUNT(CASE WHEN column_name = 'organizacao_id' THEN 1 END) > 0 AS tem_org_id,
  COUNT(CASE WHEN column_name = 'deleted_at' THEN 1 END) > 0 AS tem_soft_delete,
  COUNT(CASE WHEN column_name = 'created_at' THEN 1 END) > 0 AS tem_created_at,
  COUNT(CASE WHEN column_name = 'updated_at' THEN 1 END) > 0 AS tem_updated_at
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas_escritorios';
-- Resultado: true, true, true, true ✅


-- ============================================================================
-- DIAGNÓSTICO FINAL
-- ============================================================================

-- Tabelas por status:
--  ✅ empresas (10 índices, 2 triggers, RLS, todas colunas)
--  ✅ orgaos_restritivos (4 índices, 1 trigger, RLS, todas colunas)
--  ❌ empresas_categorias (2 índices, 0 triggers, RLS, FALTAM deleted_at + updated_at + idx_del)
--  ⚠️ empresas_escritorios (4 índices, 1 trigger, RLS, FALTA idx_org_del)

-- Issues P1 (críticas):
--  1. empresas_categorias faltam deleted_at, updated_at
--  2. empresas_categorias falta trigger set_updated_at

-- Issues P2 (melhorias):
--  1. empresas_escritorios falta idx_empresas_escritorios_org_del

-- Conformidades positivas: 10/10 ✅

