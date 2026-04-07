# Auditoria MdZap Workflows n8n — 2026-04-07

## Resumo Executivo

**Status geral: 🟠 PARCIALMENTE FUNCIONAL**

- **16 workflows ativos** | 5 desligados (inactive)
- **5 workflows com execuções recentes** (últimos 7 dias)
- **11 workflows ativos mas SEM execuções** (webhook nunca foi chamado)
- **Taxa de morte silenciosa: 68.75%** dos workflows ativos (11 de 16)

---

## 1. Workflows que Realmente Funcionam ✅

Apenas **5 de 16** workflows ativos têm execuções documentadas:

| Nome | ID | Último Status | Execuções (últimas 10) | Saúde |
|------|----|----|---|---|
| /MDZAP — Enviar Mensagem FE | 5nZxUubzqoeYInSO | SUCCESS 02:19:47 | 10 ✅ 0 ❌ | ✅ Excelente |
| /MDZAP — Inbound Upsert Lead | A0DEvhxjfzhJmGbU | SUCCESS 02:17:19 | 4 ✅ 0 ❌ | ✅ Funcional |
| /MDZAP — AI Composer | 2iVpyvXO2Q2kCzOi | SUCCESS 01:58:24 | 7 ✅ 3 ❌ | 🟡 70% sucesso |
| /MDZAP — Julia Prompt Save | 6jgyFxNBWVrkI132 | SUCCESS 01:59:20 | 1 ✅ 2 ❌ | 🔴 33% sucesso |
| /MDZAP — Julia Lab Refine | 66qcFi6VlruMrHRA | ERROR 20:00:46 | 0 ✅ 1 ❌ | 🔴 Quebrado |

### Detalhes dos Funcionais

**✅ /MDZAP — Enviar Mensagem FE** (5nZxUubzqoeYInSO)
- Webhook: `POST /webhook/mdzap/enviar-mensagem`
- Taxa de sucesso: 100% (10/10)
- Última execução: 2026-04-07 02:19:47 UTC
- **Conclusão**: Apenas este está verdadeiramente confiável

**✅ /MDZAP — Inbound Upsert Lead** (A0DEvhxjfzhJmGbU)
- Webhook: `POST /webhook/mdzap/inbound-upsert-lead`
- Taxa de sucesso: 100% (4/4)
- Última execução: 2026-04-07 02:17:19 UTC
- **Conclusão**: Novo, poucos dados, mas promissor

**🟡 /MDZAP — AI Composer** (2iVpyvXO2Q2kCzOi)
- Webhook: `POST /webhook/mdzap/ai-composer`
- Taxa de sucesso: 70% (7/10)
- Últimas falhas: 3 errors não investigados
- **Conclusão**: Instável. Investigar causa de failures

**🔴 /MDZAP — Julia Prompt Save** (6jgyFxNBWVrkI132)
- Webhook: `POST /webhook/mdzap/julia-prompt-save`
- Taxa de sucesso: 33% (1/3)
- **Conclusão**: Quebrado. Requer debugação

**🔴 /MDZAP — Julia Lab Refine** (66qcFi6VlruMrHRA)
- Webhook: `POST /webhook/mdzap/julia-lab-refine`
- Taxa de sucesso: 0% (0/1)
- Erro: 2026-04-06 20:00:46 UTC
- **Conclusão**: Nunca funcionou após última mudança (2026-04-06 20:00:15)

---

## 2. Workflows Mortos Silenciosamente ⚠️

**11 workflows ativos mas NUNCA foram executados** = webhook não está sendo chamado de lugar algum

