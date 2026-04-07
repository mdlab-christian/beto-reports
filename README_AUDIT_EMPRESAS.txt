================================================================================
DB AUDIT: /EMPRESAS — 2026-04-06
Projeto: qdivfairxhdihaqqypgb | Tabelas auditadas: 4
================================================================================

ÍNDICE DE ARQUIVOS
==================

1. RESUMO EXECUTIVO (comece aqui)
   └─ audit_empresas_SUMMARY.txt
      → Visão rápida: issues P1, SQL de correção, próximos passos
      → Tempo de leitura: 5 minutos

2. RELATÓRIO COMPLETO
   └─ audit_empresas_2026_04_06.md
      → Análise detalhada por tabela (RLS, índices, triggers, FKs, RPCs)
      → Conformidades positivas (10/10)
      → Tempo de leitura: 15 minutos

3. DASHBOARD VISUAL (recomendado)
   └─ audit_empresas_2026_04_06.html
      → Versão interativa em HTML
      → Abra no navegador: open audit_empresas_2026_04_06.html
      → KPIs, tabelas de status, cards de issues

4. QUERIES EXECUTADAS
   └─ audit_queries_executadas.sql
      → Todas as queries SQL usadas na auditoria (22 queries)
      → Comentários explicando cada resultado
      → Útil para re-auditoria manual

5. INSTRUÇÕES PARA APLICAR CORREÇÕES
   └─ APLICAR_CORRECOES.md
      → Como corrigir os 2 issues P1 (passo-a-passo)
      → Checklist, validações, troubleshooting
      → Leia ANTES de executar SQL na produção

6. ESTE ARQUIVO
   └─ README_AUDIT_EMPRESAS.txt


RESUMO DE DESCOBERTAS
=====================

TABELAS AUDITADAS: 4
  ✅ empresas (completa)
  ✅ orgaos_restritivos (completa)
  ❌ empresas_categorias (P1 crítica)
  ⚠️  empresas_escritorios (P2 recomendado)

ISSUES ENCONTRADAS: 3
  [P1] empresas_categorias — Faltam colunas deleted_at + updated_at
  [P1] empresas_categorias — Falta trigger set_updated_at
  [P2] empresas_categorias — Falta índice org_del
  [P2] empresas_escritorios — Falta índice org_del (opcional)

CONFORMIDADES POSITIVAS: 10/10
  • RLS habilitado em 4/4 tabelas
  • Isolamento de tenant: 4/4
  • Foreign Keys: 6/6 válidas
  • RPCs com SECURITY DEFINER: 14/15
  • Sem ENUM nativo: 0 encontrados


FLUXO RECOMENDADO
=================

1. Leia: audit_empresas_SUMMARY.txt (5 min)
2. Visualize: audit_empresas_2026_04_06.html (5 min)
3. Estude: APLICAR_CORRECOES.md (5 min)
4. Execute: SQL em order (passo-a-passo)
5. Valide: queries de validação em APLICAR_CORRECOES.md
6. Comunique: ao time que schema foi atualizado


SQL DE CORREÇÃO RÁPIDO
======================

Execute em ordem (cada um isoladamente):

1. ALTER TABLE public.empresas_categorias 
     ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL,
     ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now() NOT NULL;

2. CREATE OR REPLACE FUNCTION public.update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN NEW.updated_at = now(); RETURN NEW; END;
   $$ LANGUAGE plpgsql SECURITY DEFINER;

   CREATE TRIGGER set_updated_at_empresas_categorias
     BEFORE UPDATE ON public.empresas_categorias
     FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

3. CREATE INDEX IF NOT EXISTS idx_empresas_categorias_org_del 
     ON public.empresas_categorias(organizacao_id) WHERE deleted_at IS NULL;

4. CREATE INDEX IF NOT EXISTS idx_empresas_escritorios_org_del 
     ON public.empresas_escritorios(organizacao_id) WHERE deleted_at IS NULL;


CONTATO
=======

Se encontrar problemas:
  • CTO: Christian (c.paz@mdlab.com.br)
  • Projeto: MdFlow (beta-mdflow)
  • Auditoria: MdFlow DB Auditor (haiku model)
  • Data: 2026-04-06 17:30 UTC

Logs do Supabase: https://app.supabase.com/project/qdivfairxhdihaqqypgb/sql/query


CHECKLIST RÁPIDO
================

Antes de corrigir:
  [ ] Backup do banco realizado
  [ ] Ninguém usando /empresas neste momento
  [ ] Acesso ao SQL Editor do Supabase
  [ ] Lê as instruções em APLICAR_CORRECOES.md

Após corrigir:
  [ ] Todas as 4 queries SQL executadas com sucesso
  [ ] Queries de validação passaram (check: índices, triggers, colunas)
  [ ] Testou UPDATE em empresas_categorias (updated_at muda)
  [ ] Testou DELETE lógico (updated_at = now(), deleted_at = now())
  [ ] Comunicou ao time

Monitoramento:
  [ ] Erro logs vazios (1 hora)
  [ ] Queries antigas ainda funcionam (compatibilidade)
  [ ] Performance das queries com WHERE deleted_at IS NULL


ESTRUTURA DO RELATÓRIO
======================

Cada arquivo segue padrão MdFlow:
  • Português pt-BR (termos técnicos em EN)
  • Markdown e HTML com tokens de cor do DS v5
  • Sem emojis (apenas em SUMMARY para leitura rápida)
  • Queries comentadas e validadas

Versão deste audit: 1.0 (estrutura definitiva)
Próxima auditoria: /pagina_cliente ou /processos (agenda CTO)


================================================================================
                         FIM DO README
================================================================================

Comece por: audit_empresas_SUMMARY.txt
