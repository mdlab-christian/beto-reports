# Schema Audit: ICP Telemetria — Análise de Campos Disponíveis

**Data:** 2026-04-06  
**Escopo:** leads, processos, clientes, icp_reports, mdzap_*  
**Org de teste:** 55a0c7ba-1a23-4ae1-b69b-a13811324735  
**Objetivo:** Mapear campos para implementação de agente ICP Ideal Customer Profile

---

## 1. TABELA LEADS (64 campos)

### Campos de Identidade
- `id` (uuid) — PK
- `organizacao_id` (uuid) — FK, obrigatório
- `nome` (text) — obrigatório
- `email`, `telefone`, `whatsapp`, `cpf` — contato
- `mdzap_contact_id`, `mdzap_conversation_id` — integração WhatsApp

### Campos Demográficos ⭐ (ICP-relevantes)
| Campo | Tipo | Preenchimento | Observação |
|-------|------|---|---|
| `data_nascimento` | DATE | 9% (4/44) | Dados esparsos, apenas 4 leads com data |
| `profissao` | TEXT | 2% (1/44) | Praticamente vazio |
| `endereco_estado` | TEXT | 11% (5/44) | Estado do lead — baixa cobertura |
| `endereco_cidade` | TEXT | ~11% | Mesmo padrão |
| `endereco_cep` | TEXT | ? | Não auditado individualmente |
| `estado_id` | UUID | ? | Foreign key para tabela estados |
| `sexo` | TEXT | ? | Campo demográfico genérico |

### Campos de Valor ⭐ (Relevante para ICP)
| Campo | Tipo | Preenchimento | Observação |
|-------|------|---|---|
| `valor_estimado` | BIGINT | 0% | **SEMPRE NULL** — não há estimativas de valor em leads |
| `icp_score` | SMALLINT | 100% | Score pré-calculado (0-100) — JÁ EXISTE |
| `score` | INTEGER | ? | Score genérico (diferente de icp_score) |

### Campos de Conversão
- `convertido` (boolean) — flag booleana
- `convertido_em` (timestamptz) — quando converteu
- `cliente_id` (uuid) — cliente associado após conversão
- `data_conversao` (timestamptz) — timestamp de conversão

### Campos de Engajamento
- `ultimo_contato` (timestamptz)
- `last_inbound_at`, `last_outbound_at` (timestamptz) — timing de comunicação
- `wa_last_message_at` (timestamptz) — último msg WhatsApp
- `wa_unread_count` (integer) — mensagens não lidas
- `tentativas` (integer) — quantas tentativas de contato

### Campos de Contexto
- `coluna_crm` (text) — estágio no CRM (obrigatório)
- `origem_id` (uuid) — origem do lead (FK)
- `campanha_id` (uuid) — qual campanha trouxe
- `captador_id` (uuid) — quem captou o lead
- `responsavel_id` (uuid) — responsável pelo acompanhamento
- `advogado_id` (uuid) — advogado associado
- `indicacao_id` (uuid) — se foi indicação
- `estado_civil`, `rg` — dados pessoais genéricos

### Campos de Restrição
- `restricoes` (jsonb) — restrições do lead (negativação, etc)
- `motivo_perda` (text) — por que não converteu
- `arquivado` (boolean), `arquivado_motivo_id` (uuid) — archiving

### Campos de IA
- `ai_report` (jsonb) — relatório gerado por IA
- `historico` (jsonb) — histórico de interações

### Campos Estruturais (obrigatórios)
- `created_at`, `updated_at`, `deleted_at` — ✅ Presentes

**DIAGNÓSTICO LEADS:**
- Dados demográficos **MUITO ESPARSOS** (9-11% preenchimento)
- `valor_estimado` **NUNCA preenchido** — usar `icp_score` como proxy
- `icp_score` JÁ EXISTE e está preenchido em 100% dos registros
- Engajamento bem capturado (último contato, mensagens)

---

## 2. TABELA CLIENTES (59 campos)

### Campos de Identidade
- `id`, `organizacao_id`, `nome`, `cpf_cnpj` — PK e identifiers
- `user_id` (uuid) — link para usuário portal (opcional)
- `advbox_id` (integer) — ID no Advbox (integração externa)

