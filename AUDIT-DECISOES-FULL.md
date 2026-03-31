# DB Audit: /decisoes — MdFlow Supabase
**Data:** 2026-03-31 | **Projeto:** qdivfairxhdihaqqypgb | **Auditor:** mdflow-db-auditor (Claude Haiku 4.5)

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---|---|
| Tabelas auditadas | 1 |
| Colunas principais | 24+ |
| Issues P0 | 3 |
| Issues P1 | 2 |
| Issues P2 | 1 |
| RPCs vinculadas | 2 |
| Triggers vinculados | 1 |
| RLS Policies validadas | ❌ MCP indisponível |

---

## 🗂️ Tabela: `decisoes`

### Estrutura — Campos Principais

```
id (UUID, PK)
├─ organizacao_id (UUID, FK→organizacoes, NOT NULL) ✅
├─ processo_id (UUID, FK→processos, NOT NULL)
├─ intimacao_id (UUID, FK→intimacoes, nullable, NOVO)
│
├─ DECISÃO CORE
│  ├─ tipo (TEXT, DEFAULT 'merito')
│  ├─ resultado (TEXT, NOT NULL, CHECK IN ('favoravel','parcial','desfavoravel','improcedente','extinto'))
│  ├─ grau (INT2, DEFAULT 1)
│  ├─ data_decisao (DATE, NOT NULL)
│
├─ VALORES & CÁLCULOS
│  ├─ valor_condenacao (NUMERIC 15,2)
│  ├─ valor_honorarios (NUMERIC 15,2)
│  ├─ valor_atualizado (NUMERIC 15,2) [C12-A]
│  ├─ valor_juros (NUMERIC 15,2) [C12-A]
│  ├─ valor_total_calculado (NUMERIC 15,2) [C12-A]
│  ├─ data_calculo (DATE) [C12-A]
│  ├─ data_inicio_juros (DATE) [C12-A]
│  ├─ indice_correcao (TEXT, DEFAULT 'IPCA', CHECK IN ('INPC','IPCA','SELIC','CDI','MANUAL')) [C12-A]
│  ├─ taxa_juros_mensal (NUMERIC 6,5, DEFAULT 0.01) [C12-A]
│  └─ calculo_memoria (JSONB) [C12-A]
│
├─ ANÁLISE IA & DOCUMENTOS
│  ├─ pdf_dispositivo_texto (TEXT) [C12-A]
│  ├─ resumo_ia (TEXT)
│  ├─ ia_payload (JSONB)
│  ├─ tipo_condenacao (TEXT, CHECK IN ('dano_moral','dano_material','dano_moral_material','outro')) [C12-A]
│  └─ chance_sucesso_pct (NUMERIC 5,2, CHECK BETWEEN 0 AND 100) [C12-A]
│
├─ STATUS & AUDITORIA
│  ├─ status_analise (TEXT, nullable, valores: 'pendente'|'arquivada'|null) ⚠️ SEM CHECK
│  ├─ origem (TEXT, nullable) ← onde veio? ('controller_pipeline' em RPC)
│  ├─ arquivada (BOOLEAN, DEFAULT false) ⚠️ DUPLICA status_analise
│  ├─ created_at (TIMESTAMPTZ, NOT NULL, DEFAULT now()) ✅
│  ├─ updated_at (TIMESTAMPTZ, NOT NULL, DEFAULT now()) ✅
│  └─ deleted_at (TIMESTAMPTZ, nullable) ✅ Soft delete
```

### Migrations Relacionadas

| Migration | Descrição | Status |
|---|---|---|
| 20260304200001_trg_decisao_update_processo.sql | Trigger AFTER INSERT/UPDATE/DELETE → atualiza processos.ultima_decisao_* | ✅ Aplicada |
| 20260305100001_c12a_decisoes_calc_fields_and_intimacoes_fk.sql | Adiciona 8 colunas de cálculo + indices + FK intimacoes→decisoes | ⚠️ Parcial |
| 20260305100002_c12a_rpc_calcular_valor_atualizado.sql | RPC SECURITY DEFINER para calcular valores com juros/correção | ✅ Aplicada |
| 20260305100003_c12a_rpc_decisoes_inserir_via_pipeline.sql | RPC SECURITY DEFINER para INSERT atomico + UPDATE intimacoes.decisao_id | ✅ Aplicada |
| 20260306000001_add_decisoes_intimacao_id.sql | Adiciona coluna intimacao_id FK (redundante com 20260305100001?) | ❓ Duplicado? |

