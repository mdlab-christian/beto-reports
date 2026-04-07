# Atendimento Completo — Central de Planejamento
> Pasta de trabalho para planejar 100% antes de executar.
> Criada: 2026-04-06

## Estrutura

```
atendimento-completo/
├── INDEX.md              ← este arquivo
├── CONTINUIDADE.md       ← documento para retomar em outra conversa
├── audios/               ← audios do Christian (transcritos)
├── htmls/                ← relatorios, frameworks, referencias
└── planos/               ← planos de acao por area
```

## Audios Recebidos

| # | Arquivo | Data | Resumo |
|---|---------|------|--------|
| 01 | `01-mdzap-sdr-julia-fluxo.ogg` | 2026-04-06 | SDR Julia no MdZap: auditoria Boa Vista, abas Restricoes/Documentos reutilizaveis, lead panel fechado por default, edicao completa do lead, docs WA salvam automaticamente |
| 02 | `02-mdzap-documentos-bugs.ogg` | 2026-04-06 | Drag-and-drop, docs do lead salvam em aba docs, rename inline, BUG: valores restricoes errados, BUG: comprovante nao salva |
| 03 | `03-documentos-drive-fluxo.ogg` | 2026-04-06 | Docs obrigatoriamente no Drive, pastas criadas via restricoes, docs iniciais vs tramitacao, conversao PDF automatica, investigar conexao Drive |
| 04 | `04-restricoes-fluxo.ogg` | 2026-04-06 | Restricoes diretas no CRM, regra Boa Vista (excluir cartorios), fluxo empresa, componentes reutilizaveis, fluxograma conexoes |

## HTMLs de Referencia (do Lovable / projeto)

| Arquivo | Origem | Conteudo |
|---------|--------|----------|
| `ref-mdzap-lovable-cloud.html` | Projeto MdZap antigo (Lovable Cloud) | Sistema completo de mensagens: compositor, drag-drop, paste, templates, audio recorder |
| `ref-mdzap-mdflow-atual.html` | Projeto MdFlow atual | 34 componentes, 14 hooks, 9 webhooks, 8 canais realtime, layout 3 colunas |
| `ref-docs-restricoes-v1.html` | Lovable gerado | Docs & Restricoes: 3 tiers, 4 contextos, upload flow, Drive sync, RestricaoPastaCard, Tramitacao |
| `ref-restricoes-docs-completo.html` | Lovable gerado | Restricoes aprofundado: modelo dados, ciclo vida, hooks, RPCs, drag&drop mapa, sub-tabs, pendencias |
| `ref-fluxo-atendimento-lovable.html` | Lovable gerado | Fluxo completo: auditorias, CRM pipeline, empresa matching, distribuicao, processos, mapa dependencias |

## Planos Gerados

| Arquivo | Versao | Conteudo | Perguntas |
|---------|--------|----------|-----------|
| `framework-v1.html` | v1 | Framework atendimento MdZap+CRM — 4 fases fluxo, layout lead panel, componentes shared, pipeline docs | 8 perguntas |
| `plano-documentos-restricoes-v1.html` | v1 | Plano completo docs+restricoes — estado atual, 11 mudancas, fluxogramas, shared components, Drive, bugs, 5 fases execucao | 12 perguntas |
| `framework-atendimento-v2.html` | **v2 (MAIS RECENTE)** | Framework completo: MdZap (3 SDRs) → Auditoria → CRM → Distribuicao → Processos. Jornada 6 etapas, 3 tiers docs, Drive obrigatorio, 7 shared components, 4 bugs, 6 fases execucao | 20 perguntas (8+12) |
| `briefing-christian-v1.html` | **BRIEFING CTO** | Documento para o Christian revisar: tudo que eu entendi, o que ele precisa confirmar, decidir e detalhar. 10 confirmacoes, 15 decisoes, 4 bugs pra detalhar | — |

## Status

**Fase atual:** INVESTIGACAO — coletando requisitos, NAO executando codigo.
**Regra:** So comecamos a codar quando TODOS os planos estiverem 100% aprovados.

### Pendencias
- [ ] Respostas as 8 perguntas do framework (Q1-Q8)
- [ ] Respostas as 12 perguntas de docs/restricoes (D1-D12)
- [ ] Audio sobre cenarios/fluxograma do atendimento completo
- [ ] Audio sobre abas de documentos e restricoes individuais
- [ ] Instrucoes sobre outras paginas alem de CRM/MdZap
- [ ] Teste do MdZap atual pelo Christian
- [ ] Verificar token Meta WhatsApp no Railway
- [ ] Investigar API Google Drive (service account? webhook?)

## Documento de Continuidade

Para retomar em outra conversa: **ler `CONTINUIDADE.md`** — contem tudo que foi feito, o intuito, as pendencias, e como continuar.
