# ICP Telemetria — Auditoria de Schema Supabase

## Tl;dr (30 segundos)

**Pergunta:** Quais campos tenho disponíveis para implementar um agente ICP (Ideal Customer Profile)?

**Resposta:** 8 fatores viáveis imediatamente

| Fator | Fonte | Cobertura | Status |
|-------|-------|-----------|--------|
| Idade | clientes.data_nascimento | 92% | EXCELENTE |
| Profissão | clientes.profissao | 45% | BOM |
| Estado | clientes.endereco_uf | 52% | BOM |
| Valor Causa | processos.valor_causa | 71% | EXCELENTE |
| Fase Processual | processos.fase_processual | 93% | EXCELENTE |
| ICP Score | leads.icp_score | 100% | PERFEITO (pré-calculado) |
| Acordo | processos.acordo_candidato | 100% | PRESENTE |
| Tempo | calculated | 100% | FÁCIL |

**Status:** Implementável com base sólida. Requer enriquecimento para 3 gaps P1.

---

## Documentos Entregues (49 KB)

### 1. ICP_EXEC_SUMMARY.txt (7.6 KB) — **COMECE AQUI**
Resumo executivo em 5 minutos. Para CTO/Tech Lead decidir próximos passos.

**Seções:**
- Resposta Rápida (4 perguntas críticas)
- Fatores ICP Viáveis (força vs fraqueza)
- Problemas Críticos (P0/P1/P2)
- Arquitetura Recomendada
- Próximos Passos (7 tarefas, com prioridade)
- Conclusão com estimativa (2-3 sprints)

**Arquivo:** `~/beto-reports/ICP_EXEC_SUMMARY.txt`

---

### 2. icp_schema_audit_20260406.md (15 KB) — **DOCUMENTAÇÃO COMPLETA**
Auditoria técnica detalhada de todas as tabelas.

**Conteúdo:**
- Leads (64 campos): diagnóstico de dados demográficos esparsos
- Clientes (59 campos): excelente cobertura, gaps de renda e valor
- Processos (134 campos): ótimos valores e fases
- icp_reports: tabela existe mas vazia
- Mdzap (9 tabelas): para enriquecimento via IA
- Gap Analysis com serveridade
- DDL e RPC sugeridos
- Conclusão: implementável com enriquecimento progressivo

**Arquivo:** `~/beto-reports/icp_schema_audit_20260406.md`

---

### 3. icp_schema_audit_20260406.json (9.3 KB) — **INTEGRAÇÃO PROGRAMÁTICA**
Dados estruturados em JSON. Para integração em BI, pipelines, ou validação automática.

**Estrutura:**
```json
{
  "metadata": { ... },
  "tabelas_auditadas": { leads, clientes, processos, icp_reports },
  "fatores_icp_disponiveis": { forte, fraco },
  "gaps_criticos": [ { gap, campo, severidade, solucao }, ... ],
  "recomendacoes": { tabela_sugerida, rpc, campos }
}
```

**Arquivo:** `~/beto-reports/icp_schema_audit_20260406.json`

---

### 4. icp_campos_summary.csv (1.8 KB) — **PARA EXCEL/SHEETS**
Sumário de 21 campos críticos em CSV. Importar direto em planilha.

**Colunas:**
- Tabela, Campo, Tipo, Preenchimento_pct, Contagem, Severidade, Categoria, Uso_ICP

**Arquivo:** `~/beto-reports/icp_campos_summary.csv`

---

### 5. ICP_QUERIES_PRONTAS.sql (10 KB) — **COPIAR/COLAR NO SUPABASE**
10 queries prontas para executar (audit, RPC, samples, agregação, DDL).

**Queries incluídas:**
1. Cobertura demográfica em clientes
2. Cobertura de valores em processos
3. Cobertura em leads
4. RPC para calcular valor recuperável
5. Sample de cliente com todos os fatores
6. Agregação ICP por período
7. Validação de icp_score
8. Estrutura de mdzap_lead_memory
9. Correlação icp_score vs valor
10. DDL completo de icp_telemetria_snapshots + RLS + índices

**Arquivo:** `~/beto-reports/ICP_QUERIES_PRONTAS.sql`

---

### 6. ICP_AUDIT_INDEX.md (5.7 KB) — **ORIENTAÇÃO**
Índice de navegação. Quick answers. Guia por perfil (CTO/Dev/DBA/Analista).

