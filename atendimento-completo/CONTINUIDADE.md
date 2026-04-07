# Atendimento Completo — Documento de Continuidade
> Para retomar o trabalho em outra conversa do Claude Code.
> Criado: 2026-04-06

---

## O que foi feito

### 1. Recebemos 4 audios do Christian
Os audios foram salvos em `audios/` e transcritos. Conteudo:

- **Audio 01** (`01-mdzap-sdr-julia-fluxo.ogg`): SDR Julia no MdZap, auditoria Boa Vista automatica, abas Restricoes/Documentos reutilizaveis entre CRM e MdZap, lead panel fechado por default, edicao completa do lead no panel, docs do WhatsApp salvam automaticamente em leads_documentos.

- **Audio 02** (`02-mdzap-documentos-bugs.ogg`): Drag-and-drop de documentos, docs do lead salvam em aba docs, rename inline de documentos, BUG: valores de restricoes errados na auditoria, BUG: comprovante de restricao nao salva.

- **Audio 03** (`03-documentos-drive-fluxo.ogg`): Google Drive OBRIGATORIO em todos os contextos de documentos. Pastas criadas automaticamente baseado nas restricoes. Docs iniciais vs tramitacao. Conversao automatica de imagens para PDF. Investigar API do Google Drive (service account vs OAuth).

- **Audio 04** (`04-restricoes-fluxo.ogg`): Restricoes diretas no CRM sem auditoria tambem deve ser possivel. Regra Boa Vista: excluir cartorios (nao sao processaveis). Fluxo completo lead→empresa→restricao→processo. Componentes reutilizaveis entre paginas.

### 2. Recebemos 5 HTMLs de referencia do Lovable/projeto
Salvos em `htmls/ref-*.html`:

- **ref-mdzap-lovable-cloud.html**: Sistema de mensagens MdZap antigo (Lovable Cloud). ChatInterface com 2730 linhas, compositor 3 modos, MEDIA_CONFIG, signed URLs, drafts LRU, audio recorder.

- **ref-mdzap-mdflow-atual.html**: MdZap atual no MdFlow. 34 componentes, 14 hooks, 9 webhooks, 8 canais realtime. Layout 3 colunas. Lead panel com 4 abas.

- **ref-docs-restricoes-v1.html**: Docs & Restricoes v1. 3 tiers de documentos, 4 contextos de uso, upload flow, Drive sync, RestricaoPastaCard, Tramitacao.

- **ref-restricoes-docs-completo.html**: Restricoes aprofundado. Modelo de dados completo, ciclo de vida, hooks (useRestricoes vs useClienteRestricoes retornam tipos DIFERENTES), RPCs, drag&drop mapa, sub-tabs Inicial vs Tramitacao, pendencias.

- **ref-fluxo-atendimento-lovable.html**: Fluxo completo de atendimento gerado pelo Lovable. Auditorias → CRM pipeline → empresa matching → distribuicao → processos. Mapa de dependencias entre paginas, tabelas e RPCs envolvidas.

### 3. Geramos 3 documentos de planejamento
Salvos em `htmls/`:

- **framework-v1.html**: Framework atendimento MdZap+CRM v1. 4 fases do fluxo, layout lead panel, componentes shared, pipeline de docs. 8 perguntas pendentes.

- **plano-documentos-restricoes-v1.html**: Plano completo de documentos e restricoes. Estado atual de cada componente/hook, 11 mudancas propostas, fluxogramas, shared components, Drive integration, bugs conhecidos, 5 fases de execucao. 12 perguntas pendentes.

- **framework-atendimento-v2.html**: Framework completo v2 (mais recente). Conecta TODAS as paginas do atendimento: MdZap (3 SDRs) → Auditoria → CRM Pipeline → Distribuicao → Processos. Jornada do lead em 6 etapas detalhadas. Sistema de documentos 3 tiers. Google Drive obrigatorio. 7 componentes shared. 4 bugs a corrigir. 6 fases de execucao. 20 perguntas pendentes (8 framework + 12 docs).

---

## Intencao / Objetivo

O Christian quer **reconstruir o atendimento completo** do escritorio MP Advocacia dentro do MdFlow. Hoje as paginas existem mas nao estao conectadas de forma fluida. O objetivo e:

1. **MdZap como porta de entrada** — SDR Julia (IA) recebe o cliente via WhatsApp, faz auditoria automatica, coleta documentos, qualifica o lead.