| Nome | ID | Webhook | Última Mudança | Diagnóstico |
|------|----|----|---|---|
| /MDZAP — Lead Sync | 38t0RwznvYRKqdJB | `mdzap/lead-sync` | 2026-04-06 17:14:34 | Ativo mas não integrado |
| /MDZAP — Encerrar Conversa | 6ht8s7FVDKEnLLPz | `mdzap/encerrar-conversa` | 2026-04-06 17:14:29 | Ativo mas não integrado |
| /MDZAP — Transferir Conversa | Af4O6x0EDJu8n5Qq | `mdzap/transferir-conversa` | 2026-04-06 17:14:27 | Ativo mas não integrado |
| MDZAP-SEND-TEST | A6S18du3FDCOy4yY | `mdzap-send` | 2026-03-19 10:20:07 | Teste morto (antigo) |
| [Gu] MdZap - Teste | 9XYj1e4g139fwBiW | UUID custom | 2026-04-06 20:22:06 | Teste de Gustavo |
| /MDZAP — Enviar Template | 2DxMd7m0d2GMASFg | `mdzap/enviar-template` | 2026-04-06 17:14:22 | Não integrado |
| WH-CRM-08 — MDZap Stage Change | 803vWxLuqM8r6jAB | `mdflow/mdzap/stage-change` | 2026-03-06 22:09:06 | Antigo (desligado de facto) |
| /MDZAP — Stage Changed | 6juwlcSdlkOcDOAB | `mdflow/mdzap/event-stage-changed` | 2026-04-06 17:14:36 | Não integrado |
| /MDZAP — Document Received | 7BvjpfcStEG2z27V | `mdzap/document-received` | 2026-04-07 03:09:16 | Novo, não chamado |
| /MDZAP — Julia Lab | 4T5QQjKetCoXI6rR | `mdzap/julia-lab` | 2026-04-06 17:14:47 | Não integrado |
| /MDZAP — Triagem | AbdytxeYO6mMQKGw | `mdflow/mdzap/triagem` | 2026-04-06 17:14:38 | Não integrado |

### O que está Acontecendo?

Estes workflows foram **criados e deixados ativos**, mas **ninguém está chamando os webhooks deles**. Possíveis causas:

1. **Frontend não implementou as chamadas** — páginas do MdZap não estão disparando estes webhooks
2. **URLs de webhook diferentes na integração** — frontend pode estar chamando `/webhook/outro-path/`
3. **Workflows prototipados e nunca completados** — pendências de integração do Gustavo/Matheus
4. **Mudança de arquitetura** — webhooks foram substituídos por outros (eg: talvez usar apenas os 2 que funcionam)

---

## 3. Workflows Desligados ❌

5 workflows foram explicitamente desligados (inactive = false):

| Nome | ID | Desligado Desde | Razão Provável |
|------|----|----|---|
| [GUSTAVO] MDZAP-TRIAGEM-CRM | 5SsWckbHAqILF1Cd | 2026-03-05 18:06:59 | Substituído por versão nova |
| [GUSTAVO] MDZAP-SYNC | 6Vjckjh5o55R7u1I | 2026-03-05 18:04:44 | Substituído ou descontinuado |
| MDZAP-JULIA-LAB | 1xuljfmQLAFVjHm6 | 2026-03-20 22:38:33 | Substituído por v2 (no ar) |
| [MATHEUS] 08b_MDZAP-SYNC-IN | 1B3LQbmsvJEUU5K-nDc-p | 2026-02-25 20:09:16 | Arquitetura antiga |
| [MATHEUS] 08a_MDZAP-SYNC-OUT | 8yKy19ZqlLFSELOUaENKL | 2026-02-25 20:09:01 | Arquitetura antiga |

---

## 4. Análise dos 2 IDs que Você Pediu

### ID A0DEvhxjfzhJmGbU (/MDZAP — Inbound Upsert Lead)
```
✅ Status: FUNCIONANDO
Ativo: SIM
Webhook: POST /webhook/mdzap/inbound-upsert-lead
Últimas 4 execuções: SUCESSO (100%)
  SUCCESS — 2026-04-07 02:17:19
  SUCCESS — 2026-04-07 02:16:53
  SUCCESS — 2026-04-07 02:15:45
  SUCCESS — 2026-04-07 02:14:33
```
**Conclusão**: Este está bem. Sendo chamado recentemente e sem erros.

### ID 38t0RwznvYRKqdJB (/MDZAP — Lead Sync)
```
⚠️  Status: MORTO (webhook nunca foi chamado)
Ativo: SIM
Webhook: POST /webhook/mdzap/lead-sync
Última mudança: 2026-04-06 17:14:34
Execuções: ZERO
```
**Conclusão**: Ativo mas não está sendo usado. Ou:
1. Frontend não implementou a chamada
2. O webhook foi prototipado e abandonado
3. Funcionalidade foi integrada de outro jeito

---

## 5. Webhook Path Inconsistências

Há **dois padrões de webhook paths**:

**Padrão A** (novo, minúsculas com hífen):
- `mdzap/enviar-mensagem`
- `mdzap/inbound-upsert-lead`
- `mdzap/lead-sync`
- `mdzap/ai-composer`

**Padrão B** (antigo, com prefixo mdflow):
- `mdflow/mdzap/stage-change`
- `mdflow/mdzap/event-stage-changed`
- `mdflow/mdzap/triagem`