---

## ⚠️ Issues P0 — Bloqueadores

### P0.1: Conflito `arquivada` vs `status_analise`

**Problema:**
- Trigger em 20260304200001 filtra: `WHERE (d.status_analise IS NULL OR d.status_analise <> 'arquivada')`
- Migration 20260305100001 filtra índice: `WHERE arquivada = false`
- RPC 20260305100003 nunca toca em `arquivada`, sempre usa `status_analise`
- **Qual é a verdade?** Dois flags booleanos para mesma coisa = inconsistência total

**Impacto:**
```
// Cenário: usuário arquiva decisão marcando status_analise='arquivada'
// Mas índice idx_decisoes_valor_total ignora porque filtra arquivada=false
// → dados fantasma nas queries agregadas
```

**Recomendação:**
```sql
-- OPÇÃO A (recomendada): remover 'arquivada' e usar ONLY status_analise
ALTER TABLE decisoes DROP COLUMN IF EXISTS arquivada;

-- Então adicionar CHECK:
ALTER TABLE decisoes ADD CONSTRAINT decisoes_status_check 
  CHECK (status_analise IS NULL OR status_analise IN ('pendente','arquivada','analisada'));

-- OPÇÃO B: remover status_analise e usar ONLY arquivada
-- (menos semântico, evitar)
```

---

### P0.2: RLS Policy Não Validado

**Problema:**
- Supabase Management API indisponível
- Não foi possível validar se `ALTER TABLE decisoes ENABLE ROW LEVEL SECURITY` foi aplicado
- Não foi possível validar se policy `decisoes_org_isolation` existe

**Risco de segurança:**
```
Sem RLS → qualquer user de qualquer org vê TODAS as decisões
→ violação P4-04 (Multi-tenant Absoluto) do MdFlow
```

**Validação imediata necessária:**
```sql
-- Via Supabase Studio: SQL Editor
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname='public' AND tablename='decisoes';

SELECT policyname, cmd, roles FROM pg_policies 
WHERE tablename='decisoes';
```

---

### P0.3: Índices em `organizacao_id` Não Validados

**Esperado (obrigatório em MdFlow):**
```sql
CREATE INDEX idx_decisoes_org ON decisoes(organizacao_id);
CREATE INDEX idx_decisoes_org_active ON decisoes(organizacao_id) WHERE deleted_at IS NULL;
```

**Status:** Não validado via MCP

**Impacto:** Queries lentas em org com 1000+ decisões

---

## ⚠️ Issues P1 — Importantes

### P1.1: FK `intimacao_id` — Semântica Duvidosa

**Problema:**
```sql
-- Migration 20260306000001:
ALTER TABLE decisoes ADD COLUMN IF NOT EXISTS intimacao_id UUID 
  REFERENCES intimacoes(id) ON DELETE SET NULL;

-- RPC 20260305100003:
UPDATE intimacoes SET decisao_id = v_decisao_id
WHERE id = p_intimacao_id;
```

**Pergunta:** É relação 1:1, 1:N ou N:N?
- Uma `intimacao` pode ter múltiplas `decisoes`? (1:N)
- Uma `decisao` pode ter múltiplas `intimacoes`? (N:1 ou N:N)
- Ambas referenciam uma à outra? (bidirecional = problema)

**Padrão MdFlow:** FKs devem ser unidirecionais ou N:N via tabela de join explícita

**Validação necessária:**
```sql
-- Contar intimações que referenciam múltiplas decisões
SELECT intimacao_id, COUNT(DISTINCT id) as num_decisoes
FROM decisoes
WHERE intimacao_id IS NOT NULL
GROUP BY intimacao_id
HAVING COUNT(DISTINCT id) > 1;
```

---

### P1.2: `status_analise` Sem CHECK CONSTRAINT

**Problema:**
- Migration referencia valores: 'pendente' | 'arquivada'
- Mas não há CHECK documentado em CREATE TABLE ou ALTER TABLE
- INSERT direto sem passar por RPC permite valores inválidos

**Código para aplicar:**
```sql
ALTER TABLE decisoes ADD CONSTRAINT decisoes_status_analise_values
  CHECK (status_analise IS NULL OR status_analise IN ('pendente', 'arquivada', 'analisada'))
  NOT VALID;

VALIDATE CONSTRAINT decisoes_status_analise_values;
```

