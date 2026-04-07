# /configuracoes Audit — Quick Reference

## 3 Critical Issues to Fix TODAY

| Issue | Tables | Fix | Time |
|-------|--------|-----|------|
| P0.1: No `deleted_at` | ALL 21 | `ALTER TABLE ADD COLUMN` | 2h |
| P0.2: No triggers | 12 config tables | `CREATE TRIGGER` | 1h |
| P0.3: Verify RLS | `users` table | Check policy exists | 30min |

## Status Overview

```
Compliance:  ████████░░ 70%
P0 Issues:   ███ 3 CRITICAL
P1 Issues:   ████████ 8 IMPORTANT
P2 Issues:   ████ 4 MINOR
Total Tables: 26 audited
Risk Level: HIGH
```

## One-Liner Fixes

```sql
-- P0.1: Add deleted_at to core tables
ALTER TABLE public.users ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE public.advogados ADD COLUMN deleted_at TIMESTAMPTZ;
-- ... (21 total)

-- P0.2: Add update_updated_at trigger
CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.atividades_tipos
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- ... (12 total)

-- P0.3: Verify RLS policy
SELECT policyname FROM pg_policies WHERE tablename='users' AND policyname ILIKE '%org%';

-- P1.5: Add perfil CHECK
ALTER TABLE public.users 
  ADD CONSTRAINT check_users_perfil 
  CHECK (perfil IN ('juridico','comercial','financeiro','operacional'));

-- P1.6: Add FK indexes
CREATE INDEX idx_adv_dist_uf_advogado ON advogados_distribuicao_uf(advogado_id);
CREATE INDEX idx_adv_dist_itens_advogado ON advogados_distribuicao_itens(advogado_id);
```

## Impact If Not Fixed

| P0.1 | Hard delete fails on users → FK constraint violation |
|------|--------|
| P0.2 | No audit trail — can't track config changes |
| P0.3 | Multi-tenant data leak — cross-org access |

## Tables by Category

### Core (5)
- users ❌ deleted_at, ❌ CHECK(perfil)
- advogados ❌ deleted_at
- advogados_correspondentes ❌ created_at, ❌ updated_at, ❌ deleted_at
- organizacao_setores ❌ trigger
- organizacoes ✅ OK

### Configuration (12)
- atividades_tipos ❌ trigger
- config_etiquetas_catalogo ❌ trigger
- config_templates ❌ trigger
- contas_bancarias ❌ trigger
- cartoes_credito ❌ trigger
- controller_dominios ❌ trigger
- crm_estagios_funil ❌ trigger
- crm_followup_config ❌ trigger
- crm_origens ❌ trigger
- docs_categorias ❌ trigger
- docs_tipos ❌ trigger
- mdzap_ai_modules ❌ trigger

### Relationships (4)
- advogados_distribuicao_uf ❌ timestamps, ❌ index
- advogados_distribuicao_itens ❌ timestamps, ❌ index
- users_paginas_permissoes ❌ trigger, ❌ indexes
- whatsapp_numeros ❌ trigger

### System (2)
- config_paginas_sistema ⚠️ scope ambiguous
- processos_situacoes ⚠️ scope ambiguous

## Verification Queries

```sql
-- Check what needs deleted_at
SELECT tablename FROM pg_tables 
WHERE schemaname='public' AND tablename IN (
  'users','advogados','organizacao_setores',...
) AND tablename NOT IN (
  SELECT DISTINCT table_name FROM information_schema.columns 
  WHERE table_schema='public' AND column_name='deleted_at'
);

-- Check missing triggers
SELECT event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema='public' AND trigger_name ILIKE '%updated%'
EXCEPT
SELECT tablename FROM pg_tables 
WHERE schemaname='public' AND tablename IN (
  'atividades_tipos','config_etiquetas_catalogo',...
);

-- Check RLS on users
SELECT policyname FROM pg_policies WHERE tablename='users';
-- Must include: users_org_isolation or similar
```

## Full Reports

1. **QUICK REFERENCE** (this file) — 2 min read
2. **AUDIT_SUMMARY.txt** — 10 min read (executive overview)
3. **audit_configuracoes_20260331.md** — 20 min read (detailed findings)
4. **audit_configuracoes_DETAILED.md** — 30 min read (code evidence + fix strategy)

## Timeline

**Same day (4h):**
- P0.1: Add deleted_at columns
- P0.2: Add missing triggers
- P0.3: Verify RLS policies

**This week (5h):**
- P1.1-P1.8: Audit columns, constraints, indexes

**Next 2 weeks (12h):**
- P2.1-P2.4: RPCs, audit logging, documentation

## Who Needs This

- **Christian (CTO)**: Review migration strategy
- **Database team**: Execute SQL fixes
- **Frontend team**: No code changes needed (schema-only fix)
- **QA team**: Test soft delete workflows

## Contact

Questions? See AUDIT_SUMMARY.txt → CONTACT & ESCALATION section

---

**Status:** Ready for implementation | **Risk:** HIGH (P0 blockers) | **Date:** 2026-03-31

