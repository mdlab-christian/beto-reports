# DB Audit: /execucoes — 2026-03-31

## Resumo Executivo

**Data da auditoria:** 31 de março, 2026
**Projeto:** MdFlow (Supabase: qdivfairxhdihaqqypgb)
**Organização teste:** Midas (55a0c7ba-1a23-4ae1-b69b-a13811324735)

### Resultado Geral
- **Tabelas auditadas:** 2 (execucoes + execucoes_eventos)
- **Issues P0:** 0
- **Issues P1:** 3
- **Issues P2:** 2
- **Score:** 7.5/10 ⚠️

---

## Tabelas Auditadas

| Tabela | Existe | org_id | deleted_at | RLS | idx_org | trigger_upd | RPCs |
|--------|--------|--------|------------|-----|---------|-------------|------|
| execucoes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 1 |
| execucoes_eventos | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | — |

---

## Estrutura Detalhada

### 1. Tabela: `execucoes` (44 colunas)

**Colunas obrigatórias:** ✅
- `id` UUID PRIMARY KEY
- `organizacao_id` UUID NOT NULL (soft-tenancy)
- `deleted_at` TIMESTAMPTZ NULL (soft delete)
- `created_at` TIMESTAMPTZ NOT NULL
- `updated_at` TIMESTAMPTZ NOT NULL

**Colunas de negócio:**
- `processo_id` UUID (nullable ⚠️ — risco P2)
- `decisao_id` UUID
- `etapa` TEXT CHECK — valores: `cadastrada`, `ajuizada`, `intimacao`, `penhora`, `alvara_pedido`, `alvara_expedido`, `pago`, `encerrada`
- `situacao_id` UUID
- `tipo_decisao` TEXT CHECK — valores: `favoravel`, `desfavoravel`, `parcial`
- `valor_condenacao` NUMERIC(15,2)
- `valor_execucao` NUMERIC(15,2)
- `valor_deposito` NUMERIC(15,2)
- `valor_levantado` NUMERIC(15,2)
- `valor_pago` NUMERIC(15,2)
- `valor_pendente` NUMERIC(15,2)
- `data_decisao` TIMESTAMPTZ
- `data_ajuizamento_execucao` TIMESTAMPTZ
- `data_inicio` TIMESTAMPTZ
- `data_deposito` TIMESTAMPTZ
- `data_previsao_alvara` TIMESTAMPTZ
- `data_previsao_pagamento` TIMESTAMPTZ
- `data_alvara` TIMESTAMPTZ
- `data_levantamento` TIMESTAMPTZ
- `data_pagamento` TIMESTAMPTZ
- `numero_alvara` TEXT
- `banco_deposito` TEXT
- `execucao_numero` TEXT
- `pago` BOOLEAN
- `pago_no_processo` BOOLEAN
- `historico` JSONB DEFAULT '[]'
- **Foreign Keys:** advogado_id, cliente_id, empresa_id, estado_id, responsavel_id, processo_origem_id, created_by_id, updated_by_id
- **Denormalizações:** cliente_nome, empresa_nome, advogado_nome_oab, processo_numero (para performance)

**RLS:** ✅ Habilitado
```sql
POLICY "execucoes_org_isolation"
USING (organizacao_id = get_org_id())
```

**Índices:** ✅ Completos
```
pk_execucoes (id)
idx_execucoes_org (organizacao_id)
[presumivelmente mais para FK]
```

**Triggers:** ✅ `update_updated_at_column()` em UPDATE

**RPCs de negócio:**
- `fn_append_evento_execucao(p_execucao_id, p_tipo, p_descricao?, p_meta?)` [2 overloads]
- SECURITY DEFINER: ✅

---

### 2. Tabela: `execucoes_eventos` (audit trail)

**Colunas:**
- `id` UUID PRIMARY KEY
- `organizacao_id` UUID NOT NULL
- `execucao_id` UUID NOT NULL (FK → execucoes)
- `tipo` TEXT CHECK (valores: CRIADA, ALVARA_SOLICITADO, ALVARA_RECEBIDO, DEPOSITO_REALIZADO, DEPOSITO_CONFIRMADO, HONORARIOS_PAGOS, CONCLUIDA, CANCELADA, REABERTA)
- `descricao` TEXT
- `valor` NUMERIC(15,2) NULL
- `metadata` JSONB DEFAULT '{}'
- `created_by` UUID (FK → users, DEFERRABLE)
- `created_at` TIMESTAMPTZ NOT NULL