### Campos Demográficos ⭐ (ICP-relevantes)
| Campo | Tipo | Preenchimento | Observação |
|-------|------|---|---|
| `data_nascimento` | DATE | 92% (3424/3725) | **EXCELENTE cobertura** |
| `profissao` | TEXT | 45% (1672/3725) | Bom nível de preenchimento |
| `endereco_uf` | TEXT | 52% (1929/3725) | Estado — adequado |
| `endereco_cidade` | TEXT | ~52% | Mesmo padrão |
| `sexo` | TEXT | ? | Preenchimento desconhecido |
| `estado_civil` | TEXT | ? | Preenchimento desconhecido |
| `naturalidade` | TEXT | ? | Naturalidade (UF/país) |
| `nacionalidade` | TEXT | ? | Nacionalidade |
| `renda_mensal` | NUMERIC | 0% | **SEMPRE NULL** — não há renda capturada |
| `banco` | TEXT | ? | Banco para pagamento/depósito |
| `pix` | TEXT | ? | Chave PIX para pagamento |

### Campos de Valor ⭐ (Crítico para ICP)
| Campo | Tipo | Preenchimento | Observação |
|-------|------|---|---|
| `valor_total_estimado_recuperavel` | NUMERIC | 0% | **SEMPRE NULL** — não há valor estimado por cliente |
| `ia_score_portfolio` | SMALLINT | ? | Score IA do portfólio (preenchimento desconhecido) |

### Campos de Prioridade
- `prioridade_legal` (boolean) — é caso prioritário?
- `prioridade_tipo` (text) — qual tipo de prioridade
- `pendencias` (boolean) — tem pendências

### Campos de Engajamento
- `engajamento_nivel` (text) — nível de engajamento
- `ultima_interacao_em` (timestamptz) — última vez que interagiu
- `portal_ativo` (boolean) — cliente tem acesso a portal?

### Campos de Relacionamento
- `lead_id` (uuid) — lead de origem (link para leads)
- `captador_id`, `advogado_responsavel_id`, `atendente_id` — pessoas relacionadas
- `parceiro_advogado_id` (uuid) — advogado parceiro

### Campos de Documentação
- `documentos` (jsonb) — documentos anexados
- `restricoes` (jsonb) — restrições do cliente
- `drive_cliente`, `google_drive_folder_id` (text) — links para pastas
- `historico` (jsonb) — histórico de eventos

### Campos de Contrato
- `contrato_midas_url` (text) — link do contrato
- `contrato_midas_gerado_em` (timestamptz) — quando gerou contrato

### Estruturais
- `created_at`, `updated_at`, `deleted_at` — ✅ Presentes
- `ativo` (boolean) — cliente ativo
- `tipo_documento` (text) — tipo de documento (PF/PJ)

**DIAGNÓSTICO CLIENTES:**
- Dados demográficos **EXCELENTES** (92% data_nascimento, 45% profissao, 52% UF)
- **SEM dados de renda** (`renda_mensal` always NULL)
- **SEM valor estimado recuperável** por cliente — problema P1 para ICP
- `ia_score_portfolio` presente mas preenchimento desconhecido
- Boa rastreabilidade de origem (lead_id, captador_id, origem_id)

---

## 3. TABELA PROCESSOS (134 campos)

### Campos de Identidade
- `id`, `organizacao_id`, `numero_processo`, `numero_cnj` — identificadores
- `cliente_id` (uuid) — cliente do processo
- `advogado_id` (uuid) — advogado responsável
- `empresa_id` (uuid) — empresa envolvida

### Campos de Valor ⭐ (CRÍTICO para ICP)
| Campo | Tipo | Preenchimento | Observação |
|-------|------|---|---|
| `valor_causa` | NUMERIC | 71% (10224/14386) | **BOA cobertura** — principal valor |
| `valor_condenacao` | NUMERIC | 0% | **SEMPRE NULL** |
| `valor_estimado_recuperavel` | NUMERIC | ? | Preenchimento desconhecido |
| `deposito_judicial_valor` | NUMERIC | ? | Valor do depósito |
| `alvara_valor` | NUMERIC | ? | Valor do alvará expedido |
| `restricao_valor`, `restricao_valor_new` | NUMERIC | ? | Valor das restrições |

### Campos de Localização
- `estado_id_new` (uuid) — estado do processo (NEW versão)
- `estado_id` (text) — versão antiga (deprecada?)
- `cidade_distribuicao`, `vara_distribuicao`, `foro_regional` — localização

### Campos de Fase Processual ⭐
| Campo | Tipo | Preenchimento | Observação |
|-------|------|---|---|
| `fase_processual` | TEXT | 93% (13315/14386) | Fase (1º, 2º grau, etc) |
| `etapa_distribuicao` | TEXT | 100% | Estágio na distribuição (obrigatório) |
| `grau` | SMALLINT | ? | Grau de jurisdição |
| `processo_tipo_id`, `tipo_id`, `tipo_processo` | UUID/TEXT | ? | Tipo processual |