**Padrão C** (teste):
- `aa30b664-1bd1-4867-aaa2-b72da6d40e63` (UUID, workflow de teste)
- `mdzap-send` (sem hífen)

**Recomendação**: Padronizar em `mdzap/[acao]` (Padrão A). Remover Padrão B.

---

## 6. Erros Identificados

### Julia Lab Refine (66qcFi6VlruMrHRA)
- Status: ERROR em 2026-04-06 20:00:46 UTC
- Última mudança: 2026-04-06 20:00:15 UTC
- **Problema**: Falha logo após última modificação — bug introduzido no último update
- **Ação**: Inspecionar nós do workflow, verificar o que mudou

### Julia Prompt Save (6jgyFxNBWVrkI132)
- Histórico: 1 SUCCESS, 2 ERRORS
- Taxa: 33% sucesso
- **Problema**: Intermitente, talvez timeout ou validação fraca
- **Ação**: Debugar, aumentar timeout, adicionar retry logic

### AI Composer (2iVpyvXO2Q2kCzOi)
- Taxa: 70% sucesso (7/10, 3 errors)
- **Problema**: Integração com IA instável
- **Ação**: Verificar rate limits, tratamento de erros da IA, retry

---

## 7. Recomendações de Ação

### P1 — Imediato (hoje)
1. **Desligar os 11 workflows mortos** — remover ruído visual em n8n
   - Manter apenas os 5 que funcionam + os 5 desligados existentes
   - Ou integrar os webhooks no frontend para começar a usar

2. **Debugar Julia Lab Refine** — erro recente é crítico
   - Reverter para versão anterior ou inspecionar nós

3. **Verificar se frontend está chamando os webhooks**
   - Usar Chrome DevTools em /mdzap → Network tab
   - Confirmar se está chamando `POST /webhook/mdzap/enviar-mensagem` ou outros

### P2 — Esta semana
1. **Consolidar workflows Julia**
   - Temos `Julia Lab`, `Julia Lab Refine`, `Julia Prompt Save`
   - Determinar qual é a versão de produção
   - Desligar duplicatas

2. **Padronizar webhook paths**
   - Migrar Padrão B → Padrão A
   - Remover testes (`MDZAP-SEND-TEST`, etc)

3. **Investigar Stage Change workflows**
   - `WH-CRM-08` (morto desde 2026-03-06)
   - `Stage Changed` (novo, não chamado)
   - São complementares? Qual usar?

### P3 — Próximas sprints
1. **Documentar qual workflow faz o quê**
   - Spec dos webhooks com payload esperado
   - Qual página chama qual webhook

2. **Implementar monitoring**
   - Alertas para workflows com >50% error rate
   - Alertas para workflows com 0 execuções por 24h (muito ativo)

3. **Clean up geral**
   - Deletar workflows antigos (Matheus, Gustavo v1)
   - Revisar nomenclatura (remover [USER] prefixes)

---

## 8. Webhook Health Status

| Categoria | Workflows | Status |
|-----------|-----------|--------|
| ✅ Saudáveis (sucesso 100%) | 2 | `enviar-mensagem`, `inbound-upsert-lead` |
| 🟡 Instáveis (sucesso 30-90%) | 2 | `ai-composer`, `julia-prompt-save` |
| 🔴 Quebrados (sucesso <30%) | 1 | `julia-lab-refine` |
| ⚠️  Mortos (0 execuções) | 11 | Lead Sync, Encerrar, Transferir, Enviar Template, etc |
| ❌ Desligados | 5 | Gustavo v1, Matheus v1, etc |

**Score geral: 1/16 workflows verdadeiramente confiável (Enviar Mensagem FE)**

---

## Conclusão

MdZap tem **apenas 1 workflow totalmente confiável**. Os outros estão em um destes estados:

1. **Funcionando com 100% sucesso** (2): Enviar Mensagem FE, Inbound Upsert Lead
2. **Funcionando com erros** (2): AI Composer, Julia Prompt Save
3. **Quebrado** (1): Julia Lab Refine
4. **Morto silenciosamente** (11): Ativo mas nunca chamado
5. **Desligado** (5): Removido intencionalmente

**Antes de ligar recursos novos em MdZap, limpar esta bagunça:**
- Desligar os 11 mortos
- Fixar os 3 quebrados/instáveis
- Documentar o que cada um faz
- Confirmar integração no frontend

---

*Auditoria completa usando n8n API helper. Relatório honesto sem sugar coating.*
*2026-04-07 02:30 UTC — Beto / Claude Code*