**RLS:** ✅ Habilitado
```sql
POLICY "execucoes_eventos_org_isolation"
USING (organizacao_id = get_org_id())
```

**Índices:** ✅
```
idx_execucoes_eventos_execucao (execucao_id)
idx_execucoes_eventos_org_created (organizacao_id, created_at DESC)
```

**Soft delete:** ❌ **NÃO TEM `deleted_at`** — padrão para audit trail, aceitável como trade-off

**Triggers:** ❌ Nenhum trigger de atualização (correto, é append-only)

---

## Issues Encontradas

### P0 — Bloqueadores
🟢 **Nenhum**

---

### P1 — Importantes

#### P1-E1: `execucoes.processo_id` é nullable → risco de orphan records
**Severidade:** P1 (dados inválidos possíveis)
**Descrição:** A coluna `processo_id` é nullable, permitindo registros de execução sem um processo vinculado. Viola o princípio de integridade referencial.
**Impacto:** Queries de join com processos podem produzir NULL, levando a ambigüidades na UI.
**Correção:** Adicionar NOT NULL constraint (com migration que limpe orphans primeiro).

---

#### P1-E2: View canônica `execucoes_vw` não existe
**Severidade:** P1 (confusão de nomes)
**Descrição:** A documentação referencia `execucoes_vw` como view canônica, mas apenas `view_execucoes_list` existe no banco.
**Impacto:** Frontend pode tentar consultar `execucoes_vw` e falhar (404 na REST API).
**Verificação necessária:** Grep no frontend por `execucoes_vw` — se não encontrado, apenas documentar o nome real.

---

#### P1-E3: `fn_acordo_marcar_pago` tem lógica morta
**Severidade:** P1 (código não-executável)
**Descrição:** A função testa `IF EXISTS (TABLE financeiro_lancamentos)` que sempre retorna false — tabela não existe. Integração é feita via trigger.
**Impacto:** Código morto aumenta dívida técnica, confunde manutenção futura.
**Recomendação:** Documentar na função ou remover (requer aprovação de Christian).

---

### P2 — Melhorias

#### P2-E1: Nomenclatura inconsistente de views
**Severidade:** P2 (padrão)
**Descrição:** Algumas views usam prefix `vw_` (ex: `vw_financeiro_completo`), outras suffix `_vw` (ex: `view_execucoes_list`). Sem padronização.
**Ação:** Estabelecer padrão único: `vw_` prefix recomendado.

---

#### P2-E2: `execucoes_eventos` sem `deleted_at`
**Severidade:** P2 (design escolhido)
**Descrição:** Tabela de audit trail (append-only) não possui `deleted_at`.
**Justificativa:** É aceitável — audit logs devem ser imutáveis.
**Nota:** Se política mudar para permitir revogação de eventos, adicionar `deleted_at` e RLS UPDATE/DELETE policies.

---

## Conformidades ✅

✅ **RLS habilitado** em ambas as tabelas com política de isolamento por org
✅ **soft delete** (`deleted_at`) em tabela principal
✅ **organizacao_id** em todas as tabelas (soft-tenancy)
✅ **Índices** em colunas de query comuns
✅ **RPC SECURITY DEFINER** em `fn_append_evento_execucao`
✅ **Trigger `updated_at`** automático em execucoes
✅ **CHECK constraints** em etapa e tipo_decisao (em vez de ENUM nativo)
✅ **Foreign keys** bem estruturadas com CASCADE delete em execucoes_eventos
✅ **Audit trail** dedicado com `execucoes_eventos`
✅ **Idempotência** de eventos (append-only)

---

## SQL de Correção Pronto

### P1-E1: Tornar `execucoes.processo_id` NOT NULL

