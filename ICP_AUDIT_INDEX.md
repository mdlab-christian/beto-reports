# ICP Telemetria — Schema Audit Report Index

**Data:** 2026-04-06  
**Org:** Midas (55a0c7ba-1a23-4ae1-b69b-a13811324735)  
**Objetivo:** Mapear campos disponíveis para implementação de agente ICP Ideal Customer Profile

---

## 📄 Arquivos Gerados

### 1. **ICP_EXEC_SUMMARY.txt** (7.6 KB, 171 linhas)
Resumo executivo para decisão rápida.

**Conteúdo:**
- ✅ Resposta rápida: campos demográficos, valor, ICP, mdzap
- ✅ Fatores ICP viáveis (força vs fraqueza)
- ✅ Problemas críticos (P0/P1/P2)
- ✅ Arquitetura recomendada
- ✅ Próximos passos ordenados
- ✅ Conclusão e estimativa de esforço

**Use quando:** Precisa de decisão em 5 minutos.

---

### 2. **icp_schema_audit_20260406.md** (15 KB, 386 linhas)
Relatório técnico detalhado de auditoria de schema.

**Conteúdo:**
- Tabelas auditadas: leads (64 campos), clientes (59), processos (134), icp_reports
- Campos demográficos com preenchimento (%)
- Campos de valor e scoring
- Campos de engajamento e processual
- Gap analysis com severidade
- Recomendações de DDL para `icp_telemetria_snapshots`
- Exemplo de RPC `calcular_icp_agregado()`

**Use quando:** Precisa entender detalhes técnicos e estrutura completa.

---

### 3. **icp_schema_audit_20260406.json** (9.3 KB, 311 linhas)
Dados estruturados em JSON para consumo programático.

**Conteúdo:**
- metadata (data, org, escopo)
- tabelas_auditadas (leads, clientes, processos, icp_reports)
  - campos_demograficos com detalhe
  - campos_valor
  - diagnostico por tabela
- tabelas_mdzap (lista + relevância)
- fatores_icp_disponiveis (forte vs fraco)
- gaps_criticos (com solução)
- recomendacoes (tabela sugerida, RPC, campos)
- proximos_passos

**Use quando:** Precisa integrar dados em sistema ou gerar visualização.

---

### 4. **icp_campos_summary.csv** (1.8 KB, 22 linhas)
Sumário em CSV para importar em Excel/sheets.

**Colunas:**
| Tabela | Campo | Tipo | Preenchimento_pct | Contagem | Severidade | Categoria | Uso_ICP |

**Use quando:** Precisa filtrar/ordenar campos em planilha.

---

## 🎯 Quick Answers

### "Quais campos tenho para análise de perfil?"

**Resposta curta:** 8 fatores viáveis imediatamente

1. **idade_anos** ← clientes.data_nascimento (92% cobertura) ✅ EXCELENTE
2. **profissao** ← clientes.profissao (45% cobertura) ✅ BOM
3. **estado_uf** ← clientes.endereco_uf (52% cobertura) ✅ BOM
4. **valor_causa** ← processos.valor_causa (71% cobertura) ✅ EXCELENTE
5. **fase_processual** ← processos.fase_processual (93% cobertura) ✅ EXCELENTE
6. **icp_score** ← leads.icp_score (100% pré-calculado) ✅ PERFEITO
7. **acordo_candidato** ← processos.acordo_candidato (100% presente) ✅ PRESENTE
8. **tempo_dias_caso** ← calculado from timestamps ✅ FÁCIL

### "Tem valor do processo?"

**Sim:** processos.valor_causa (71% preenchimento, excelente)

**Não:** clientes não têm valor_total_estimado_recuperavel (0%)
- **Solução:** Agregar SUM(processos.valor_causa) por cliente em RPC

### "Tem renda do cliente?"

**Não:** clientes.renda_mensal é sempre NULL (0%)
- **Problema:** P1 — fator-chave de ICP ausente
- **Solução:** Enriquecer via Advbox API ou OlivIA

### "Tem dados demográficos em leads?"

**Quase nada:**
- data_nascimento: 9% (4 de 44 leads)
- profissao: 2% (1 de 44 leads)
- estado: 11% (5 de 44 leads)
- **Problema:** P1 — leads não recebem qualificação
- **Solução:** Integrar OlivIA na captação + mdzap

### "Tabela ICP já existe?"

**Sim:** icp_reports (9 campos estruturados)
- **Status:** Vazia (0 registros)
- **Recomendação:** Criar tabela nova `icp_telemetria_snapshots` com dados agregados

---

## 📊 Estatísticas Resumidas

| Métrica | Valor | Status |
|---------|-------|--------|
| Leads | 44 | Muito poucos dados demográficos |
| Clientes | 3.725 | Excelente cobertura demográfica |
| Processos | 14.386 | Ótimo para valores e fase |
| Campos viáveis imediatamente | 8 | Pronto para MVP |
| Gaps críticos (P1) | 3 | Requerem enriquecimento |
| Tabela ICP já existe | ✅ Sim | Mas vazia |
| Mdzap disponível | ✅ 9 tabelas | Para enriquecimento |

---

## 🔧 Próximos Passos Recomendados

### IMEDIATO (esta semana)
1. Revisar ICP_EXEC_SUMMARY.txt com time
2. Decidir: Opção A (RPC SUM) vs B (campo novo) para valor_estimado_recuperavel
3. Especificar tabela icp_telemetria_snapshots (SDD)

### CURTO PRAZO (próximas 2 semanas)
4. Implementar RPC fn_cliente_valor_recuperavel_total
5. Criar tabela icp_telemetria_snapshots + RLS + índices
6. n8n workflow para popular daily

### MÉDIO PRAZO (próximas 4 semanas)
7. Integração OlivIA para enriquecimento de leads
8. Dashboard ICP Telemetria
9. Validação de integridade de dados

---

## 📝 Como Usar Este Relatório

### Se você é CTO/Tech Lead:
👉 Leia: `ICP_EXEC_SUMMARY.txt` (5 min) + decida próximos passos

### Se você é Dev Backend:
👉 Leia: `icp_schema_audit_20260406.md` (20 min) + implemente tabelas/RPCs

### Se você é DBA/DevOps:
👉 Use: `icp_schema_audit_20260406.json` (validar estrutura) + `icp_schema_audit_20260406.md` (DDL)

### Se você é Dev Frontend/n8n:
👉 Leia: `icp_EXEC_SUMMARY.txt` (entender escopo) + `icp_campos_summary.csv` (campos disponíveis)

### Se você é Analista de Dados:
👉 Use: `icp_schema_audit_20260406.json` (integrar em BI) + `icp_campos_summary.csv` (mapping)

---

## 🔗 Referências

- **Supabase Project:** qdivfairxhdihaqqypgb
- **Org Midas:** 55a0c7ba-1a23-4ae1-b69b-a13811324735
- **User Teste:** 5fe9f43f-6a88-485c-9689-be486f645ba2
- **CLAUDE.md:** /Users/beto/beta-mdflow/CLAUDE.md (regras MdFlow)
- **Docs MdFlow:** ~/beta-mdflow/docs/

---

**Relatório gerado por:** Claude Code (MdFlow DB Auditor)  
**Data:** 2026-04-06 18:14 UTC  
**Validade:** Até próxima auditoria ou schema change
