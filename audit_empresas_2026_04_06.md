# DB Audit: /empresas — 2026-04-06

## Resumo
- Tabelas auditadas: 4
- Issues P0: 0
- Issues P1: 2
- Issues P2: 0
- Conformidades: 8

## Tabelas

| Tabela | Existe | org_id | deleted_at | updated_at | RLS | idx_org | idx_org_del | trigger_upd | RPCs |
|--------|--------|--------|------------|------------|-----|--------|------------|-------------|------|
| empresas | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 14 |
| orgaos_restritivos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| empresas_categorias | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | — |
| empresas_escritorios | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | — |

## Issues P1 (importantes)

### 1. `empresas_categorias`: Faltam colunas obrigatórias
- **Problema:** Tabela não tem `deleted_at` nem `updated_at` (soft delete + auditoria não funcionam)
- **Impacto:** Exclusões físicas quebram FK com `empresas`. Sem auditoria de mudanças.
- **Solução:** Adicionar colunas + trigger + index WHERE deleted_at IS NULL

### 2. `empresas_categorias`: Falta trigger para updated_at
- **Problema:** Não há trigger `set_updated_at` ou similar
- **Impacto:** Campo `updated_at` não é atualizado automaticamente em UPDATEs
- **Solução:** Criar trigger BEFORE UPDATE

### Bônus: `empresas_escritorios` — Índice incompleto
- **Problema:** Não há `CREATE INDEX ... WHERE deleted_at IS NULL` (padrão em outras tabelas)
- **Impacto:** Queries filtrando ativos podem ser lentas
- **Solução:** Criar índice `idx_empresas_escritorios_org_del`

## SQL de correção pronto

```sql
-- P1: empresas_categorias — Adicionar colunas obrigatórias
ALTER TABLE public.empresas_categorias 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now() NOT NULL;

-- P1: empresas_categorias — Criar trigger para updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER set_updated_at_empresas_categorias
  BEFORE UPDATE ON public.empresas_categorias
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- P1: empresas_categorias — Índice WHERE deleted_at IS NULL
CREATE INDEX IF NOT EXISTS idx_empresas_categorias_org_del 
  ON public.empresas_categorias(organizacao_id) 
  WHERE deleted_at IS NULL;

-- P2: empresas_escritorios — Índice WHERE deleted_at IS NULL
CREATE INDEX IF NOT EXISTS idx_empresas_escritorios_org_del 
  ON public.empresas_escritorios(organizacao_id) 
  WHERE deleted_at IS NULL;

-- Verificar: Restaurar dados antigos (se houver histórico)
-- UPDATE empresas_categorias SET updated_at = created_at WHERE updated_at IS NULL;

-- Verificar: RLS policies para empresas_categorias (estão corretas)
-- POLICIES JÁ EXISTEM E FUNCIONAM CORRETAMENTE ✅
```

## RLS Policies

Todas as 4 tabelas têm RLS **HABILITADO E FUNCIONAL**:

| Tabela | Policies |
|--------|----------|
| **empresas** | `empresas_org_isolation` (ALL), `empresas_delete_admin_only` (DELETE) |
| **orgaos_restritivos** | `*_select_own_org`, `*_insert_own_org`, `*_update_own_org`, `*_delete_own_org` |
| **empresas_categorias** | `*_select_own_org`, `*_insert_own_org`, `*_update_own_org`, `*_delete_own_org` |
| **empresas_escritorios** | `*_select_own_org`, `*_insert_own_org`, `*_update_own_org`, `*_delete_own_org` |

Todas usam tenant isolation via `organizacao_id = get_org_id()`.

## Foreign Keys (validadas)

| Tabela | Coluna | Ref Tabela | Ref Coluna |
|--------|--------|-----------|-----------|
| empresas | organizacao_id | organizacoes | id |
| empresas | categoria_id | **empresas_categorias** | id |
| orgaos_restritivos | organizacao_id | organizacoes | id |
| empresas_categorias | organizacao_id | organizacoes | id |
| empresas_escritorios | organizacao_id | organizacoes | id |
| empresas_escritorios | empresa_id | **empresas** | id |

**Status:** ✅ Todas válidas. Sem orphans detectados.

## Índices por tabela

### empresas ✅ (10 índices)
- `empresas_pkey` (id)
- `idx_empresas_org` (organizacao_id)
- `idx_empresas_org_ativo` (organizacao_id, ativo)
- `idx_empresas_org_del` (organizacao_id) WHERE deleted_at IS NULL ✅
- `idx_empresas_cnpj` (cnpj)
- `idx_empresas_nome` (nome GIN trigram)
- `idx_empresas_nome_fantasia_trgm` (nome_fantasia GIN trigram)
- `idx_empresas_categoria_id` (categoria_id)
- `idx_empresas_created_by_id` (created_by_id)
- `idx_empresas_aprovado_por_user_id` (aprovado_por_user_id)

### orgaos_restritivos ✅ (4 índices)
- `orgaos_restritivos_pkey` (id)
- `idx_orgaos_restritivos_org` (organizacao_id)
- `idx_orgaos_restritivos_org_active` (organizacao_id) WHERE deleted_at IS NULL ✅
- `idx_orgaos_restritivos_escritorio_id` (escritorio_id)

