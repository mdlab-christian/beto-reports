# Aplicar Correções — DB Audit /empresas

## ⚠️ Resumo das Correções Necessárias

| Prioridade | Tipo | Tabela | Problema | Status |
|---|---|---|---|---|
| P1 | Coluna | `empresas_categorias` | Faltam `deleted_at` + `updated_at` | 🚨 URGENTE |
| P1 | Trigger | `empresas_categorias` | Falta `set_updated_at` automático | 🚨 URGENTE |
| P1 | Índice | `empresas_categorias` | Falta `idx_*_org_del` (WHERE deleted_at IS NULL) | 🚨 URGENTE |
| P2 | Índice | `empresas_escritorios` | Falta `idx_*_org_del` (complementar) | ⚠️ RECOMENDADO |

---

## 🚀 Passo 1: Adicionar Colunas em empresas_categorias

**O quê:** Adicionar `deleted_at` (soft delete) e `updated_at` (auditoria).

**Por quê:** Sem essas colunas, exclusões de categorias quebram FK com `empresas` (que referencia categoria_id). Sem `updated_at`, não há auditoria de mudanças.

```sql
ALTER TABLE public.empresas_categorias 
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now() NOT NULL;
```

**Status após:** 
- Coluna `deleted_at` adicionada (nullable, default NULL)
- Coluna `updated_at` adicionada (NOT NULL, default now())
- Dados históricos terão `updated_at = created_at` (de forma implícita)

**Testar:**
```sql
SELECT * FROM empresas_categorias LIMIT 1;
-- Verificar colunas deleted_at e updated_at presentes
```

---

## 🚀 Passo 2: Criar Trigger para updated_at

**O quê:** Criar trigger que atualiza `updated_at` automaticamente em UPDATEs.

**Por quê:** Sem o trigger, campo não é atualizado — fica com timestamp de criação.

```sql
-- Função (se não existir)
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger específico para esta tabela
CREATE TRIGGER set_updated_at_empresas_categorias
  BEFORE UPDATE ON public.empresas_categorias
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();
```

**Status após:**
- Trigger `set_updated_at_empresas_categorias` criado
- Função `update_updated_at_column` existente (reutilizável)

**Testar:**
```sql
-- Atualizar uma categoria
UPDATE empresas_categorias 
  SET nome = 'Novo Nome' 
  WHERE id = 'uuid-da-categoria'
  RETURNING id, nome, updated_at;

-- Verificar que updated_at foi atualizado
SELECT updated_at FROM empresas_categorias WHERE id = 'uuid-da-categoria';
```

---

## 🚀 Passo 3: Criar Índice WHERE deleted_at IS NULL

**O quê:** Criar índice `idx_empresas_categorias_org_del` para otimizar queries de categorias ativas.

**Por quê:** Padrão em MdFlow — queries filtrando ativos devem usar índice.

```sql
CREATE INDEX IF NOT EXISTS idx_empresas_categorias_org_del 
  ON public.empresas_categorias(organizacao_id) 
  WHERE deleted_at IS NULL;
```

**Status após:**
- Índice criado (se não existir)
- Queries com `WHERE organizacao_id = X AND deleted_at IS NULL` usarão este índice

**Testar:**
```sql
-- Verificar índice foi criado
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'empresas_categorias' 
  AND indexname LIKE '%org_del%';

-- Verificar que EXPLAIN usa o índice
EXPLAIN SELECT * FROM empresas_categorias 
  WHERE organizacao_id = '55a0c7ba-1a23-4ae1-b69b-a13811324735' 
    AND deleted_at IS NULL;
```

---

## 🚀 Passo 4 (OPCIONAL P2): Criar Índice em empresas_escritorios

**O quê:** Criar índice `idx_empresas_escritorios_org_del` (complementar).

**Por quê:** Consistência com outras tabelas. Não é crítico (tabela já tem outros índices).

```sql
CREATE INDEX IF NOT EXISTS idx_empresas_escritorios_org_del 
  ON public.empresas_escritorios(organizacao_id) 
  WHERE deleted_at IS NULL;
```

---

## 📋 Checklist de Execução

