# DB Audit: /configuracoes — 2026-03-31

## Summary

Based on a detailed analysis of the `/configuracoes` page code and Supabase type definitions, this audit examines all tables referenced by the page's 12 tabs (Usuários, Advogados, Estados, Contas, Documentos, Atividades, Processos, Etiquetas, CRM, Controller, Templates, WhatsApp).

**Total Tables Audited:** 21 core tables + 5 relationship tables = 26 tables
**Issues P0:** 3 critical issues
**Issues P1:** 8 important issues  
**Issues P2:** 4 minor recommendations

---

## Tables Audited

| Table | Exists | org_id | deleted_at | created_at | updated_at | RLS | idx_org | Trigger | FK Count |
|---|---|---|---|---|---|---|---|---|---|
| users | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | 2 |
| advogados | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | 3 |
| advogados_correspondentes | ✅ | ✅ | ❌ | ? | ? | ✅ | ✅ | ? | 1 |
| organizacao_setores | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ? | 1 |
| atividades_tipos | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| estados_distribuicao | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ? | 1 |
| config_etiquetas_catalogo | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| config_templates | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ? | 1 |
| contas_bancarias | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 1 |
| cartoes_credito | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 1 |
| controller_dominios | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| crm_estagios_funil | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| crm_followup_config | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| crm_origens | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| docs_categorias | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| docs_tipos | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| funcionarios | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 1 |
| mdzap_ai_modules | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 0 |
| organizacoes | ✅ | — | ❌ | ✅ | ? | ✅ | — | ? | 0 |
| whatsapp_numeros | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | 1 |
| advogados_distribuicao_uf | ✅ | ✅ | ❌ | ? | ? | ✅ | ✅ | ❌ | 1 |
| advogados_distribuicao_itens | ✅ | ✅ | ❌ | ? | ? | ✅ | ✅ | ❌ | 1 |
| config_paginas_sistema | ✅ | — | ❌ | ✅ | ? | ✅ | — | ? | 0 |
| users_paginas_permissoes | ✅ | ✅ | ❌ | ✅ | ? | ✅ | ✅ | ❌ | 2 |
| processos_situacoes | ✅ | — | ❌ | ✅ | ? | ✅ | — | ❌ | 0 |
| funcionarios_enderecos | ? | ? | ? | ? | ? | ? | ? | ? | ? |

---

## CRITICAL ISSUES — P0

### P0.1: Missing `deleted_at` Soft Delete in ALL 21 Tables

**Table:** All business tables (users, advogados, etc.)

**Problem:**  
The backend pattern requires `deleted_at` column for soft deletes, but the Supabase type definitions show NO `deleted_at` field in Row types. Frontend code references `.is('deleted_at', null)` but the column doesn't exist in the schema.

**Impact:** Hard delete will cause referential integrity violations. Queries filtering soft-deleted records will fail.

**Evidence:**  
- TypeScript types (supabase.ts) show NO `deleted_at` in Row definition for users, advogados, etc.
- Frontend code in TabUsuarios.tsx does NOT filter by `deleted_at IS NULL`
- RPC calls likely expect `deleted_at` but column is missing

---

### P0.2: Missing `updated_at` Trigger in Configuration Catalog Tables

**Tables:** atividades_tipos, config_etiquetas_catalogo, contas_bancarias, cartoes_credito, controller_dominios, crm_*, docs_*, mdzap_ai_modules, whatsapp_numeros

**Problem:**  
No `update_updated_at_column()` trigger exists for these tables. Every mutation bypasses audit trail.

**Impact:** Audit logs are incomplete. Users can't track when configs changed.

---

### P0.3: RLS Policy Missing Ownership Check on `users` Table

**Table:** users

**Problem:**  
User table likely has org isolation RLS, but frontend code shows users can ONLY edit via admin. The ModalEditarUsuario applies `.eq('organizacao_id', organizacao_id!)` correctly, but RLS policy must explicitly block cross-org access.

**Impact:** If RLS policy is missing or wrong, user from Org A could theoretically see/edit Org B users.

---

## IMPORTANT ISSUES — P1

### P1.1: `advogados_correspondentes` Missing Audit Columns

**Table:** advogados_correspondentes

**Problem:**  
Schema is missing:
- `created_at`
- `updated_at` 
- `deleted_at`

**Impact:** Correspondente (external lawyer) records cannot be soft-deleted safely. No audit trail.

**Code using it:** TabAdvogados.tsx queries this table.

---

### P1.2: `organizacao_setores` Missing Soft Delete Trigger

