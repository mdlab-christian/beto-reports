================================================================================
--                   QUERIES PRONTAS PARA EXECUTAR
--              ICP Telemetria — Auditoria Supabase MdFlow
================================================================================
-- Org Teste: 55a0c7ba-1a23-4ae1-b69b-a13811324735
-- Data: 2026-04-06
================================================================================

-- ============================================================================
-- 1. AUDIT: Cobertura de dados demográficos em CLIENTES
-- ============================================================================
SELECT 
  COUNT(*) as total_clientes,
  COUNT(CASE WHEN data_nascimento IS NOT NULL THEN 1 END) as com_data_nasc,
  ROUND(COUNT(CASE WHEN data_nascimento IS NOT NULL THEN 1 END)::NUMERIC / COUNT(*) * 100, 1) as pct_data_nasc,
  COUNT(CASE WHEN profissao IS NOT NULL THEN 1 END) as com_profissao,
  ROUND(COUNT(CASE WHEN profissao IS NOT NULL THEN 1 END)::NUMERIC / COUNT(*) * 100, 1) as pct_profissao,
  COUNT(CASE WHEN endereco_uf IS NOT NULL THEN 1 END) as com_uf,
  ROUND(COUNT(CASE WHEN endereco_uf IS NOT NULL THEN 1 END)::NUMERIC / COUNT(*) * 100, 1) as pct_uf,
  COUNT(CASE WHEN renda_mensal IS NOT NULL THEN 1 END) as com_renda,
  COUNT(CASE WHEN valor_total_estimado_recuperavel IS NOT NULL THEN 1 END) as com_valor_recup
FROM clientes
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND deleted_at IS NULL;

-- ============================================================================
-- 2. AUDIT: Cobertura de dados de PROCESSOS
-- ============================================================================
SELECT 
  COUNT(*) as total_processos,
  COUNT(CASE WHEN valor_causa IS NOT NULL THEN 1 END) as com_valor_causa,
  ROUND(COUNT(CASE WHEN valor_causa IS NOT NULL THEN 1 END)::NUMERIC / COUNT(*) * 100, 1) as pct_valor_causa,
  COUNT(CASE WHEN fase_processual IS NOT NULL THEN 1 END) as com_fase,
  ROUND(COUNT(CASE WHEN fase_processual IS NOT NULL THEN 1 END)::NUMERIC / COUNT(*) * 100, 1) as pct_fase,
  COUNT(CASE WHEN acordo_candidato = true THEN 1 END) as candidatos_acordo,
  COUNT(CASE WHEN acordo_propensao_pct IS NOT NULL THEN 1 END) as com_propensao_acordo,
  COUNT(CASE WHEN chance_sucesso_pct IS NOT NULL THEN 1 END) as com_chance_sucesso
FROM processos
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND deleted_at IS NULL;

-- ============================================================================
-- 3. AUDIT: Cobertura em LEADS
-- ============================================================================
SELECT 
  COUNT(*) as total_leads,
  COUNT(CASE WHEN data_nascimento IS NOT NULL THEN 1 END) as com_data_nasc,
  ROUND(COUNT(CASE WHEN data_nascimento IS NOT NULL THEN 1 END)::NUMERIC / COUNT(*) * 100, 1) as pct_data_nasc,
  COUNT(CASE WHEN profissao IS NOT NULL THEN 1 END) as com_profissao,
  COUNT(CASE WHEN endereco_estado IS NOT NULL THEN 1 END) as com_estado,
  COUNT(CASE WHEN valor_estimado IS NOT NULL THEN 1 END) as com_valor_est,
  COUNT(CASE WHEN icp_score IS NOT NULL THEN 1 END) as com_icp_score
FROM leads
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND deleted_at IS NULL;

-- ============================================================================
-- 4. RPC: Calcular valor recuperável total por cliente (SUM de processos)
-- ============================================================================
-- CRIAR RPC (copiar para Supabase SQL Editor):

CREATE OR REPLACE FUNCTION public.fn_cliente_valor_recuperavel_total(
  p_cliente_id UUID
)
RETURNS NUMERIC AS $$
BEGIN
  RETURN COALESCE(
    SUM(COALESCE(p.valor_causa, 0))
    FROM processos p
    WHERE p.cliente_id = p_cliente_id
      AND p.organizacao_id = auth.jwt() ->> 'org_id'
      AND p.deleted_at IS NULL,
    0::NUMERIC
  );
END;
$$ LANGUAGE PLPGSQL SECURITY DEFINER SET search_path = public;

-- TESTAR RPC:
SELECT 
  c.id,
  c.nome,
  public.fn_cliente_valor_recuperavel_total(c.id) as valor_total_processos
FROM clientes c
WHERE c.organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND c.deleted_at IS NULL
LIMIT 10;

-- ============================================================================
-- 5. SAMPLE: Dados reais de cliente com todos os fatores ICP
-- ============================================================================
SELECT 
  c.id,
  c.nome,
  EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.data_nascimento))::INT as idade_anos,
  c.profissao,
  c.endereco_uf,
  c.estado_civil,
  c.renda_mensal,
  COUNT(p.id) as total_processos,
  SUM(COALESCE(p.valor_causa, 0)) as valor_total_causa,
  MAX(p.fase_processual) as ultima_fase,
  SUM(CASE WHEN p.acordo_candidato = true THEN 1 ELSE 0 END) as processos_candidatos_acordo,
  MAX(p.created_at) as primeiro_processo_em,
  MAX(p.updated_at) as ultimo_update
FROM clientes c
LEFT JOIN processos p ON p.cliente_id = c.id 
  AND p.organizacao_id = c.organizacao_id
  AND p.deleted_at IS NULL
