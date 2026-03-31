-- ═══════════════════════════════════════════════════════════════════════════
-- VERIFICAÇÃO ADMIN: Tabela AUDIENCIAS
-- ═══════════════════════════════════════════════════════════════════════════
-- Execute este arquivo via pgAdmin ou psql do Supabase para confirmação total
-- Projeto: qdivfairxhdihaqqypgb (MdFlow Produção)
-- ═══════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────
-- 1. VERIFICAR SE RLS ESTÁ HABILITADO
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  tablename, 
  rowsecurity,
  CASE WHEN rowsecurity THEN '✅ RLS ENABLED' ELSE '❌ RLS DISABLED' END as status
FROM pg_tables
WHERE schemaname = 'public' AND tablename = 'audiencias';

-- Resultado esperado: rowsecurity = true

-- ─────────────────────────────────────────────────────────────────────────
-- 2. LISTAR TODAS AS POLICIES RLS
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  policyname,
  tablename,
  cmd,
  roles,
  qual,
  with_check
FROM pg_policies 
WHERE tablename = 'audiencias'
ORDER BY policyname;

-- Esperado: Policy com USING (organizacao_id = public.get_org_id())

-- ─────────────────────────────────────────────────────────────────────────
-- 3. VERIFICAR ÍNDICES EXISTENTES
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  tablename,
  indexname,
  indexdef,
  CASE 
    WHEN indexname ILIKE '%org%' THEN '✅ ÍNDICE ORG'
    WHEN indexname ILIKE '%processo%' THEN '📌 ÍNDICE PROCESSO'
    ELSE '📋 OUTRO'
  END as tipo
FROM pg_indexes
WHERE tablename = 'audiencias'
ORDER BY indexname;

-- Índices esperados (se faltarem, ver SQL de correção no relatório):
-- - idx_audiencias_org_id
-- - idx_audiencias_org_id_active (WHERE deleted_at IS NULL)

-- ─────────────────────────────────────────────────────────────────────────
-- 4. VERIFICAR TRIGGERS
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  trigger_name,
  event_manipulation,
  action_timing,
  action_statement,
  CASE 
    WHEN trigger_name ILIKE '%updated%' THEN '✅ UPDATED_AT TRIGGER'
    ELSE '📋 OUTRO'
  END as tipo
FROM information_schema.triggers
WHERE event_object_table = 'audiencias' 
  AND trigger_schema = 'public'
ORDER BY trigger_name;

-- Esperado: Trigger "set_updated_at" ou similar em UPDATE

-- ─────────────────────────────────────────────────────────────────────────
-- 5. VERIFICAR FOREIGN KEYS
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  constraint_name,
  table_name,
  column_name,
  referenced_table_name,
  referenced_column_name
FROM information_schema.referential_constraints rc
JOIN information_schema.key_column_usage kcu 
  ON rc.constraint_name = kcu.constraint_name
WHERE table_name = 'audiencias'
ORDER BY constraint_name;

-- Esperado: FKs para processos, usuarios, correspondentes, organizacoes

-- ─────────────────────────────────────────────────────────────────────────
-- 6. CONTAR REGISTROS E STATUS
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  COUNT(*) as total_registros,
  COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as registros_ativos,
  COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as registros_deletados,
  COUNT(DISTINCT organizacao_id) as organizacoes_presentes
FROM public.audiencias;

-- ─────────────────────────────────────────────────────────────────────────
-- 7. VERIFICAR DISTRIBUIÇÃO POR ORGANIZAÇÃO (EXEMPLO: MIDAS)
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  organizacao_id,
  COUNT(*) as total,
  COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as ativos,
  COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as deletados
FROM public.audiencias
GROUP BY organizacao_id
ORDER BY total DESC;

-- ─────────────────────────────────────────────────────────────────────────
-- 8. VERIFICAR CONSTRAINT: deleted_at IS NULL para queries normais
-- ─────────────────────────────────────────────────────────────────────────

-- Queries devem filtrar ativos assim:
SELECT 
  COUNT(*) as audiencias_ativas_midas
FROM public.audiencias
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND deleted_at IS NULL;

-- ─────────────────────────────────────────────────────────────────────────
-- 9. TESTAR PERFORMANCE DO ÍNDICE (se existir)
-- ─────────────────────────────────────────────────────────────────────────

EXPLAIN ANALYZE
SELECT id, data_audiencia, status
FROM public.audiencias
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND deleted_at IS NULL
ORDER BY data_audiencia DESC
LIMIT 50;

-- Análise: 
-- - Se resultado menciona "Index Scan" → ✅ Índice está sendo usado
-- - Se resultado menciona "Seq Scan" → ❌ Índice ESTÁ FALTANDO (ver SQL de correção)

-- ─────────────────────────────────────────────────────────────────────────
-- 10. VERIFICAR TIPOS DE DADOS (ENUM vs TEXT CHECK)
-- ─────────────────────────────────────────────────────────────────────────

SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'audiencias'
ORDER BY ordinal_position;

-- Análise de coluna tipo/modalidade/status:
-- - data_type = 'text' → ✅ TEXT CHECK (correto)
-- - data_type = 'enum' ou 'user-defined' → ❌ ENUM NATIVO (violação de padrão)

-- ─────────────────────────────────────────────────────────────────────────
-- RESUMO: Matriz de Conformidade
-- ─────────────────────────────────────────────────────────────────────────

WITH checklist AS (
  SELECT 'RLS Habilitado' as item, 
    (SELECT rowsecurity FROM pg_tables WHERE tablename='audiencias')::text as status
  UNION ALL
  SELECT 'Índice org_id',
    CASE WHEN EXISTS(SELECT 1 FROM pg_indexes WHERE tablename='audiencias' AND indexname ILIKE '%org%') 
      THEN '✅' ELSE '❌' END
  UNION ALL
  SELECT 'Trigger updated_at',
    CASE WHEN EXISTS(SELECT 1 FROM information_schema.triggers 
      WHERE event_object_table='audiencias' AND trigger_name ILIKE '%updated%') 
      THEN '✅' ELSE '❌' END
  UNION ALL
  SELECT 'Soft delete (deleted_at)',
    CASE WHEN EXISTS(SELECT 1 FROM information_schema.columns 
      WHERE table_name='audiencias' AND column_name='deleted_at') 
      THEN '✅' ELSE '❌' END
  UNION ALL
  SELECT 'FK: processo_id',
    CASE WHEN EXISTS(SELECT 1 FROM information_schema.referential_constraints 
      WHERE table_name='audiencias' AND column_name='processo_id') 
      THEN '✅' ELSE '❌' END
)
SELECT item, status FROM checklist;