### Antes de começar
- [ ] Backup do banco (Supabase Dashboard > Database > Backups)
- [ ] Verificar que ninguém está usando `/empresas` neste momento
- [ ] Ter acesso ao Supabase Management Console ou SQL Editor

### Execução
- [ ] **Passo 1:** ALTER TABLE (colunas)
- [ ] **Passo 2:** CREATE FUNCTION + CREATE TRIGGER
- [ ] **Passo 3:** CREATE INDEX (org_del)
- [ ] **Passo 4 (opcional):** CREATE INDEX (org_del em empresas_escritorios)

### Validação
- [ ] Verificar que colunas foram criadas: `SELECT column_name FROM information_schema.columns WHERE table_name = 'empresas_categorias'`
- [ ] Verificar que trigger existe: `SELECT trigger_name FROM information_schema.triggers WHERE event_object_table = 'empresas_categorias'`
- [ ] Verificar que índices existem: `SELECT indexname FROM pg_indexes WHERE tablename = 'empresas_categorias'`
- [ ] Testar UPDATE (verificar que updated_at muda)
- [ ] Testar DELETE lógico: `UPDATE ... SET deleted_at = now()`
- [ ] Testar query com WHERE deleted_at IS NULL

### Pós-execução
- [ ] Comunicar ao time que schema foi atualizado
- [ ] Atualizar documentação de schema
- [ ] Monitorar logs de erro durante 1 hora (podem haver queries antigas incompatíveis)

---

## ⚠️ Possíveis Problemas e Soluções

### Problema 1: "Coluna já existe"
```
ERROR: column "deleted_at" of relation "empresas_categorias" already exists
```
**Solução:** Usar `IF NOT EXISTS` (já está no script acima) — será ignorado.

### Problema 2: "Trigger já existe"
```
ERROR: trigger "set_updated_at_empresas_categorias" for relation "empresas_categorias" already exists
```
**Solução:** Dropar antes: `DROP TRIGGER IF EXISTS set_updated_at_empresas_categorias ON empresas_categorias;`

### Problema 3: Índice não muda plano de execução
```
EXPLAIN mostra "Seq Scan" em vez de "Index Scan"
```
**Solução:** 
1. Executar `ANALYZE empresas_categorias;` para atualizar estatísticas
2. Esperar 5 minutos (Supabase atualiza periodicamente)
3. Verificar se query tem `WHERE deleted_at IS NULL` (obrigatório para usar índice)

### Problema 4: Queries antigas quebram
Se frontend/n8n usa `SELECT * FROM empresas_categorias` sem `WHERE deleted_at IS NULL`:
- **Antes:** Retorna todas (deletadas + ativas)
- **Depois:** Idem (não muda resultado)
- **Ação:** Nenhuma — compatível para trás

---

## 🔍 Queries de Validação (execute após cada passo)

```sql
-- Validar Passo 1
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'empresas_categorias'
  AND column_name IN ('deleted_at', 'updated_at')
ORDER BY column_name;
-- Esperado: 2 linhas (deleted_at e updated_at)

-- Validar Passo 2
SELECT trigger_name, event_manipulation, action_timing
FROM information_schema.triggers
WHERE event_object_table = 'empresas_categorias' AND trigger_schema = 'public';
-- Esperado: 1 linha (set_updated_at_empresas_categorias, UPDATE, BEFORE)

-- Validar Passo 3
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'empresas_categorias' AND indexname LIKE '%org_del%';
-- Esperado: 1 linha (idx_empresas_categorias_org_del com WHERE deleted_at IS NULL)

-- Validar Passo 4 (optional)
SELECT indexname FROM pg_indexes
WHERE tablename = 'empresas_escritorios' AND indexname LIKE '%org_del%';
-- Esperado: 1 linha (idx_empresas_escritorios_org_del)
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verificar logs do Supabase Dashboard (Database tab)
2. Testar cada comando isoladamente (não executar todos de uma vez)
3. Comparar com schema de outras tabelas (orgaos_restritivos, empresas)
4. Contactar: CTO Christian (c.paz@mdlab.com.br)

---

**Status:** PRONTO PARA APLICAÇÃO  
**Data de Criação:** 2026-04-06  
**Prioridade:** P1 (crítica — afeta soft delete)