WHERE c.organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND c.deleted_at IS NULL
GROUP BY c.id, c.nome, c.data_nascimento, c.profissao, c.endereco_uf, c.estado_civil, c.renda_mensal
LIMIT 10;

-- ============================================================================
-- 6. AGREGAÇÃO ICP por período (base para tabela icp_telemetria_snapshots)
-- ============================================================================
SELECT 
  DATE(c.created_at) as data_snapshot,
  COUNT(DISTINCT c.id) as total_clientes,
  ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.data_nascimento)))::NUMERIC, 1) as idade_media,
  COUNT(CASE WHEN c.profissao IS NOT NULL THEN 1 END) as clientes_com_profissao,
  COUNT(DISTINCT c.endereco_uf) as estados_unicos,
  SUM(COALESCE(p.valor_causa, 0)) as valor_causa_total,
  COUNT(DISTINCT CASE WHEN p.acordo_candidato = true THEN p.id END) as processos_acordo,
  ROUND(SUM(COALESCE(p.valor_causa, 0))::NUMERIC / COUNT(DISTINCT c.id), 2) as valor_medio_por_cliente
FROM clientes c
LEFT JOIN processos p ON p.cliente_id = c.id 
  AND p.organizacao_id = c.organizacao_id
  AND p.deleted_at IS NULL
WHERE c.organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND c.deleted_at IS NULL
  AND c.created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(c.created_at)
ORDER BY data_snapshot DESC;

-- ============================================================================
-- 7. VALIDAÇÃO: Integridade de ICP_SCORE em LEADS
-- ============================================================================
SELECT 
  icp_score,
  COUNT(*) as total_leads,
  MIN(created_at) as primeiro_lead,
  MAX(created_at) as ultimo_lead
FROM leads
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND deleted_at IS NULL
GROUP BY icp_score
ORDER BY icp_score DESC;

-- ============================================================================
-- 8. VERIFICAÇÃO: Campos de MDZAP para enriquecimento
-- ============================================================================
-- Ver estrutura de mdzap_lead_memory
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'mdzap_lead_memory'
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- ============================================================================
-- 9. INSIGHT: Correlação entre ICP_SCORE de leads e valor total de processos
-- ============================================================================
SELECT 
  l.icp_score,
  COUNT(DISTINCT l.id) as total_leads_com_score,
  COUNT(DISTINCT CASE WHEN l.cliente_id IS NOT NULL THEN l.cliente_id END) as leads_convertidos,
  ROUND(
    COUNT(DISTINCT CASE WHEN l.cliente_id IS NOT NULL THEN l.cliente_id END)::NUMERIC 
    / COUNT(DISTINCT l.id) * 100, 
    1
  ) as taxa_conversao_pct,
  SUM(COALESCE(p.valor_causa, 0)) as valor_total_processos
FROM leads l
LEFT JOIN clientes c ON c.id = l.cliente_id 
  AND c.organizacao_id = l.organizacao_id
  AND c.deleted_at IS NULL
LEFT JOIN processos p ON p.cliente_id = c.id 
  AND p.organizacao_id = l.organizacao_id
  AND p.deleted_at IS NULL
WHERE l.organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735'
  AND l.deleted_at IS NULL
GROUP BY l.icp_score
ORDER BY l.icp_score DESC;

-- ============================================================================
-- 10. DDL: Tabela icp_telemetria_snapshots (pronto para executar)
-- ============================================================================
-- CRIAR TABELA:

CREATE TABLE IF NOT EXISTS public.icp_telemetria_snapshots (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organizacao_id UUID NOT NULL REFERENCES public.organizacoes(id) ON DELETE CASCADE,
  data_snapshot DATE NOT NULL,
  
  -- Foreign keys (opcionais, para drill-down)
  lead_id UUID REFERENCES public.leads(id),
  cliente_id UUID REFERENCES public.clientes(id),
  processo_id UUID REFERENCES public.processos(id),
  
  -- Demográfico
  idade_anos SMALLINT,
  profissao TEXT,
  estado_uf TEXT,
  sexo TEXT,
  estado_civil TEXT,
  
  -- Financeiro
  valor_causa NUMERIC(15,2),
  valor_estimado_recuperavel NUMERIC(15,2),
  renda_mensal NUMERIC(15,2),
  
  -- Processual
  fase_processual TEXT,
  tempo_dias_caso INTEGER,
  agreement_propensity_pct SMALLINT,
  ia_success_chance_pct SMALLINT,
  
  -- Scoring
  icp_score SMALLINT,
  icp_factors JSONB,  -- {"idade": 8, "valor": 9, "profissao": 7}
  
  -- Audit
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  deleted_at TIMESTAMPTZ
);

-- CRIAR ÍNDICES:
CREATE INDEX IF NOT EXISTS idx_icp_snap_org_date 
  ON public.icp_telemetria_snapshots(organizacao_id, data_snapshot);

CREATE INDEX IF NOT EXISTS idx_icp_snap_cliente 
  ON public.icp_telemetria_snapshots(cliente_id) 
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_icp_snap_score 
  ON public.icp_telemetria_snapshots(icp_score) 
  WHERE deleted_at IS NULL;

-- RLS (padrão tenant isolation):
ALTER TABLE public.icp_telemetria_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation" 
  ON public.icp_telemetria_snapshots 
  FOR ALL USING (organizacao_id = public.get_org_id());

-- TRIGGER para updated_at:
CREATE TRIGGER set_updated_at_icp_snapshots 
  BEFORE UPDATE ON public.icp_telemetria_snapshots 
  FOR EACH ROW 
  EXECUTE FUNCTION public.update_updated_at_column();

================================================================================
-- FIM DAS QUERIES
================================================================================