**Arquivo:** `~/beto-reports/ICP_AUDIT_INDEX.md`

---

## 🎯 Quick Reference

### Fatores Disponíveis (use já)
```
✅ idade_anos (92% clientes)
✅ profissao (45% clientes)
✅ estado_uf (52% clientes)
✅ valor_causa (71% processos)
✅ fase_processual (93% processos)
✅ icp_score (100% leads — pré-calculado)
✅ acordo_candidato (100% processos)
✅ tempo_dias_caso (calculável)
```

### Gaps Críticos (enriquecer)
```
❌ renda_mensal (0% — nunca preenchido)
❌ valor_estimado_recuperavel (0% — nunca preenchido)
❌ dados_demograficos_leads (9-11% — muito esparsos)
```

### Arquitetura Recomendada
```
Tabela nova:  icp_telemetria_snapshots
Frequência:   Daily via n8n (01:00 UTC)
RPC:          calcular_icp_agregado(org_id, periodo_dias)
Enriquec.:    OlivIA para campos faltantes
Dashboard:    rolling 90 dias com evolução de KPIs
```

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de campos auditados | 257 (leads 64 + clientes 59 + processos 134) |
| Fatores ICP imediatos | 8 |
| Gaps críticos P1 | 3 |
| Tabela ICP já existe | Sim (icp_reports — vazia) |
| Mdzap para enriquec. | 9 tabelas |
| Estimativa MVP | 2-3 sprints |
| Leads | 44 (dados demográficos esparsos) |
| Clientes | 3.725 (excelente cobertura demográfica) |
| Processos | 14.386 (ótimo para valores) |

---

## 🚀 Próximos Passos (do EXEC_SUMMARY)

### Esta Semana (IMEDIATO)
1. Revisar ICP_EXEC_SUMMARY.txt com team
2. Decidir: RPC SUM vs campo novo para valor_estimado_recuperavel
3. Especificar tabela icp_telemetria_snapshots (SDD)

### Próximas 2 Semanas (CRÍTICO)
4. Implementar RPC fn_cliente_valor_recuperavel_total
5. Criar tabela icp_telemetria_snapshots + RLS + índices
6. n8n workflow para popular daily

### Próximas 4 Semanas (MEDIUM)
7. Integração OlivIA para enriquecimento de leads
8. Dashboard ICP Telemetria
9. Validação de integridade

---

## 🔗 Referências

- **Supabase Project:** qdivfairxhdihaqqypgb
- **Org Midas:** 55a0c7ba-1a23-4ae1-b69b-a13811324735
- **User Teste:** 5fe9f43f-6a88-485c-9689-be486f645ba2
- **CLAUDE.md MdFlow:** ~/beta-mdflow/CLAUDE.md
- **Docs:** ~/beta-mdflow/docs/

---

## 📖 Como Usar Este Relatório

**🎬 Se tem 5 min:**  
→ Leia ICP_EXEC_SUMMARY.txt

**🎬 Se tem 20 min:**  
→ Leia icp_schema_audit_20260406.md

**🎬 Se precisa estruturado:**  
→ Use icp_schema_audit_20260406.json

**🎬 Se precisa em Excel:**  
→ Importe icp_campos_summary.csv

**🎬 Se vai implementar:**  
→ Execute queries de ICP_QUERIES_PRONTAS.sql

**🎬 Se tá perdido:**  
→ Veja ICP_AUDIT_INDEX.md

---

## ✅ Conclusão

**ICP Telemetria é implementável** com dados sólidos atualmente disponíveis.

**Strengths:**
- Clientes têm excelente cobertura demográfica (92% idade)
- Processos têm ótimo valor e fase (71%, 93%)
- Leads já têm icp_score pré-calculado (100%)

**Weaknesses:**
- Renda cliente não capturada (0%)
- Valor estimado recuperável não calculado (0%)
- Dados demográficos em leads muito esparsos (9-11%)

**Recomendação:**
Começar MVP com campos sólidos (idade, profissão, valor_causa, fase) e adicionar progressivamente enriquecimento via OlivIA para gaps.

**Estimativa:** 2-3 sprints para MVP completo + enriquecimento.

---

**Gerado em:** 2026-04-06 18:15 UTC  
**Por:** Claude Code (MdFlow DB Auditor)  
**Válido até:** Próxima auditoria ou schema change

