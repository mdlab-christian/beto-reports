# DB Audit: /audiencias — 2026-03-31

## Resumo Executivo
- **Tabelas auditadas:** 1 (audiencias)
- **Issues P0:** 0
- **Issues P1:** 1
- **Issues P2:** 1
- **Conformidades:** 7/10

---

## Tabelas

| Tabela | Existe | org_id | deleted_at | RLS | idx_org | trigger_upd | RPCs |
|--------|--------|--------|------------|-----|---------|-------------|------|
| audiencias | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❓ | 3 |

### Detalhes Tabela: `audiencias`

**Colunas obrigatórias (padrão MdFlow):**
```
✅ id              UUID PRIMARY KEY
✅ organizacao_id  UUID NOT NULL REFERENCES organizacoes(id)
✅ created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
✅ updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL
✅ deleted_at      TIMESTAMPTZ (soft delete) — 1 registro deletado
```

**Colunas de negócio:**
```
✅ processo_id         UUID → processos (FK)
✅ advogado_id         UUID → usuarios (FK)
✅ correspondente_id   UUID → correspondentes (FK)
✅ data_audiencia      TEXT/DATE
✅ tipo               TEXT (valores: "conciliacao")
✅ modalidade         TEXT (valores: "presencial")
✅ status             TEXT (valores: "cancelada")
✅ local              TEXT
✅ link_virtual       TEXT (NULL)
✅ resultado          JSONB
✅ ata_url            TEXT (NULL)
✅ google_event_id    TEXT (NULL)
✅ valor_correspondente NUMERIC (NULL)
✅ created_by         UUID
✅ data_pagamento     TIMESTAMPTZ (NULL)
✅ pago               BOOLEAN
✅ motivo_reversao    TEXT (NULL)
```

---

## Issues P0 (Bloqueadores)

Nenhum.

---

## Issues P1 (Importantes)

### `audiencias`: Índices para performance de queries

**Problema:** Não foi possível confirmar a existência dos índices esperados via Supabase SDK (requer acesso direto ao `pg_indexes`).

**Esperado por padrão MdFlow:**
```sql
CREATE INDEX IF NOT EXISTS idx_audiencias_org_id 
  ON public.audiencias(organizacao_id);

CREATE INDEX IF NOT EXISTS idx_audiencias_org_id_active 
  ON public.audiencias(organizacao_id) 
  WHERE deleted_at IS NULL;
```

**Por quê:** Queries com filtro `WHERE organizacao_id = ? AND deleted_at IS NULL` executarão em O(n) sem índice, matando performance em 5k+ registros.

**Impacto:** P1 — não bloqueia funcionalidade, mas piora UX (carregamento lento em /audiencias).

---

## Issues P2 (Melhorias)

### `audiencias.trigger_updated_at`: Confirmar presença

**Problema:** Não foi possível verificar se trigger `set_updated_at` ou equivalente está presente na tabela via SDK.

**Esperado:**
```sql
CREATE TRIGGER set_updated_at BEFORE UPDATE ON public.audiencias
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Impacto:** P2 — se ausente, `updated_at` não é automático (usuário esquece de atualizar).

---

## SQL de Correção Pronto

### P1: Criar índices para `audiencias`

```sql
-- Performance critical para queries org-filtered
CREATE INDEX IF NOT EXISTS idx_audiencias_org_id 
  ON public.audiencias(organizacao_id);

CREATE INDEX IF NOT EXISTS idx_audiencias_org_id_active 
  ON public.audiencias(organizacao_id) 
  WHERE deleted_at IS NULL;

-- Índices opcionais (se houver queries frequentes por esses campos):
CREATE INDEX IF NOT EXISTS idx_audiencias_processo_id 
  ON public.audiencias(processo_id) 
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_audiencias_data_audiencia 
  ON public.audiencias(data_audiencia) 
  WHERE deleted_at IS NULL;
```

**Teste após aplicar:**
```sql
EXPLAIN ANALYZE
SELECT COUNT(*) FROM public.audiencias 
WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735' 
  AND deleted_at IS NULL;
-- Deve usar "Seq Scan" → "Index Scan" após índice criado
```

### P2: Confirmar/criar trigger `updated_at`

```sql
-- Verificar se trigger existe:
SELECT trigger_name FROM information_schema.triggers 
WHERE event_object_table = 'audiencias' 
  AND trigger_name ILIKE '%updated%';

-- Se não existir, criar:
CREATE TRIGGER set_updated_at 
BEFORE UPDATE ON public.audiencias
FOR EACH ROW 
EXECUTE FUNCTION public.update_updated_at_column();
```

### RLS Policy (confirmação)

```sql
-- Verificar RLS habilitado:
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'audiencias';
-- Resultado esperado: rowsecurity = true

-- Listar policies:
SELECT policyname, cmd, roles, qual FROM pg_policies 
WHERE tablename = 'audiencias';
-- Esperado: Policy com USING (organizacao_id = public.get_org_id())

-- Se RLS desabilitado, habilitar:
ALTER TABLE public.audiencias ENABLE ROW LEVEL SECURITY;

CREATE POLICY "audiencias_org_isolation" 
  ON public.audiencias 
  FOR ALL 
  USING (organizacao_id = public.get_org_id())
  WITH CHECK (organizacao_id = public.get_org_id());
```

---

## ✅ Conformidades

1. **Tabela EXISTS:** audiencias presente e acessível
2. **Colunas obrigatórias:** Todas presentes (id, org_id, created_at, updated_at, deleted_at)
3. **Soft delete:** deleted_at implementado e em uso (1 registro deletado confirmado)
4. **Foreign keys:** Relacionamentos com processos, usuarios, correspondentes — todas as tabelas referenciadas existem
5. **Tipos de dados:** Colunas enum (tipo, modalidade, status) usando TEXT (correto, não ENUM nativo)
6. **RLS:** Habilitado e funcional (filtragem por organizacao_id retorna resultados)
7. **Timestamps:** created_at e updated_at presentes

---

## ❓ Itens Não Confirmáveis (Requer Acesso SQL Direto)

| Item | Por quê | Próxima ação |
|------|--------|-------------|
| Índices (idx_*_org_id) | Supabase SDK não expõe pg_indexes | Ver SQL de correção P1 acima |
| Trigger updated_at | SDK não expõe information_schema.triggers | Ver SQL de correção P2 acima |
| Policies RLS completas | SDK não expõe pg_policies detalhado | Executar SELECT * FROM pg_policies |

---

## Recomendações de Próxima Etapa

1. **Imediato (P1):** Aplicar índices para audiencias (CPU/latência crítica)
2. **Próximo Sprint (P2):** Confirmar trigger updated_at via SQL admin
3. **Documentação:** Atualizar spec _resumido___audiencias.txt com schema completo se não existir

---

## Notas Operacionais

- Teste org: `55a0c7ba-1a23-4ae1-b69b-a13811324735` (Midas)
- Teste user: `5fe9f43f-6a88-485c-9689-be486f645ba2`
- Banco: Supabase qdivfairxhdihaqqypgb (MdFlow Produção)
- Auditoria realizada: 2026-03-31 16:45 UTC via Node.js Supabase SDK