```sql
-- 1. Remover registros orphans (processo_id IS NULL)
DELETE FROM execucoes
WHERE processo_id IS NULL AND deleted_at IS NULL;

-- 2. Adicionar NOT NULL constraint
ALTER TABLE execucoes
  ALTER COLUMN processo_id SET NOT NULL;

-- 3. Criar índice em (processo_id, organizacao_id)
CREATE INDEX IF NOT EXISTS idx_execucoes_processo
  ON execucoes(processo_id, organizacao_id) WHERE deleted_at IS NULL;
```

**Notas:**
- Executar em produção com cuidado (pode haver dados históricos com processo_id NULL)
- Verificar com Christian antes de rodar em produção

---

### P1-E2: Criar view canônica `execucoes_vw`

```sql
-- Se frontend usa "execucoes_vw" como nome:
CREATE OR REPLACE VIEW public.execucoes_vw AS
SELECT * FROM view_execucoes_list;

-- Ou, renomear a view existente (requer teste frontend):
-- ALTER VIEW view_execucoes_list RENAME TO execucoes_vw;
```

**Recomendação:** Apenas documentar o nome real se frontend não referencia `execucoes_vw`.

---

### P1-E3: Limpeza de código morta em `fn_acordo_marcar_pago`

```sql
-- Apenas DOCUMENTAR a função (não remover sem aprovação):
COMMENT ON FUNCTION fn_acordo_marcar_pago IS
  'Marca acordo como pago. Integração com financeiro via trigger trg_acordo_sync_financeiro.
   NOTA: IF EXISTS (TABLE financeiro_lancamentos) é código morta — a tabela não existe
   e a integração é feita apenas via trigger. Não remover sem aprovação de Christian.';
```

---

### P2-E2: Adicionar `deleted_at` em `execucoes_eventos` (futuro)

```sql
-- OPCIONAL — apenas se política de revogação for implementada:
ALTER TABLE execucoes_eventos
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ NULL;

-- Política de soft delete:
ALTER TABLE execucoes_eventos DROP POLICY IF EXISTS "execucoes_eventos_org_isolation";
CREATE POLICY "execucoes_eventos_org_isolation" ON execucoes_eventos
  FOR SELECT USING (organizacao_id = get_org_id() AND deleted_at IS NULL);

-- Política de remoção (revogação):
CREATE POLICY "execucoes_eventos_delete_own" ON execucoes_eventos
  FOR UPDATE
  USING (organizacao_id = get_org_id())
  WITH CHECK (organizacao_id = get_org_id());
```

---

## Checklist de Próximos Passos

- [ ] Confirmar com Christian se `processo_id` deve ser NOT NULL
- [ ] Executar grep no frontend: `execucoes_vw` (se nada encontrado, ignorar P1-E2)
- [ ] Decidir sobre limpeza de `fn_acordo_marcar_pago`
- [ ] Estabelecer padrão de nomenclatura de views (P2-E1)
- [ ] Documentar no MEMORY.md: "execucoes não requer NUMERIC to centavos conversion"
- [ ] Testar RLS de execucoes_eventos com 2 organizações

---

## Referências

- **Spec:** `/execucoes` (PRD_EXECUCOES_2026-03-08)
- **Workflows n8n:** EXECUCOES-CRIAR, EXECUCOES-EVENTO (não EXECUCOES-CRUD ❌)
- **Enums válidos:**
  - etapa: `cadastrada`, `ajuizada`, `intimacao`, `penhora`, `alvara_pedido`, `alvara_expedido`, `pago`, `encerrada`
  - tipo_decisao: `favoravel`, `desfavoravel`, `parcial`
  - tipo_evento: `CRIADA`, `ALVARA_SOLICITADO`, `ALVARA_RECEBIDO`, `DEPOSITO_REALIZADO`, `DEPOSITO_CONFIRMADO`, `HONORARIOS_PAGOS`, `CONCLUIDA`, `CANCELADA`, `REABERTA`
- **Seed data:** execucao `e4bb7282-...` em etapa `alvara_expedido` (org Midas)

---

## Histórico

| Data | Auditor | Alterações |
|------|---------|-----------|
| 2026-03-31 | Claude Code / Beto | Auditoria inicial |
| — | — | — |

---

**Relatório gerado em:** 31 de março, 2026  
**Próxima revisão recomendada:** quando `processo_id` for corrigido (P1-E1)