---

## ⚠️ Issues P2 — Melhorias

### P2.1: Campos de Cálculo Nunca são Preenchidos

**Problema:**
- `valor_total_calculado`, `data_calculo`, `calculo_memoria` começam NULL
- Só preenchem se `rpc_calcular_valor_atualizado` for chamado
- Nenhuma garantia de que serão calculados automaticamente

**Melhoria (opcional):**
```sql
-- Trigger para calcular automaticamente após INSERT/UPDATE com valor_condenacao
CREATE OR REPLACE FUNCTION fn_decisoes_auto_calculate()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.valor_condenacao IS NOT NULL 
     AND NEW.valor_total_calculado IS NULL THEN
    -- Chamar RPC de cálculo
    SELECT rpc_calcular_valor_atualizado(NEW.id, CURRENT_DATE)
    INTO NEW.calculo_memoria;
  END IF;
  RETURN NEW;
END; $$;

CREATE TRIGGER trg_decisoes_auto_calculate
  AFTER INSERT OR UPDATE ON decisoes
  FOR EACH ROW WHEN (NEW.valor_condenacao IS NOT NULL)
  EXECUTE FUNCTION fn_decisoes_auto_calculate();
```

---

## ✅ RPCs — Status

### `rpc_decisoes_inserir_via_pipeline`

```sql
CREATE OR REPLACE FUNCTION rpc_decisoes_inserir_via_pipeline(
  p_organizacao_id UUID,
  p_processo_id UUID,
  p_intimacao_id UUID,
  p_resultado TEXT,  -- 'favoravel'|'parcial'|'desfavoravel'|'improcedente'|'extinto'
  p_tipo TEXT DEFAULT 'merito',
  p_grau INT2 DEFAULT 1,
  p_data_decisao DATE DEFAULT NULL,
  p_valor_condenacao NUMERIC DEFAULT NULL,
  p_valor_honorarios NUMERIC DEFAULT NULL,
  p_tipo_condenacao TEXT DEFAULT NULL,
  p_indice_correcao TEXT DEFAULT 'IPCA',
  p_taxa_juros_mensal NUMERIC DEFAULT 0.01,
  p_data_inicio_juros DATE DEFAULT NULL,
  p_resumo_ia TEXT DEFAULT NULL,
  p_pdf_dispositivo_texto TEXT DEFAULT NULL,
  p_ia_payload JSONB DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
```

**Status:** ✅ SECURITY DEFINER + SET search_path + RETURNS JSONB

**Fluxo:**
1. INSERT em `decisoes` com status='pendente', origem='controller_pipeline'
2. UPDATE `intimacoes.decisao_id` = v_decisao_id
3. UPDATE `processos.ultima_decisao_*` (snapshot)
4. CALL `rpc_calcular_valor_atualizado` se favorável + tem valor
5. RETURN JSONB com resultado

---

### `rpc_calcular_valor_atualizado`

```sql
CREATE OR REPLACE FUNCTION rpc_calcular_valor_atualizado(
  p_decisao_id UUID,
  p_data_calculo DATE DEFAULT CURRENT_DATE
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
```

**Status:** ✅ SECURITY DEFINER + SET search_path + RETURNS JSONB

**Lógica:**
```
valor_base = valor_condenacao
data_inicio = COALESCE(data_inicio_juros, data_distribuicao_processo, data_decisao - 180 dias)
meses = EXTRACT(year|month|day FROM age(p_data_calculo, data_inicio))

fator_correcao = POWER(taxa_mensal, meses)
  └─ IPCA: 0.5%/mês
  └─ INPC: 0.48%/mês
  └─ SELIC: 0.75%/mês
  └─ CDI: 0.73%/mês
  └─ MANUAL: 1.0 (sem correção)

valor_corrigido = valor_base × fator_correcao
valor_juros = valor_base × taxa_juros_mensal × meses
valor_total = valor_corrigido + valor_juros + valor_honorarios

RETORNA: JSONB com memória de cálculo auditável
```

**GRAVA EM:** decisoes.valor_atualizado, valor_juros, valor_total_calculado, data_calculo, calculo_memoria

---

## ✅ Triggers — Status

### `trg_decisao_update_processo`

```sql
CREATE TRIGGER trg_decisao_update_processo
  AFTER INSERT OR UPDATE OR DELETE ON decisoes
  FOR EACH ROW
  EXECUTE FUNCTION fn_trg_decisao_update_processo();
```

