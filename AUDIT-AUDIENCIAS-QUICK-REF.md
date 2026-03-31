# DB Audit: /audiencias — Quick Reference

**Data:** 2026-03-31 | **Projeto:** qdivfairxhdihaqqypgb (MdFlow) | **Tabela:** audiencias

## Status em Uma Linha

✅ **Tabela OK** | ⚠️ **1 Issue P1 (índices)** | ❓ **1 Issue P2 (trigger)** | **Conformidade 7/10**

---

## O que Está Bom ✅

```
✅ Tabela EXISTS com 23 colunas
✅ Colunas obrigatórias (id, org_id, created_at, updated_at, deleted_at)
✅ RLS ENABLED (filtragem por org funciona)
✅ Soft delete em uso (1 registro deletado verificado)
✅ Foreign keys (processos, usuarios, correspondentes)
✅ Enums em TEXT (tipo, modalidade, status — correto)
✅ Timestamps funcionais
```

---

## O que Precisa Corrigir

### P1 — Índices (CRÍTICO)

**Problema:** Queries lentas em tabelas grandes

**Fix (copiar e colar):**

```sql
CREATE INDEX IF NOT EXISTS idx_audiencias_org_id 
  ON public.audiencias(organizacao_id);

CREATE INDEX IF NOT EXISTS idx_audiencias_org_id_active 
  ON public.audiencias(organizacao_id) 
  WHERE deleted_at IS NULL;
```

**Onde executar:** Supabase → SQL Editor (projeto qdivfairxhdihaqqypgb)

---

### P2 — Trigger updated_at (VERIFICAR)

**Problema:** Não confirmado se trigger existe

**Comando para verificar:**

```sql
SELECT trigger_name FROM information_schema.triggers 
WHERE event_object_table = 'audiencias' 
  AND trigger_name ILIKE '%updated%';
```

**Se vazio, criar:**

```sql
CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.audiencias
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

---

## Colunas Chave

| Coluna | Tipo | Uso |
|--------|------|-----|
| `id` | UUID PK | Identificador |
| `organizacao_id` | UUID | Tenant (RLS) |
| `processo_id` | UUID FK | Vinculo processo |
| `data_audiencia` | DATE/TEXT | Data da audiência |
| `status` | TEXT | enum: cancelada, realizada... |
| `tipo` | TEXT | enum: conciliacao, instrução... |
| `resultado` | JSONB | Resultado (complexo) |
| `deleted_at` | TIMESTAMPTZ | Soft delete |
| `created_at` | TIMESTAMPTZ | Criação |
| `updated_at` | TIMESTAMPTZ | Atualização |

---

## Verificação Rápida

```sql
-- 1. Contar registros
SELECT COUNT(*) FROM public.audiencias;

-- 2. Testar RLS (deve retornar 0 se org está isolada)
SELECT COUNT(*) FROM public.audiencias 
WHERE organizacao_id != '55a0c7ba-1a23-4ae1-b69b-a13811324735';

-- 3. Verificar índice
EXPLAIN ANALYZE
SELECT * FROM public.audiencias 
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735' 
  AND deleted_at IS NULL
LIMIT 10;
-- Se linha menciona "Index Scan" → ✅ OK
-- Se menciona "Seq Scan" → ⚠️ Índice não existe
```

---

## Arquivos de Referência

| Arquivo | Uso |
|---------|-----|
| `audit_audiencias_20260331.md` | Relatório completo (recomendado) |
| `schema_audiencias_admin_verification.sql` | Script SQL admin (verificação total) |
| `audit_audiencias_visual.html` | Relatório visual (stakeholders) |
| `AUDIT-AUDIENCIAS-QUICK-REF.md` | Este arquivo (quick ref) |

---

## Checklist para Implementação

- [ ] Ler `audit_audiencias_20260331.md` (5 min)
- [ ] Copiar SQL de índices
- [ ] Executar em Supabase SQL Editor
- [ ] Rodar `EXPLAIN ANALYZE` para confirmar índice
- [ ] Executar `schema_audiencias_admin_verification.sql` para validação completa
- [ ] Confirmar trigger updated_at existe
- [ ] Fechar issue/task

**Tempo estimado:** 15 min

---

## Contato

Dúvidas? Consulte:
- Spec: `_resumido___audiencias.txt` (se existir)
- Código: `src/components/homepage/homepage_audiencias_dia.tsx`
- Teste E2E: `tests/e2e/audiencias.spec.ts`

---

**Preparado por:** MdFlow DB Auditor (Claude) | **Modo:** Supabase SDK + SQL