### Campos de Decisão
- `ultima_decisao_data` (date) — data da última decisão
- `ultima_decisao_tipo` (text) — tipo (sentença, acórdão, etc)
- `ultima_decisao_resultado` (text) — resultado (procedência, etc)
- `hrefs_decisao` (jsonb) — links para decisões

### Campos de Restrição
- `restricao_tipo`, `restricao_contrato`, `restricao_orgao_nome` — info da restrição
- `restricao_data`, `restricao_data_new` (date) — data da restrição
- `restricao_id` (uuid) — FK para tabela restricoes (se existir)

### Campos de Oportunidade (ICP!)
- `acordo_candidato` (boolean) — é candidato a acordo?
- `acordo_propensao_pct` (smallint) — % propensão acordo
- `chance_sucesso_pct` (smallint) — % chance de sucesso
- `chance_sucesso_ia` (smallint) — chance sucesso via IA

### Campos de Deposito Judicial
- `com_deposito` (boolean) — tem depósito?
- `deposito_judicial_em` (timestamptz) — quando foi depositado
- `deposito_judicial_tipo` (text) — tipo de depósito

### Campos de Alvará
- `alvara_expedido_em` (timestamptz) — quando expediu alvará
- `alvara_numero` (text) — número do alvará

### Campos Estruturais
- `created_at`, `updated_at`, `deleted_at` — ✅ Presentes
- `status` (text) — status do processo (obrigatório)
- `status_id` (uuid) — FK para status
- `ativo` (boolean) — processo ativo?
- `distribuido` (boolean) — foi distribuído?
- `distribuicao_manual` (boolean) — distribuição manual?
- `pendencias` (boolean) — tem pendências?

### Campos de Data-chave
- `data_distribuicao`, `data_cadastro` (date) — quando entrou
- `data_citacao`, `data_contestacao` (date) — marcos processuais
- `transitado_em` (timestamptz) — quando transitou em julgado
- `status_changed_at` (timestamptz) — última mudança de status

### IA e Análise
- `ia_status`, `ia_error`, `ia_versao` (text) — status IA
- `ia_resumo` (jsonb) — resumo gerado por IA
- `ia_resumo_atualizado_em` (timestamptz)
- `analise_status`, `analise_resumo` (text/jsonb) — análise
- `ultima_analise_completa` (timestamptz)

### Integração Externa
- `advbox_id` (integer) — ID Advbox
- `advbox_tipo`, `advbox_fase`, `advbox_grupo` (text) — dados Advbox
- `advbox_parte_cadastrada` (boolean)

**DIAGNÓSTICO PROCESSOS:**
- **`valor_causa` ótimo** (71% preenchimento) — base sólida para ICP
- `fase_processual` excelente (93%) — segmentação
- `acordo_candidato` + `acordo_propensao_pct` — insight de oportunidade
- Sem `valor_condenacao` ou `valor_estimado_recuperável` preenchidos
- IA de análise presente mas integridade desconhecida

---

## 4. TABELA ICP_REPORTS (9 campos) — ✅ JÁ EXISTE

Estrutura:
```sql
id              UUID PRIMARY KEY
organizacao_id  UUID NOT NULL
data_ref        DATE NOT NULL           -- data referência do relatório
periodo_inicio  DATE NOT NULL           -- início do período
periodo_fim     DATE NOT NULL           -- fim do período
payload         JSONB NOT NULL          -- dados agregados do ICP
total_conversoes INTEGER NOT NULL        -- total de conversões no período
source          TEXT                     -- origem dos dados (manual/auto)
created_at      TIMESTAMPTZ NOT NULL   -- quando foi criado
```

**Status:** Tabela existe, **vazia** para org Midas (0 registros).

---

## 5. TABELAS MDZAP (9 tabelas)

- `mdzap_ai_modules` — módulos IA para WhatsApp
- `mdzap_audio_messages` — mensagens áudio
- `mdzap_conversas_timeline` — timeline de conversas
- `mdzap_julia_lab_sessoes` — sessões Julia (IA conversacional)
- `mdzap_julia_prompts` — prompts reutilizáveis
- `mdzap_lead_memory` — memória de leads (contexto conversacional)
- `mdzap_message_queue` — fila de mensagens a enviar
- `mdzap_stage_map` — mapeamento de estágios CRM
- `mdzap_user_map` — mapeamento de usuários

**Relevância ICP:** `mdzap_lead_memory` pode armazenar contexto demográfico extraído via IA.

---

## RESUMO EXECUTIVO: Campos Disponíveis para ICP