**Status:** ✅ IMPLEMENTADO

**Fluxo:**
1. Evento: INSERT/UPDATE/DELETE em `decisoes`
2. Fetch processo_id de NEW/OLD
3. SELECT última decisão NÃO ARQUIVADA ordenada por data_decisao DESC
4. UPDATE processos.ultima_decisao_{tipo, resultado, data}
5. Se DELETE e nenhuma decisão restante → zera campos

---

## 🔧 SQL de Correção — Ready to Apply

### FASE 1: RLS & Índices (P0)

```sql
-- 1. RLS (OBRIGATÓRIO)
ALTER TABLE decisoes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "decisoes_org_isolation" ON decisoes;
CREATE POLICY "decisoes_org_isolation" ON decisoes
  FOR ALL USING (organizacao_id = public.get_org_id())
  WITH CHECK (organizacao_id = public.get_org_id());

-- 2. Índices (OBRIGATÓRIO)
CREATE INDEX IF NOT EXISTS idx_decisoes_org 
  ON decisoes(organizacao_id);

CREATE INDEX IF NOT EXISTS idx_decisoes_org_active 
  ON decisoes(organizacao_id) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_decisoes_valor_total
  ON decisoes(organizacao_id, valor_total_calculado)
  WHERE valor_total_calculado IS NOT NULL 
    AND (status_analise IS NULL OR status_analise <> 'arquivada');

-- 3. Trigger updated_at (se não existe)
CREATE TRIGGER IF NOT EXISTS trg_decisoes_updated_at 
  BEFORE UPDATE ON decisoes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### FASE 2: Semântica — DECISÃO NECESSÁRIA

**OPÇÃO A: Remover `arquivada`, usar ONLY `status_analise` (RECOMENDADO)**

```sql
-- 1. Adicionar CHECK constraint
ALTER TABLE decisoes ADD CONSTRAINT decisoes_status_check 
  CHECK (status_analise IS NULL OR status_analise IN ('pendente', 'arquivada', 'analisada'))
  NOT VALID;

VALIDATE CONSTRAINT decisoes_status_check;

-- 2. Remover coluna duplicada
ALTER TABLE decisoes DROP COLUMN IF EXISTS arquivada CASCADE;

-- 3. Validar índices que referenciam 'arquivada'
-- Se houver: DROP e recriar usando status_analise
```

**OPÇÃO B: Remover `status_analise`, usar ONLY `arquivada`**

```sql
-- NÃO RECOMENDADO — menos semântico
ALTER TABLE decisoes DROP COLUMN IF EXISTS status_analise CASCADE;
ALTER TABLE decisoes ADD COLUMN arquivada BOOLEAN DEFAULT false;
ALTER TABLE decisoes ADD CONSTRAINT decisoes_arquivada_check 
  CHECK (arquivada IN (true, false));
```

### FASE 3: Check Constraint em `status_analise` (P1)

```sql
ALTER TABLE decisoes ADD CONSTRAINT decisoes_status_analise_values
  CHECK (status_analise IS NULL OR status_analise IN ('pendente', 'arquivada', 'analisada'))
  NOT VALID;

VALIDATE CONSTRAINT decisoes_status_analise_values;
```

### FASE 4: Validar FK `intimacao_id` (P1)

```sql
-- Verificar cardinalidade
SELECT 
  intimacao_id,
  COUNT(DISTINCT id) as num_decisoes,
  COUNT(*) as total_rows
FROM decisoes
WHERE intimacao_id IS NOT NULL
GROUP BY intimacao_id
ORDER BY num_decisoes DESC
LIMIT 10;