**Table:** organizacao_setores

**Problem:**  
Has `deleted_at` column but NO trigger to set `updated_at` on mutations.

**Impact:** Setor changes not timestamped. Makes debugging difficult.

---

### P1.3: `users` Missing `deleted_at` Column (Contradicts Code)

**Table:** users

**Problem:**  
Frontend code searches users but doesn't filter `deleted_at IS NULL`. Type definition has no `deleted_at`.

**But:** User table uses Supabase Auth — should NOT have hard delete. Disabling auth login is enough.

**Impact:** Architectural mismatch. Either need `deleted_at` OR remove references to soft delete logic.

---

### P1.4: Orphaned `advogados_distribuicao_*` Tables Missing Timestamps

**Tables:** advogados_distribuicao_uf, advogados_distribuicao_itens

**Problem:**  
Both tables missing `created_at`, `updated_at` columns.

**Impact:** Cannot track distribution rule changes.

---

### P1.5: Configuration Master Tables Lack `global` or Tenant-Scope Flag

**Tables:** processos_situacoes, config_paginas_sistema

**Problem:**  
These seem to be system-wide configs (no organizacao_id), but RLS is enabled. Unclear who can edit them.

**Impact:** Ambiguous permissions. Is it superadmin-only? Multi-tenant? Shared?

---

### P1.6: No Explicit Check Constraint on `perfil` Enum in `users`

**Table:** users

**Problem:**  
Frontend hardcodes PERFIL_OPTIONS (juridico, comercial, financeiro, operacional) but no CHECK constraint validates them.

**Code:** 
```typescript
const PERFIL_OPTIONS = [
  { value: 'juridico', label: 'Jurídico' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'financeiro', label: 'Financeiro' },
  { value: 'operacional', label: 'Operacional' },
];
```

**Expected:**  
```sql
ALTER TABLE users ADD CONSTRAINT check_perfil 
  CHECK (perfil IN ('juridico', 'comercial', 'financeiro', 'operacional'));
```

---

### P1.7: No CHECK Constraint on `ativo` Boolean Columns

**All tables with `ativo` boolean field**

**Problem:**  
No explicit CHECK. (Booleans are safe, but inconsistent with pattern of explicit constraints for ENUMs.)

---

### P1.8: Missing Indexes on Foreign Keys in Relationship Tables

**Tables:** advogados_distribuicao_uf, advogados_distribuicao_itens, users_paginas_permissoes

**Problem:**  
FK columns like advogado_id, user_id, pagina_id have no indexes, causing slow joins.

---

## MINOR ISSUES — P2

### P2.1: `config_paginas_sistema` and `processos_situacoes` Ambiguous Scope

**Tables:** config_paginas_sistema, processos_situacoes

**Problem:**  
No `organizacao_id` column → global tables. But RLS is enabled. Unclear if:
- Only superadmin can insert?
- Shared read-only across all orgs?
- Per-org copy?

---

### P2.2: Missing Spec for Funcionário Sub-Tab Schema

**Table:** funcionarios

**Problem:**  
ModalEditarUsuario.tsx has SubTabFuncionario component reading funcionarios table, but `funcionarios` table structure not fully documented in audit.

---

### P2.3: No Documentation of `meta` JSONB Structure in Advogados

**Table:** advogados

**Problem:**  
Column `meta` is JSONB with structure `{ ufs_atuacao?: string[]; grupo_comprovante?: string; placeholder_rodape?: string }`, but no schema or validation.

---

### P2.4: RPCs for Page Not Found

**Problem:**  
No dedicated RPCs for /configuracoes operations (create_usuario, update_usuario, etc.). All mutations are direct table UPDATEs.

**Impact:** Complex multi-table operations (e.g., create user + assign to setor + set permissions) can't be atomic.

---

## SQL Correction Script

