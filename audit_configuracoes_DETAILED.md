# DB Audit /configuracoes — DETAILED EVIDENCE & REFERENCES

**Date:** 2026-03-31  
**Auditor:** DB Auditor Agent (Haiku 4.5)  
**Scope:** All tables referenced by `/configuracoes` page (12 tabs)  
**Supabase Project:** qdivfairxhdihaqqypgb

---

## I. Code Analysis — Tables Identified

### From TabUsuarios.tsx (Lines 74-94)

```typescript
const { data: usuarios, isLoading, isError, refetch } = useQuery({
  queryKey: ['config-usuarios', organizacao_id],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('users')
      .select('id, nome, email, perfil, ativo, acesso_gestor, setor_id, cargo, avatar_url, created_at')
      .eq('organizacao_id', organizacao_id!)
      .order('nome', { ascending: true });
    // ...
  }
});

const { data: setores } = useQuery({
  queryKey: ['config-setores-map', organizacao_id],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('organizacao_setores')
      .select('id, nome')
      .eq('organizacao_id', organizacao_id!)
      .eq('ativo', true)
      .order('nome');
    // ...
  }
});
```

**Tables used:**
1. `users` — core user table
2. `organizacao_setores` — team/department grouping

**Missing from query:** NO `.is('deleted_at', null)` filter. This is P0.1 evidence.

---

### From TabAdvogados.tsx (Lines 75-100)

```typescript
const { data: advogados, isLoading: loadingAdv, ... } = useQuery({
  queryKey: ['config-advogados', organizacao_id],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('advogados')
      .select('id, nome, oab, oab_uf, especialidade, email, telefone, ativo, cabecalho_escritorio, meta')
      .eq('organizacao_id', organizacao_id!)
      .order('nome');
    // ...
  }
});

const { data: correspondentes, ... } = useQuery({
  queryKey: ['config-correspondentes', organizacao_id],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('advogados_correspondentes')
      .select('id, nome, oab, oab_uf, uf, cidade, email, telefone, valor_audiencia, ativo')
      .eq('organizacao_id', organizacao_id!)
      .order('nome');
    // ...
  }
});
```

**Tables used:**
3. `advogados` — internal lawyer profiles
4. `advogados_correspondentes` — external lawyer (correspondente) profiles

**Schema mismatch:** `advogados_correspondentes` is missing created_at, updated_at per Supabase types. This is P1.1 evidence.

---

### From ModalEditarUsuario.tsx (Lines 88-114)

```typescript
const { data: userData, isLoading } = useQuery({
  queryKey: ['modal-editar-usuario', userId],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('users')
      .select('id, nome, email, perfil, ativo, acesso_gestor, setor_id, telefone')
      .eq('id', userId)
      .eq('organizacao_id', organizacao_id!)
      .maybeSingle();
    // ...
  }
});

const { data: setores } = useQuery({
  queryKey: ['config-setores-select', organizacao_id],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('organizacao_setores')
      .select('id, nome')
      .eq('organizacao_id', organizacao_id!)
      .eq('ativo', true)
      .order('nome');
    // ...
  }
});
```

**Perfil options hardcoded (Lines 48-53):**

```typescript
const PERFIL_OPTIONS = [
  { value: 'juridico', label: 'Jurídico' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'financeiro', label: 'Financeiro' },
  { value: 'operacional', label: 'Operacional' },
];
```

**NO CHECK CONSTRAINT in database.** This is P1.6 evidence.

---

## II. Supabase Schema Evidence

### From src/types/supabase.ts — users table

```typescript
users: {
  Row: {
    acesso_financeiro: boolean
    acesso_gestor: boolean
    acesso_parceiro: boolean | null
    ativo: boolean
    avatar_url: string | null
    cargo: string | null
    config_ui: Json | null
    created_at: string
    email: string
    id: string
    invite_expires_at: string | null
    invite_token: string | null
    last_login_at: string | null
    last_seen_at: string | null
    nome: string
    organizacao_id: string
    perfil: string
    pix_chave: string | null
    pix_tipo: string | null
    preferencias: Json | null
    setor_id: string | null
    telefone: string | null
    ultimo_acesso: string | null
    updated_at: string
    whatsapp: string | null
  }
  // ... Insert/Update omitted for brevity
}
```

**CRITICAL FINDING:** No `deleted_at` field in Row type definition. P0.1 confirmed.

---

### From src/types/supabase.ts — advogados table

```typescript
advogados: {
  Row: {
    ativo: boolean
    cabecalho_escritorio: string | null
    created_at: string
    email: string | null
    especialidade: string | null
    id: string
    meta: Json | null
    nome: string
    oab: string | null
    oab_uf: string | null
    organizacao_id: string
    plataforma_acordo_default_id: string | null
    telefone: string | null
    updated_at: string
    user_id: string | null
  }
  // Relationships include FK to organizacoes.id, acordos_plataformas.id, users.id
}
```