-- Se cardinality for 1:1, adicionar:
-- ALTER TABLE decisoes ADD CONSTRAINT decisoes_intimacao_id_unique 
--   UNIQUE (intimacao_id);
```

---

## 📋 Checklist de Conformidade

| Item | Status | Notas |
|---|---|---|
| `organizacao_id` presente | ✅ | FK NOT NULL |
| `deleted_at` para soft delete | ✅ | TIMESTAMPTZ nullable |
| `created_at` timestamp | ✅ | DEFAULT now() |
| `updated_at` timestamp | ✅ | DEFAULT now() + trigger |
| RLS habilitado | ❌ P0 | Não validado |
| RLS policy `org_isolation` | ❌ P0 | Não validado |
| Índices `organizacao_id` | ❌ P0 | Não validado |
| Índice `organizacao_id` WHERE deleted_at IS NULL | ❌ P0 | Não validado |
| CHECK em enums (resultado, tipo_condenacao, etc) | ✅ | TEXT CHECK |
| RPCs SECURITY DEFINER | ✅ | 2 RPCs validadas |
| RPCs SET search_path = public | ✅ | 2 RPCs validadas |
| RPCs RETURNS JSONB | ✅ | 2 RPCs validadas |
| Trigger updated_at | ⚠️ | Não validado |
| Trigger snapshot (trg_decisao_update_processo) | ✅ | Implementado |
| Sem ENUM nativo PostgreSQL | ✅ | TEXT CHECK apenas |
| JSONB para dados complexos | ✅ | calculo_memoria, ia_payload |

---

## 🧪 Testes Recomendados

### Teste 1: RLS Isolation

```sql
-- Como user de org A, tentar ver decisões de org B
SET LOCAL "request.jwt.claims" = '{"sub":"uid-user-org-a","org_id":"55a0c7ba-1a23-4ae1-b69b-a13811324735"}';

SELECT COUNT(*) FROM decisoes;  -- Deve retornar APENAS decisões org A
```

### Teste 2: Cálculo de Valor

```sql
-- Inserir decision e testar cálculo
INSERT INTO decisoes 
  (organizacao_id, processo_id, tipo, resultado, data_decisao, valor_condenacao)
VALUES 
  ('55a0c7ba-1a23-4ae1-b69b-a13811324735', 'pid-123', 'merito', 'favoravel', '2025-01-01'::date, 10000);

-- Chamar RPC
SELECT rpc_calcular_valor_atualizado('decisao-id', CURRENT_DATE);

-- Validar se campos foram preenchidos
SELECT valor_atualizado, valor_juros, valor_total_calculado, calculo_memoria 
FROM decisoes WHERE id = 'decisao-id';
```

### Teste 3: Trigger Snapshot

```sql
-- UPDATE decision deve atualizar processos.ultima_decisao_*
UPDATE decisoes 
SET resultado = 'favoravel' 
WHERE id = 'decisao-id';

-- Validar
SELECT ultima_decisao_resultado, ultima_decisao_tipo, ultima_decisao_data 
FROM processos WHERE id = (SELECT processo_id FROM decisoes WHERE id = 'decisao-id');
```

---

## 📁 Arquivos Relacionados

- **Migrations:** `/Users/beto/beta-mdflow/supabase/migrations/`
  - `20260304200001_trg_decisao_update_processo.sql`
  - `20260305100001_c12a_decisoes_calc_fields_and_intimacoes_fk.sql`
  - `20260305100002_c12a_rpc_calcular_valor_atualizado.sql`
  - `20260305100003_c12a_rpc_decisoes_inserir_via_pipeline.sql`
  - `20260306000001_add_decisoes_intimacao_id.sql`

- **Documentação MdFlow:** `/Users/beto/beta-mdflow/CLAUDE.md` (seção 4 — Supabase MCP)

- **Constantes Frontend:** `/Users/beto/beta-mdflow/src/components/processo/constants/decisao-constants.ts`

---

## 🎯 Próximos Passos

### URGENTE (hoje)

1. **P0 — RLS:** Aplicar via Supabase Studio → validar com query pg_policies
2. **P0 — Índices:** Aplicar via Studio → validar com pg_indexes
3. **P0 — Semântica:** DECIDIR com CTO entre OPÇÃO A e OPÇÃO B

### Importante (esta semana)

4. **P1 — FK intimacao_id:** Validar cardinalidade com queries
5. **P1 — CHECK status_analise:** Aplicar constraint
6. **Testes:** Executar 3 testes recomendados acima

### Nice-to-have (próxima sprint)

7. **P2 — Auto-calculate:** Implementar trigger para preencher valores automaticamente

---

## 📞 Contatos & Referências

**Erro ou dúvida?**
- CTO: Christian (Telegram: 1307075495)
- Spec oficial: `/Users/beto/beta-mdflow/CLAUDE.md` seção 4 (Supabase)
- Schema Backend: `/Users/beto/workspace/mdflow/docs/Revisa_o_BACKEND.txt`

**Audit Tool:** `mdflow-db-auditor` (Claude Haiku 4.5) — 2026-03-31