2. **CRM como central de gestao** — Pipeline kanban com 5 colunas, drawer universal com abas reutilizaveis.

3. **Distribuicao automatizada** — OlivIA gera peticao, JARBAS protocola no EPROC.

4. **Documentos unificados** — 3 tiers (lead, restricao, processo), tabela unica `processos_documentos`, Google Drive obrigatorio.

5. **Componentes shared** — 7 componentes que funcionam identicamente em MdZap, CRM, Distribuicao, Clientes e Processos.

---

## Regra Critica

**NAO EXECUTAR CODIGO** ate que TODOS os planos estejam aprovados. O Christian quer planejar 100% antes de codar.

---

## Pendencias (o que falta antes de executar)

### Perguntas sem resposta
- [ ] 8 perguntas do framework (Q1-Q8) — ver `framework-atendimento-v2.html` secao 14
- [ ] 12 perguntas de docs/restricoes (D1-D12) — ver `framework-atendimento-v2.html` secao 14

### Audios/informacoes faltando
- [ ] Audio sobre cenarios/fluxograma detalhado do atendimento
- [ ] Audio sobre abas de documentos e restricoes individuais
- [ ] Instrucoes sobre outras paginas alem de CRM/MdZap
- [ ] Teste do MdZap atual pelo Christian (validar o que funciona hoje)

### Investigacoes tecnicas
- [ ] Verificar token Meta WhatsApp no Railway (se esta ativo)
- [ ] Investigar API Google Drive — service account? OAuth? Webhook bidirecional?
- [ ] Verificar schema atual das tabelas no Supabase (restricoes, processos_documentos, etc)
- [ ] Mapear exatamente quais componentes ja existem em shared/ e quais precisam ser extraidos

---

## Como retomar

Para continuar em outra conversa do Claude Code:

```
1. Ler este arquivo: ~/beto-reports/atendimento-completo/CONTINUIDADE.md
2. Ler o INDEX.md: ~/beto-reports/atendimento-completo/INDEX.md
3. Ler o framework mais recente: ~/beto-reports/atendimento-completo/htmls/framework-atendimento-v2.html
4. Se precisar de detalhes sobre docs/restricoes: ~/beto-reports/atendimento-completo/htmls/plano-documentos-restricoes-v1.html
5. Os HTMLs de referencia estao em htmls/ref-*.html para consulta
```

### Contexto tecnico critico para lembrar
- **3 Tiers de documentos**: Tier 1 (lead, restricao_id=null), Tier 2 (restricao, restricao_id=UUID), Tier 3 (processo, gerado)
- **INICIAL_CATS** (9 categorias que NUNCA vao em Tramitacao): peticao_inicial, procuracao_orgao, procuracao, comprovante_restricao, documento_restricao, banco, cartao, documento_lead, negativacao
- **Match fuzzy empresas**: >= 0.75 auto, 0.45-0.74 confirmar, < 0.45 manual. Auto-aprendizado via nome_variacoes.
- **INSERT otimista MdZap**: mensagem aparece imediato (status: pending), n8n faz UPDATE com wa_message_id
- **Webhooks MdZap**: prefix `mdzap/` (NAO `mdflow/`)
- **Lead panel MdZap**: 320px, toggle, FECHADO por default, 4 abas (Dados, Restricoes, Docs, Historico)
- **useRestricoes vs useClienteRestricoes**: retornam tipos DIFERENTES! Cuidado ao unificar.

---

## Estrutura da pasta

```
~/beto-reports/atendimento-completo/
├── INDEX.md                    ← Indice mestre
├── CONTINUIDADE.md             ← ESTE ARQUIVO (para retomar em outra conversa)
├── audios/
│   ├── 01-mdzap-sdr-julia-fluxo.ogg
│   ├── 02-mdzap-documentos-bugs.ogg
│   ├── 03-documentos-drive-fluxo.ogg
│   └── 04-restricoes-fluxo.ogg
├── htmls/
│   ├── framework-v1.html                  ← Framework v1 (superseded by v2)
│   ├── framework-atendimento-v2.html      ← Framework v2 MAIS RECENTE
│   ├── plano-documentos-restricoes-v1.html
│   ├── ref-mdzap-lovable-cloud.html
│   ├── ref-mdzap-mdflow-atual.html
│   ├── ref-docs-restricoes-v1.html
│   ├── ref-restricoes-docs-completo.html
│   └── ref-fluxo-atendimento-lovable.html
└── planos/                     ← Vazio (para planos futuros detalhados)
```