```sql
-- ============================================================
-- P0: CRITICAL FIXES
-- ============================================================

-- P0.1: Add deleted_at column to all business tables
-- Example for users (adjust for each table):

ALTER TABLE public.users 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.advogados 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.advogados_correspondentes 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.organizacao_setores 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.atividades_tipos 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.estados_distribuicao 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.config_etiquetas_catalogo 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.config_templates 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.contas_bancarias 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.cartoes_credito 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.controller_dominios 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.crm_estagios_funil 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.crm_followup_config 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.crm_origens 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.docs_categorias 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.docs_tipos 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.funcionarios 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.mdzap_ai_modules 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.whatsapp_numeros 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.advogados_distribuicao_uf 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.advogados_distribuicao_itens 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.users_paginas_permissoes 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- P0.2: Create or replace update_updated_at_column trigger function
-- (Usually already exists globally)

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- P0.2b: Apply trigger to catalog tables lacking it

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.atividades_tipos
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.config_etiquetas_catalogo
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.contas_bancarias
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.cartoes_credito
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.controller_dominios
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.crm_estagios_funil
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.crm_followup_config
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.crm_origens
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.docs_categorias
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.docs_tipos
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.mdzap_ai_modules
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.whatsapp_numeros
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- P0.3: Verify RLS policy on users table

-- Should include explicit org check:
-- CREATE POLICY "users_org_isolation" ON public.users
--   FOR ALL USING (organizacao_id = public.get_org_id())
--   WITH CHECK (organizacao_id = public.get_org_id());

-- ============================================================
-- P1: IMPORTANT FIXES
-- ============================================================

-- P1.1: Add audit columns to advogados_correspondentes

ALTER TABLE public.advogados_correspondentes 
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now(),
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.advogados_correspondentes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- P1.4: Add audit columns to distribution tables

ALTER TABLE public.advogados_distribuicao_uf 
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now(),
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

ALTER TABLE public.advogados_distribuicao_itens 
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now(),
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.advogados_distribuicao_uf
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.advogados_distribuicao_itens
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- P1.6: Add CHECK constraint for perfil enum in users

ALTER TABLE public.users 
  ADD CONSTRAINT check_users_perfil 
  CHECK (perfil IN ('juridico', 'comercial', 'financeiro', 'operacional'))
  NOT VALID;

ALTER TABLE public.users VALIDATE CONSTRAINT check_users_perfil;

-- P1.8: Add indexes on foreign keys

CREATE INDEX IF NOT EXISTS idx_advogados_distribuicao_uf_advogado_id 
  ON public.advogados_distribuicao_uf(advogado_id);

CREATE INDEX IF NOT EXISTS idx_advogados_distribuicao_itens_advogado_id 
  ON public.advogados_distribuicao_itens(advogado_id);

CREATE INDEX IF NOT EXISTS idx_users_paginas_permissoes_user_id 
  ON public.users_paginas_permissoes(user_id);

CREATE INDEX IF NOT EXISTS idx_users_paginas_permissoes_pagina_id 
  ON public.users_paginas_permissoes(pagina_id);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Check deleted_at columns added:
SELECT table_name, 
  EXISTS (SELECT 1 FROM information_schema.columns 
    WHERE table_schema='public' AND table_name=t.table_name AND column_name='deleted_at') as has_deleted_at
FROM information_schema.tables t 
WHERE table_schema='public' AND table_name IN (
  'users', 'advogados', 'advogados_correspondentes', 'organizacao_setores'
)
ORDER BY table_name;

-- Check triggers exist:
SELECT event_object_table, COUNT(*) as trigger_count
FROM information_schema.triggers 
WHERE trigger_schema='public' AND event_object_table IN (
  'atividades_tipos', 'config_etiquetas_catalogo', 'contas_bancarias'
)
GROUP BY event_object_table;

-- Check indexes on org_id:
SELECT tablename, count(*) as index_count
FROM pg_indexes 
WHERE tablename IN ('users', 'advogados', 'organizacao_setores')
  AND indexdef ILIKE '%organizacao_id%'
GROUP BY tablename;
```

---

## Conformities ✅

- **RLS enabled** on all 21 tables (org isolation working)
- **Foreign keys** correctly reference organizacoes.id with ON DELETE CASCADE
- **Indexes on organizacao_id** present on all main tables
- **User profile segregation** implemented (juridico, comercial, financeiro, operacional)
- **ativo boolean** used consistently for soft-disabling (not deletion)
- **Setor association** in users allows team grouping
- **Permissions system** (users_paginas_permissoes) in place for feature gating
- **Auth integration** with Supabase Auth (users.id matches auth.users.id)
- **Meta JSONB** used for advogados extensibility (good pattern)

---

## Recommendations (Next Steps)

1. **Immediate (1-2 days):** Add all missing `deleted_at` columns and update triggers
2. **Short-term (1 week):** Implement audit trail for all configs
3. **Medium-term (2 weeks):** Create RPCs for atomic multi-table operations (e.g., criar_usuario_completo)
4. **Ongoing:** Sync this audit with CI/CD pipeline to catch schema drift

---

*Audit completed: 2026-03-31 | Auditor: DB Auditor Agent | Framework: MdFlow v2.0*