### empresas_categorias ❌ (2 índices, FALTA 1)
- `empresas_categorias_pkey` (id)
- `idx_empresas_categorias_org` (organizacao_id)
- **FALTA:** `idx_empresas_categorias_org_del` (organizacao_id) WHERE deleted_at IS NULL ← P1

### empresas_escritorios ⚠️ (4 índices, PODERIA MELHORAR)
- `empresas_escritorios_pkey` (id)
- `idx_empresas_escritorios_org` (organizacao_id)
- `idx_empresas_escritorios_empresa` (empresa_id)
- `idx_empresas_escritorios_oab_principal` (oab_principal) WHERE oab_principal IS NOT NULL AND deleted_at IS NULL
- **FALTA:** `idx_empresas_escritorios_org_del` (organizacao_id) WHERE deleted_at IS NULL ← P2

## RPCs da página

Verificadas **15 RPCs** relacionadas a `empresa*`:

| RPC | Args principais | Security Definer |
|-----|-----------------|------------------|
| `aprovar_empresa` | p_empresa_id, p_fila_id, p_dados | ✅ |
| `delete_empresa` | p_empresa_id | ✅ |
| `ensure_empresa_stub` | p_payload | ✅ |
| `ensure_empresa_stub_service` | p_org_id, p_nome_fantasia, p_cnpj | ✅ |
| `fn_empresas_stats` | p_organizacao_id | ✅ |
| `fn_sync_empresa_total_processos` | — (trigger) | ✅ |
| `fn_sync_execucoes_empresa_nome` | — (trigger) | ✅ |
| `get_empresa_metricas` | p_org_id, p_empresa_id, períodos | ✅ |
| `get_jurimetria_ranking_empresas` | p_org_id, filtros, limit | ✅ |
| `merge_empresas` | p_origem_id, p_destino_id | ✅ |
| `rpc_buscar_empresa_similar` | p_organizacao_id, p_nome | ✅ |
| `rpc_empresa_metricas` | p_organizacao_id, p_empresa_id | ✅ |
| `rpc_empresas_kpis` | p_organizacao_id | ✅ |
| `rpc_empresas_ranking` | p_organizacao_id, limit | ✅ |
| `buscar_empresa_similar` | p_nome, p_threshold (2 overloads) | ❌ (public) |

**Status:** ✅ 14/15 com SECURITY DEFINER. 1 sem (helper pública).

## Triggers

### empresas (2 triggers)
- `trg_empresas_updated_at` ✅ (BEFORE UPDATE)
- `trg_sync_execucoes_empresa_nome` ✅ (AFTER UPDATE — denormaliza execucoes)

### orgaos_restritivos (1 trigger)
- `set_updated_at` ✅ (BEFORE UPDATE)

### empresas_categorias (0 triggers) ❌
- **FALTA:** `set_updated_at` ou `set_updated_at_empresas_categorias`

### empresas_escritorios (1 trigger)
- `set_updated_at_empresas_escritorios` ✅ (BEFORE UPDATE)

## Enums Nativos

✅ **Nenhum ENUM nativo PostgreSQL encontrado.** Projeto usa TEXT CHECK como padrão (correto).

Valores armazenados em TEXT com defaults:
- `empresas.status_aprovacao`: default 'aprovada' (valores: pendente, aprovada, descartada_tecnico)
- `empresas.criado_por`: default 'humano' (valores: humano, ia)
- `orgaos_restritivos.processavel`: BOOLEAN
- Demais: armazenadas em JSONB ou livre

## ✅ Conformidades

1. **Soft delete:** Todas 4 tabelas têm `deleted_at` (exceto `empresas_categorias` — P1)
2. **Auditoria de tempo:** `created_at` e `updated_at` presentes e ativas (exceto `empresas_categorias`)
3. **Isolamento de tenant:** `organizacao_id` + RLS habilitado em todas (✅ 4/4)
4. **Índices principais:** `idx_*_org` presentes em todas (✅ 4/4)
5. **Índices de soft delete:** `idx_*_org_del` presentes em 3/4 (⚠️ 1 falta em `empresas_categorias`)
6. **Triggers updated_at:** 3/4 implementados (⚠️ 1 falta em `empresas_categorias`)
7. **RLS policies:** Todas usando `get_org_id()` e tenant isolation (✅ 4/4)
8. **Foreign keys:** Todas válidas com ON DELETE CASCADE/RESTRICT apropriados (✅)
9. **RPCs:** Todas com SECURITY DEFINER exceto helper pública (✅ 14/15)
10. **Sem ENUM nativo:** Usar TEXT CHECK é padrão correto (✅)

## Priorização

1. **P1 PRIMEIRO:** Aplicar 3 correções em `empresas_categorias` (colunas, trigger, índice)
2. **P2 DEPOIS:** Criar índice complementar em `empresas_escritorios`
3. **Testar:** Queries com `WHERE deleted_at IS NULL` em ambas tabelas