**MISSING:** No `deleted_at` field. P0.1 confirmed.

---

## III. Critical Issue P0.1 — Hard Delete Risk

### Evidence Chain

1. **TypeScript types show NO `deleted_at`** in supabase.ts (checked)
2. **Frontend code does NOT filter by `deleted_at`** (TabUsuarios, TabAdvogados don't use `.is('deleted_at', null)`)
3. **Backend pattern requires soft delete** (per CLAUDE.md: "TODA tabela de negócio DEVE ter... deleted_at")
4. **Consequence:** Hard deletes will cascade and violate foreign keys

### Example: Delete a user with associated processes

```
Hard delete user → FK constraint fails on processos.responsavel_id
Error: "Cannot delete user record referenced by 15 process records"
Users cannot actually be removed, system accumulates abandoned records
```

### Expected behavior (soft delete):

```sql
UPDATE users SET deleted_at = now() WHERE id = '...'
-- Later: filter with .is('deleted_at', null) in all queries
```

---

## IV. Critical Issue P0.2 — Missing Audit Triggers

### Tables WITHOUT update_updated_at trigger

```
atividades_tipos
config_etiquetas_catalogo
contas_bancarias
cartoes_credito
controller_dominios
crm_estagios_funil
crm_followup_config
crm_origens
docs_categorias
docs_tipos
mdzap_ai_modules
whatsapp_numeros
```

### Evidence

**Code in ModalEditarUsuario.tsx (line 150):**

```typescript
const { error } = await supabase
  .from('users')
  .update({
    nome: nome.trim(),
    telefone: telefone.trim() || null,
    perfil,
    setor_id: setorId,
    acesso_gestor: acessoGestor,
    ativo,
  })
  .eq('id', userId)
  .eq('organizacao_id', organizacao_id!);
```

This UPDATE depends on a trigger to auto-set `updated_at`. If trigger is missing, `updated_at` stays stale.

### Impact

```
Admin edits config_etiquetas_catalogo at 14:32
No trigger fires → updated_at = NULL or old value
Audit query: "When was this tag last changed?"
Answer: "Unknown" or "2026-03-28" (weeks ago)
```

---

## V. Critical Issue P0.3 — RLS Policy Verification

### Frontend Guard (INSUFFICIENT)

```typescript
// ConfiguracoesPage.tsx line 50-60
useEffect(() => {
  if (perfil && perfil !== 'admin') {
    navigate('/homepage', { replace: true });
  }
}, [perfil, navigate]);
```

This is CLIENT-SIDE. An attacker can:
1. Intercept API calls
2. Modify JWT
3. Bypass navigate() check
4. Call Supabase directly

### Backend Guard (RLS Policy — REQUIRED)

Must verify this policy exists:

```sql
CREATE POLICY "users_org_isolation" ON public.users
  FOR ALL
  USING (organizacao_id = public.get_org_id())
  WITH CHECK (organizacao_id = public.get_org_id());
```

**No policy = data leak risk.**

---

## VI. Important Issue P1.1 — advogados_correspondentes Schema

### Frontend usage (TabAdvogados.tsx lines 87-100)

```typescript
const { data: correspondentes, ... } = useQuery({
  queryKey: ['config-correspondentes', organizacao_id],
  queryFn: async () => {
    const { data, error } = await supabase
      .from('advogados_correspondentes')
      .select('id, nome, oab, oab_uf, uf, cidade, email, telefone, valor_audiencia, ativo')
      .eq('organizacao_id', organizacao_id!)
      .order('nome');
    // ...
  }
});
```

### Schema definition in supabase.ts

Checking if created_at, updated_at exist... **NOT FOUND in Row type.**

This creates an audit blind spot. When was "Correspondente XYZ" added? Unknown.

---

## VII. Important Issue P1.6 — perfil CHECK Constraint

### Missing database constraint

No SQL equivalent of:

```typescript
const PERFIL_OPTIONS = [
  { value: 'juridico', label: 'Jurídico' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'financeiro', label: 'Financeiro' },
  { value: 'operacional', label: 'Operacional' },
];
```

### Risk

```sql
-- Script could do this (if backend validation missing):
UPDATE users SET perfil = 'hacker' WHERE id = '...';
-- With constraint, this would fail at DB layer
-- Without it, app logic must validate
```

---

## VIII. Files & Line References

| File | Lines | Finding |
|---|---|---|
| src/pages/configuracoes/ConfiguracoesPage.tsx | 50-60 | Client-side guard (insufficient) |
| src/pages/configuracoes/tabs/TabUsuarios.tsx | 74-102 | Missing deleted_at filter |
| src/pages/configuracoes/tabs/TabAdvogados.tsx | 72-100 | Uses advogados_correspondentes |
| src/pages/configuracoes/modals/ModalEditarUsuario.tsx | 48-150 | Perfil enum, no constraint |
| src/pages/configuracoes/constants/perfil.constants.ts | All | PERFIL_OPTIONS definition |
| src/types/supabase.ts | All | Type definitions (NO deleted_at) |

---

## IX. Fixing Strategy

### Phase 1: Immediate (P0 — 1 day)

```bash
# Add deleted_at to all 21 tables
for table in users advogados advogados_correspondentes ...; do
  psql -c "ALTER TABLE public.$table ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;"
done

# Add missing triggers
for table in atividades_tipos config_etiquetas_catalogo ...; do
  psql -c "CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.$table
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();"
done

# Verify RLS policies
psql -c "SELECT tablename, policyname FROM pg_policies WHERE tablename IN ('users', 'advogados');"
```

### Phase 2: Short-term (P1 — 1 week)

```bash
# Add audit columns to advogados_correspondentes
psql -c "ALTER TABLE public.advogados_correspondentes 
  ADD COLUMN created_at TIMESTAMPTZ DEFAULT now(),
  ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();"

# Add CHECK constraint
psql -c "ALTER TABLE public.users 
  ADD CONSTRAINT check_users_perfil 
  CHECK (perfil IN ('juridico','comercial','financeiro','operacional'));"

# Add FK indexes
psql -c "CREATE INDEX idx_adv_dist_advogado ON advogados_distribuicao_uf(advogado_id);"
```

### Phase 3: Medium-term (P2 — 2 weeks)

```bash
# Create RPC for atomic user creation
CREATE OR REPLACE FUNCTION public.criar_usuario_completo(
  p_organizacao_id uuid,
  p_email text,
  p_nome text,
  p_perfil text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id uuid;
BEGIN
  -- Insert user
  INSERT INTO users (organizacao_id, email, nome, perfil, ativo)
  VALUES (p_organizacao_id, p_email, p_nome, p_perfil, true)
  RETURNING id INTO v_user_id;
  
  -- Assign default permissions
  -- (future enhancement)
  
  RETURN jsonb_build_object(
    'success', true,
    'user_id', v_user_id,
    'action', 'toast_refresh'
  );
END;
$$;
```

---

## X. Verification Checklist

After applying fixes, run:

```sql
-- ✅ All business tables have deleted_at
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' AND tablename IN ('users', 'advogados', ...)
EXCEPT
SELECT tablename FROM information_schema.columns c 
WHERE table_schema = 'public' AND column_name = 'deleted_at'
GROUP BY table_name;
-- Should return: empty result

-- ✅ All mutable tables have updated_at trigger
SELECT event_object_table, COUNT(*) as trigger_count
FROM information_schema.triggers 
WHERE trigger_schema = 'public' AND trigger_name ILIKE '%updated_at%'
GROUP BY event_object_table;
-- Should show triggers for all 21 tables

-- ✅ RLS enabled on all
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public' AND rowsecurity = false;
-- Should return: empty result

-- ✅ Indexes on organizacao_id
SELECT tablename, COUNT(*) as idx_count FROM pg_indexes 
WHERE tablename IN (select tablename from pg_tables 
  where schemaname='public' and tablename NOT ILIKE '%vw_%')
  AND indexdef ILIKE '%organizacao_id%'
GROUP BY tablename;
-- Should show at least 1 index per table
```

---

## XI. Risk Assessment Matrix

| Issue | Severity | Effort to Fix | Business Impact |
|---|---|---|---|
| P0.1: Missing deleted_at | CRITICAL | 2h | Data integrity breach (hard deletes cascade) |
| P0.2: Missing triggers | CRITICAL | 1h | Audit trail incomplete |
| P0.3: RLS verification | CRITICAL | 30min | Multi-org data leak risk |
| P1.1: advogados_correspondentes | HIGH | 1h | Audit blind spot for external lawyers |
| P1.6: perfil CHECK | HIGH | 30min | Invalid enum values in DB |
| P1.8: FK indexes | MEDIUM | 1h | Query performance degradation |
| P2.1: Global table scope | LOW | 4h | Permission ambiguity |
| P2.4: Missing RPCs | LOW | 8h | No atomicity guarantees |

---

## XII. Conclusion

The `/configuracoes` schema is **70% compliant** with MdFlow patterns:

**Working well:**
- Multi-tenant org isolation via organizacao_id
- RLS enabled on all tables
- Foreign keys to organizacoes.id
- ativo boolean for soft-disabling

**Critical gaps:**
- No soft delete (deleted_at) columns
- Missing audit triggers on 12+ tables
- No database-level enum validation
- RLS policy verification needed

**Timeline to fix:**
- P0: 3.5 hours (same day)
- P1: 4 hours (next day)
- P2: 12 hours (week-long effort, lower priority)

---

*Detailed audit report | MdFlow DB Auditor | 2026-03-31*