### ✅ BASES SÓLIDAS
1. **Data de nascimento (clientes)** → 92% preenchimento → idade é fator ICP
2. **Profissão (clientes)** → 45% preenchimento → tipo de cliente
3. **Estado/UF (clientes)** → 52% preenchimento → segmentação regional
4. **Valor da causa (processos)** → 71% preenchimento → tamanho do caso
5. **Fase processual (processos)** → 93% preenchimento → onde está o caso
6. **ICP_score (leads)** → 100% preenchimento → já pré-calculado
7. **Oportunidade acordo (processos)** → `acordo_candidato` + `acordo_propensao_pct` presente

### ⚠️ GAPS CRÍTICOS (P1)
1. **Sem renda do cliente** (`renda_mensal` always NULL) — fator-chave de ICP
2. **Sem valor estimado recuperável** (clientes/processos) → `valor_estimado_recuperavel` sempre NULL
3. **Dados demográficos em leads** (nascimento, profissão, UF) → 9-11% preenchimento apenas
4. **Banco/PIX (clientes)** → existem campos mas preenchimento desconhecido

### 🔧 RECOMENDAÇÕES

#### Tabela a Criar/Enriquecer: `icp_telemetria_snapshots`
```sql
CREATE TABLE public.icp_telemetria_snapshots (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organizacao_id UUID NOT NULL REFERENCES organizacoes(id),
  data_snapshot DATE NOT NULL,
  lead_id UUID REFERENCES leads(id),
  cliente_id UUID REFERENCES clientes(id),
  processo_id UUID REFERENCES processos(id),
  
  -- Demográfico
  idade_anos SMALLINT,           -- calculado from data_nascimento
  profissao TEXT,
  estado_uf TEXT,
  sexo TEXT,
  estado_civil TEXT,
  
  -- Financeiro
  valor_causa NUMERIC,
  valor_estimado_recuperavel NUMERIC,  -- a calcular
  renda_mensal NUMERIC,                -- a enriquecer
  
  -- Processual
  fase_processual TEXT,
  tempo_dias_caso INTEGER,           -- calculado
  agreement_propensity_pct SMALLINT,
  ia_success_chance_pct SMALLINT,
  
  -- Scoring
  icp_score SMALLINT,
  icp_factors JSONB,    -- {"idade": 8, "valor": 9, "profissao": 7, ...}
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ,
  
  CONSTRAINT fk_org FOREIGN KEY (organizacao_id) REFERENCES organizacoes(id) ON DELETE CASCADE
);

CREATE INDEX idx_icp_snap_org_date ON icp_telemetria_snapshots(organizacao_id, data_snapshot);
CREATE INDEX idx_icp_snap_cliente ON icp_telemetria_snapshots(cliente_id) WHERE deleted_at IS NULL;
```

#### RPC para Calcular ICP Agregado
```sql
CREATE OR REPLACE FUNCTION public.calcular_icp_agregado(
  p_org_id UUID,
  p_periodo_dias INT DEFAULT 90
)
RETURNS TABLE (
  fator TEXT,
  valor_medio NUMERIC,
  count_nao_nulo INTEGER,
  percentual_preenchimento NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 'idade_anos'::TEXT, 
         ROUND(AVG(snp.idade_anos)::NUMERIC, 2),
         COUNT(snp.idade_anos),
         ROUND(COUNT(snp.idade_anos)::NUMERIC / COUNT(*)::NUMERIC * 100, 1)
  FROM icp_telemetria_snapshots snp
  WHERE snp.organizacao_id = p_org_id
    AND snp.data_snapshot >= (CURRENT_DATE - (p_periodo_dias || ' days')::INTERVAL)::DATE
    AND snp.deleted_at IS NULL
  UNION ALL
  SELECT 'valor_causa'::TEXT,
         ROUND(AVG(snp.valor_causa)::NUMERIC, 2),
         COUNT(snp.valor_causa),
         ROUND(COUNT(snp.valor_causa)::NUMERIC / COUNT(*)::NUMERIC * 100, 1)
  FROM icp_telemetria_snapshots snp
  WHERE snp.organizacao_id = p_org_id
    AND snp.data_snapshot >= (CURRENT_DATE - (p_periodo_dias || ' days')::INTERVAL)::DATE
    AND snp.deleted_at IS NULL
  -- ... adicionar outros fatores
  ;
END;
$$ LANGUAGE PLPGSQL SECURITY DEFINER SET search_path = public;
```

---

## CONCLUSÃO

**ICP Telemetria é viável**, mas requer:

1. **Enriquecimento de dados** (renda_mensal, valor_estimado_recuperável)
2. **Snapshot periódico** em tabela dedicada
3. **Cálculo de fatores** agregado por período
4. **Integração com IA** (OlivIA) para extrair profissão/idade/renda de documentos quando faltarem

Próximo passo: especificação formal (SDD) para implementação.

