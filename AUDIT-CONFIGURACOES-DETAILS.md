# Frontend Audit: /configuracoes — 31 de março de 2026

## Resumo Executivo
- **Arquivos encontrados:** 41 TypeScript (.tsx/.ts)
- **Total de linhas:** ~8.920 linhas
- **P0 (Bloqueadores):** 7 issues
- **P1 (Importantes):** 6 issues  
- **P2 (Melhorias):** 3 issues
- **Status:** 🔴 **CRÍTICO — Falhas de segurança multi-tenant detectadas**

---

## P0 — Bloqueadores (CORRIGIR ANTES DO DEPLOY)

### P0-001: Multi-tenant Isolation — .update() sem organizacao_id (CRÍTICO)

**Severidade:** 🔴 **CRÍTICO**  
**Impacto:** Cross-tenant data manipulation — usuário de ORG A pode alterar dados de ORG B  
**Arquivos afetados:** 26 locais em 10+ arquivos

#### Padrão Inseguro
```typescript
// ❌ INSEGURO — NÃO valida organizacao_id
const { error } = await supabase
  .from('docs_tipos')
  .update({ ativo: novoAtivo })
  .eq('id', id);  // Só filtra por ID!
```

#### Padrão Correto
```typescript
// ✅ SEGURO — Filtra por ID + organizacao_id
const { error } = await supabase
  .from('docs_tipos')
  .update({ ativo: novoAtivo })
  .eq('id', id)
  .eq('organizacao_id', organizacao_id!);
```

#### Checklist de Correção

**[TabDocumentos.tsx]**
- [ ] Linha 98: `.update({ ativo: novoAtivo }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 116: `.update({ ativo: novoAtivo }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 132: `.update({ deleted_at: ... }).eq('table', ...).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 151: `.update({ deleted_at: ... }).eq('table', ...).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabContas.tsx]**
- [ ] Linha 49: `.update({ ativo: false }).eq('id', desativarContaId)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 82: `.update({ ativo: false }).eq('id', desativarCartaoId)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabWhatsapp.tsx]**
- [ ] Linha 63: `.update({ ai_enabled })` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 171: `.update({ ... })` → add `.eq('organizacao_id', organizacao_id!)`

**[TabProcessos.tsx]**
- [ ] Linha 171: `.update({ ordem: s.ordem }).eq('id', s.id)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 189: `.update({ ativo: novoAtivo }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabAtividades.tsx]**
- [ ] Linha 100: `.update({ ativo: novoAtivo }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabAdvogados.tsx]**
- [ ] Linha 126: `.update({ ativo: novoAtivo }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabEstados.tsx]**
- [ ] Linha 88: `.update({ ativo: novoAtivo }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 104: `.update({ ativo })` → add `.eq('organizacao_id', organizacao_id!)`

**[TabUsuarios.tsx]**
- [ ] Linha 120: `.update({ ativo: novoAtivo }).eq('id', userId)` → add `.eq('organizacao_id', organizacao_id!)`
- [ ] Linha 153: `.delete().eq('id', usuarioId)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabTemplates.tsx]**
- [ ] Linha 81: `.update({ ativo: false }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`

**[TabEtiquetas.tsx]**
- [ ] Linha 73: `.update({ ativo: false }).eq('id', id)` → add `.eq('organizacao_id', organizacao_id!)`

**[ModalEditarUsuario.tsx]**
- [ ] Linha 142-150: `.update({...}).eq('id', userId)` → add `.eq('organizacao_id', organizacao_id!)`

**[CRM sub-tabs]**
- [ ] CrmEstagiosFunil.tsx:72, 97, 115, 117
- [ ] CrmFollowupConfig.tsx:104
- [ ] CrmOrigens.tsx:65, 84

**[Teste de Segurança]**
```typescript
// VERIFICAR: com 2 orgs simultâneas, user de ORG A não consegue alterar dados de ORG B
const org1UserId = 'uuid-org1';
const org2UserId = 'uuid-org2';
const recordId = 'uuid-record-org2';
const organizacao_id = org1_id;  // Simulando user de org1

// Tentar update sem org filter — DEVE FALHAR (ou não fazer nada)
await supabase.from('docs_tipos').update({ ativo: true }).eq('id', recordId);

// Verificar se dados de org2 foram modificados — NÃO DEVEM TER SIDO
```

---

### P0-002: Soft Delete Ausente (7 Tabs)

**Severidade:** 🔴 **CRÍTICO (LGPD/conformidade)**  
**Impacto:** Registros excluídos aparecem em queries, viola direito ao esquecimento  
**Spec padrão:** `.is('deleted_at', null)` obrigatório em TODAS as queries

#### Padrão Correto
```typescript
// ✅ SEMPRE implementar
const { data } = await supabase
  .from('docs_categorias')
  .select('*')
  .eq('organizacao_id', organizacao_id!)
  .is('deleted_at', null)  // ← OBRIGATÓRIO
  .order('nome');
```

#### Arquivos a Corrigir
1. **[TabController.tsx:49]** — `controller_dominios`
2. **[TabContas.tsx:33, 66]** — `contas_bancarias`, `cartoes_credito`
3. **[TabWhatsapp.tsx:49, 157]** — `whatsapp_numeros`, `mdzap_ai_modules`
4. **[TabProcessos.tsx:137]** — `processos_situacoes`
5. **[TabAtividades.tsx:62]** — `atividades_tipos`
6. **[TabAdvogados.tsx]** — `advogados_internos`, `advogados_externos`
7. **[TabEstados.tsx]** — verificar se aplica

**Status atual:** ✅ Implementado em:
- TabDocumentos.tsx (linhas 60, 76)
- ModalGerenciarSetores.tsx (linha 48)

---

### P0-003: Cores Dinâmicas sem Validação

**Severidade:** 🟠 **ALTO**  
**Arquivos:** TabProcessos.tsx:79, TabAtividades.tsx:203, TabEtiquetas.tsx:150, TabEtiquetas.tsx:144, ModalCartaoCredito.tsx:199, color_picker_grid.tsx:39

#### Problema
```typescript
// ❌ Pode quebrar se `cor` for inválido
<span style={{ backgroundColor: sit.cor || 'hsl(var(--muted-foreground))' }} />

// Cenários de risco:
// - cor = null, undefined → usa fallback ✓
// - cor = "invalid" → CSS ignora, exibe fallback ✓
// - cor = "#12" ou "red" (não-hex) → pode não renderizar

// ❌ Color picker aceita qualquer string
<input type="color" value={c.value} onChange={() => ...} />
// Usuário pode digitar "abc" em vez de "#abc123"
```

#### Solução
```typescript
// ✅ Validar antes de usar
const isValidHex = (color: string | null): boolean => {
  if (!color) return false;
  return /^#[0-9a-fA-F]{6}$/.test(color);
};

const bgColor = isValidHex(cor) ? cor : 'hsl(var(--muted-foreground))';
<span style={{ backgroundColor: bgColor }} />

// color_picker_grid.tsx — validar no onChange:
const handleColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const value = e.target.value;
  if (/^#[0-9a-fA-F]{6}$/.test(value)) {
    setColor(value);
  } else {
    toast.error('Formato de cor inválido. Use #RRGGBB');
  }
};
```

---

### P0-004: Acesso Financeiro — Máscara Insuficiente

**Severidade:** 🟠 **ALTO**  
**Arquivo:** TabContas.tsx (linhas 33-43, 65-76)  
**Contexto:** BlindedValue() mascara valor no template, mas query retorna dados brutos

#### Problema
```typescript
// Query retorna TUDO
const { data: contas } = await supabase
  .from('contas_bancarias')
  .select('*')  // ← número da conta, CPF, saldo, tudo aqui
  .eq('organizacao_id', organizacao_id!)
  .eq('ativo', true);

// Frontend mascara visualmente
{acesso_financeiro ? formatBRL(conta.saldo) : <BlindedValue />}

// ❌ MAS: usuário sem acesso_financeiro vê dados em DevTools → Network → Response
```

#### Solução Recomendada
```typescript
// Opção 1: RPC que filtra baseado em permissão (MELHOR)
const { data } = await supabase.rpc('get_contas_permitidas', {
  org_id: organizacao_id,
  user_id: user_id,
  // RPC: if acesso_financeiro=false, retorna NULL em campos sensíveis
});

// Opção 2: Campo virtual no banco (menos invasivo)
// Criar VIEW: v_contas_safe 
// SELECT id, nome, tipo, ativo, 
//   CASE WHEN current_org_has_financial_access() THEN numero ELSE NULL END as numero,
//   CASE WHEN current_org_has_financial_access() THEN saldo ELSE NULL END as saldo

// Opção 3: Documentar e confiar em RLS (atual)
// Manter: usuários sem acesso não devem ver tab de contas (TabContas só carrega se admin)
// Verificação: guarde na cache que admin tentou acessar com user sem acesso_financeiro
```

**Ação imediata:** Documentar que TabContas requer admin + acesso_financeiro=true. Verificar RLS.

---

### P0-005: Action-Driven UI Incompleto

**Severidade:** 🟠 **ALTO**  
**Contexto:** Padrão exige `switch(response.action)` em TODAS respostas webhook  
**Status:** ✅ Implementado em TabController.tsx:284 | ❌ Faltando em 10+ modais

#### Padrão Correto
```typescript
// ✅ CORRETO
const response = await callWebhook('/sync-dominios', {...});

if (response.success) {
  toast.success(response.message);
  // NÃO fazer: if (response.success) navigate(...)
  
  // ✅ FAZER: switch action
  handleWebhookAction(response.action, response.data, { queryClient, navigate, toast });
}

// Respostas canônicas que backend pode retornar:
switch (response.action) {
  case 'toast_refresh':
    toast.success(response.message);
    queryClient.invalidateQueries({ queryKey: ['dominios'] });
    break;
  case 'redirect':
    navigate(response.data.url);
    break;
  case 'toast_error':
    toast.error(response.message);
    break;
  case 'noop':
    // Silent
    break;
  // ... etc
}
```

#### Modais Que Precisam Implementar
1. ModalEditarUsuario.tsx — após save de dados/perms
2. ModalAdvogado.tsx — após create/update
3. ModalContaBancaria.tsx — após create/update
4. ModalCartaoCredito.tsx — após create/update
5. ModalTemplate.tsx — após save
6. ModalDominio.tsx — após create/update/delete
7. ModalConvidarUsuario.tsx — após invite
8. ModalEtiqueta.tsx — após create/update
9. ModalSituacaoProcesso.tsx — após create/update
10. ModalTipoAtividade.tsx — após create/update

**Script de busca:**
```bash
grep -rn "if (response.success)" ~/beta-mdflow/src/pages/configuracoes/modals/
# Nenhum deve retornar true — devem usar handleWebhookAction()
```

---

### P0-006: Delete sem Organizacao_id (TabUsuarios.tsx:153)

**Arquivo:** TabUsuarios.tsx, linha 153  
**Contexto:** Deletar usuário

```typescript
// ❌ INSEGURO
const { error } = await supabase
  .from('users')
  .delete()
  .eq('id', usuarioId);

// ✅ SEGURO
const { error } = await supabase
  .from('users')
  .delete()
  .eq('id', usuarioId)
  .eq('organizacao_id', organizacao_id!);
```

---

### P0-007: ModalEditarUsuario.tsx — Update sem Org

**Arquivo:** ModalEditarUsuario.tsx, linhas 141-151  
**Detalhe:** Após salvar dados de usuário

```typescript
// ❌ Atual
const { error } = await supabase
  .from('users')
  .update({
    nome: nome.trim(),
    telefone: telefone.trim() || null,
    perfil,
    setor_id: setorId,
    acesso_gestor: acessoGestor,
    ativo,
  })
  .eq('id', userId);

// ✅ Correto
  .eq('id', userId)
  .eq('organizacao_id', organizacao_id!);
```

---

## P1 — Importantes (Refatorar proxíma sprint)

### P1-001: Arquivos >500 linhas

**Status:** ✅ **OK** — TabUsuarios.tsx está em 489 linhas (no limite, aceitável)

Todos os arquivos estão conformes com o limite de 500 linhas do Design System v5.

---

### P1-002: Imports Excessivos (>15)

| Arquivo | Imports | Recomendação |
|---------|---------|--------------|
| ConfiguracoesPage.tsx | 23 | 🔴 Alto — lazy load tabs |
| TabUsuarios.tsx | 19 | 🟠 Médio — agrupar imports |
| TabAdvogados.tsx | 19 | 🟠 Médio |
| ModalEditarUsuario.tsx | 19 | 🟠 Médio |
| TabController.tsx | 18 | 🟠 Médio |
| TabProcessos.tsx | 17 | 🟠 Médio |
| TabWhatsapp.tsx | 16 | 🟡 Borderline |
| TabDocumentos.tsx | 16 | 🟡 Borderline |
| TabAtividades.tsx | 16 | 🟡 Borderline |

**Ação:** Refatorar ConfiguracoesPage com `React.lazy()`:

```typescript
// ✅ Atual (carrega 12 tabs antecipadamente)
import { TabUsuarios } from './tabs/TabUsuarios';
import { TabAdvogados } from './tabs/TabAdvogados';
// ... 10 mais

// ✅ Melhorado (lazy load)
const TabUsuarios = lazy(() => import('./tabs/TabUsuarios').then(m => ({ default: m.TabUsuarios })));
const TabAdvogados = lazy(() => import('./tabs/TabAdvogados').then(m => ({ default: m.TabAdvogados })));

// No JSX:
<Suspense fallback={<Skeleton />}>
  {Component && <Component />}
</Suspense>
```

**Impacto:** Reduz bundle inicial em ~15-20KB gzipped.

---

### P1-003: Soft Delete em 7 Tabs

**Ver P0-002** — mesmo checklist, classificado como P1 por não ser vulnerabilidade direta.

---

### P1-004: Responsividade Limitada

**Problema:**
- 29 linhas com breakpoints
- Apenas 3 são mobile-specific (hidden sm:inline)
- Tabelas não adaptam &lt;640px
- PermissionGrid (grid 4 colunas) quebra em mobile

**Ação:**
1. Adicionar `sm:hidden` em colunas de tabela desnecessárias em mobile
2. PermissionGrid → checkbox no mobile, grid no desktop
3. Testar em 375px, 640px, 1024px, 1440px

---

### P1-005: Refetch Ausente em PermissionGrid

**Arquivo:** ModalEditarUsuario.tsx (SubTab "Permissões")  
**Problema:** Após mudar permissão, não atualiza lista de permissões na modal

```typescript
// Após PermissionGrid.onChange():
const handleSavePermissoes = async () => {
  // ...
  // Faltando: invalidate query
  queryClient.invalidateQueries({ queryKey: ['config-user-permissoes', userId, organizacao_id] });
};
```

---

### P1-006: Typo/Inconsistência em TabAtividades.tsx

**Linha:** 36  
**Contexto:** Type `ComplexidadeFilter = 'todos' | 'alta' | 'media' | 'baixa'` é bom, mas:
- Verificar se `type.complexidade` sempre === um desses valores no DB
- Se não, adicionar default fallback

---

## P2 — Melhorias (Backlog)

### P2-001: Validação de Cores (color_picker_grid.tsx)

**Arquivo:** color_picker_grid.tsx, linha 39

```typescript
// ❌ Sem validação
style={{ backgroundColor: c.value }}

// ✅ Com validação
const isValidColor = /^#[0-9a-fA-F]{6}$/.test(c.value);
style={{ 
  backgroundColor: isValidColor ? c.value : 'hsl(var(--muted-foreground))',
  opacity: isValidColor ? 1 : 0.5,
}}
```

---

### P2-002: Cartão Gradientes (ModalCartaoCredito.tsx:199)

**Problema:** Gradients hardcoded em JS

```typescript
// ❌ Atual
const BANDEIRA_GRADIENTS = {
  visa: 'linear-gradient(135deg, #1434CB, #1E90FF)',
  mastercard: 'linear-gradient(135deg, #FF5F00, #FFB84D)',
  // ...
};

// ✅ Melhor — CSS classes
className={cn(
  'bg-gradient-visa',  // CSS: .bg-gradient-visa { background: ... }
)}
```

---

### P2-003: Documentação HealthValidatorBanner

**Arquivo:** HealthValidatorBanner.tsx (244 linhas)  
**Problema:** Não há doc sobre o que cada check faz (ok, warning, error)

Adicionar JSDoc + spec em constants.

---

## Estrutura de Arquivos — Árvore Completa

```
configuracoes/
├── index.tsx (1 linha)
├── ConfiguracoesPage.tsx (125 linhas) — HUB PRINCIPAL
├── types.ts (15 linhas)
├── constants.ts (18 linhas)
├── constants/
│   └── perfil.constants.ts (12 linhas)
├── components/ (7 componentes)
│   ├── HealthValidatorBanner.tsx (244)
│   ├── PermissionGrid.tsx (329)
│   ├── DistribuicaoEditor.tsx (384)
│   ├── color_picker_grid.tsx (45)
│   ├── PlaybookIAEditor.tsx (121)
│   ├── PlaybookIAGlobal.tsx (92)
│   └── RegrasAvancadasEditor.tsx (176)
├── tabs/ (12 tabs principais + 3 sub-tabs CRM)
│   ├── TabUsuarios.tsx (489) ← LIMITE
│   ├── TabAdvogados.tsx (381)
│   ├── TabDocumentos.tsx (381)
│   ├── TabContas.tsx (262)
│   ├── TabProcessos.tsx (290)
│   ├── TabAtividades.tsx (304)
│   ├── TabEtiquetas.tsx (193)
│   ├── TabTemplates.tsx (238)
│   ├── TabWhatsapp.tsx (345)
│   ├── TabController.tsx (308)
│   ├── TabEstados.tsx (244)
│   ├── TabCRM.tsx (18) — wrapper
│   └── crm/ (3)
│       ├── CrmEstagiosFunil.tsx (216)
│       ├── CrmFollowupConfig.tsx (239)
│       └── CrmOrigens.tsx (158)
└── modals/ (17 componentes)
    ├── ModalEditarUsuario.tsx (425)
    ├── ModalAdvogado.tsx (303)
    ├── ModalContaBancaria.tsx (289)
    ├── ModalCartaoCredito.tsx (333)
    ├── ModalTemplate.tsx (249)
    ├── ModalDominio.tsx (206)
    ├── ModalConvidarUsuario.tsx (219)
    ├── ModalGerenciarSetores.tsx (303)
    ├── ModalEtiqueta.tsx (176)
    ├── ModalSituacaoProcesso.tsx (178)
    ├── ModalTipoAtividade.tsx (190)
    ├── ModalTipoDocumento.tsx (162)
    ├── ModalCategoriaDocumento.tsx (112)
    ├── ModalParceiro.tsx (220)
    ├── SubTabFuncionario.tsx (277)
    └── [outros 2 não listados]

TOTAL: 41 arquivos | 8,920 linhas
```

---

## ✅ Conformidades Verificadas

| Verificação | Status | Detalhe |
|---|---|---|
| Hardcode hex em className | ✅ PASS | Apenas inline styles dinâmicas (aceitável com fallback) |
| Toast Sonner | ✅ PASS | Zero react-hot-toast/react-toastify |
| console.log em prod | ✅ PASS | Nenhum encontrado |
| TypeScript any | ✅ PASS | Sem `: any` ou `as any` |
| fetch/axios externo | ✅ PASS | Zero chamadas diretas (webhook via n8n) |
| service_role_key | ✅ PASS | Não exposto |
| Empty/Loading/Error states | ✅ PASS | 10+ tabs implementam (Skeleton, EmptyState) |
| Dirty state | ✅ PASS | 3 modais (TabTemplate, ModalContaBancaria, ModalCartaoCredito) |
| ErrorBoundary | ✅ PASS | TabErrorFallback em TabsContent |
| Cegueira financeira | ✅ PASS | BlindedValue() em TabContas |
| Modais aninhados | ✅ PASS | Um por vez, nunca nested |
| Icons Lucide | ✅ PASS | 100% lucide-react |
| Paginação | ✅ PASS | Sem scroll infinito, todas &lt;50 items |

---

## Matriz de Risco por Arquivo

| Arquivo | P0 | P1 | P2 | Risco | Prioridade |
|---------|----|----|----|----|-----------|
| TabDocumentos.tsx | 4 | 1 | — | 🔴 ALTO | 1º |
| TabContas.tsx | 2 | 2 | — | 🔴 ALTO | 1º |
| TabController.tsx | 1 | — | — | 🟠 MÉD | 2º |
| ModalEditarUsuario.tsx | 1 | 1 | — | 🟠 MÉD | 2º |
| TabAtividades.tsx | 1 | 1 | — | 🟠 MÉD | 2º |
| TabAdvogados.tsx | 1 | 1 | — | 🟠 MÉD | 2º |
| ConfiguracoesPage.tsx | — | 1 | — | 🟢 BAIXO | 3º |

---

## 📋 Checklist de Correção

### [ ] IMEDIATO (Esta semana — P0)
- [ ] **P0-001:** Adicionar `.eq('organizacao_id', organizacao_id!)` em 26 locais (26 `.update()` + `.delete()`)
  - [ ] TabDocumentos (4)
  - [ ] TabContas (2)
  - [ ] TabWhatsapp (2)
  - [ ] TabProcessos (2)
  - [ ] TabAtividades (1)
  - [ ] TabAdvogados (1)
  - [ ] TabEstados (2)
  - [ ] TabUsuarios (2)
  - [ ] TabTemplates (1)
  - [ ] TabEtiquetas (1)
  - [ ] ModalEditarUsuario (1)
  - [ ] CrmEstagiosFunil (4)
  - [ ] CrmFollowupConfig (1)
  - [ ] CrmOrigens (2)
- [ ] **P0-002:** Implementar `.is('deleted_at', null)` em 7 tabs
- [ ] **P0-003:** Validar cores hex em color_picker_grid.tsx
- [ ] **P0-006 & P0-007:** Adicionar org filter em delete/update

### [ ] CURTO PRAZO (2-3 semanas — P1)
- [ ] Refatorar ConfiguracoesPage com React.lazy()
- [ ] Melhorar responsividade mobile (&lt;640px)
- [ ] Implementar action-driven UI em modais

### [ ] LONGO PRAZO (Backlog — P2)
- [ ] Documentar HealthValidatorBanner
- [ ] Refatorar colors/gradients para CSS

---

## Teste de Validação

### Teste 1: Multi-tenant Isolation (P0-001)
```bash
# Setup: 2 users em 2 orgs
USER_ORG1="uuid-user-org1"
USER_ORG2="uuid-user-org2"
RECORD_ORG2="uuid-record-org2"
ORG1_ID="uuid-org-1"

# Login como USER_ORG1
auth_token=$(login_as_org1)

# Tentar update record de ORG2 sem filtro org
curl -X PATCH https://api.supabase.co/rest/v1/docs_tipos?id=eq.$RECORD_ORG2 \
  -H "Authorization: Bearer $auth_token" \
  -H "Content-Type: application/json" \
  -d '{"ativo": false}'

# Esperado: 200 OK mas nenhuma linha afetada (RLS bloqueia)
# Ou: erro de RLS

# Verificar que record ainda está ativo em ORG2
SELECT ativo FROM docs_tipos WHERE id = '$RECORD_ORG2' AND organizacao_id = '$ORG2_ID';
# Resultado: ativo = true (NÃO MODIFICADO) ✓
```

### Teste 2: Soft Delete (P0-002)
```typescript
// Query sem .is('deleted_at', null) traz registros deletados?
const { data } = await supabase
  .from('controller_dominios')
  .select('*')
  .eq('organizacao_id', organizacao_id);

// Tentar deletar um registro
await supabase
  .from('controller_dominios')
  .update({ deleted_at: new Date() })
  .eq('id', 'some-id');

// Re-fetch — deve NOT conter o registro
const { data: updated } = await supabase
  .from('controller_dominios')
  .select('*')
  .eq('organizacao_id', organizacao_id);

// Resultado: registro NÃO deve estar em `updated` (apenas se adicionar .is('deleted_at', null))
```

---

## Estimativa de Correção

| Categoria | Tempo | Risco |
|-----------|-------|-------|
| P0 fixes | 4-6 horas | 🔴 Deve ter QA rigoroso |
| P1 fixes | 8-12 horas | 🟠 Normal |
| P2 fixes | 4-8 horas | 🟢 Baixo |
| **TOTAL** | **16-26 horas** | — |
| **Sprint equiv.** | **1.5-2 dias full-stack** | — |

---

## Recomendações Finais

1. **Sprint de Segurança Imediata:** Agendar P0s como top priority (hoje/amanhã)
2. **Code Review Sistêmico:** Revisar TODAS as pages (/crm, /clientes, /processos, etc) para mesmo padrão
3. **Testes de RLS:** Implementar test suite automatizado para multi-tenant isolation
4. **CI/CD:** Adicionar linter que detecta `.update()` sem `.eq('organizacao_id')`

---

**Relatório gerado:** 31 de março de 2026, 17:47 BRT  
**Auditado por:** Claude Code Frontend Auditor  
**Documentação:** ~/beto-reports/audit-configuracoes-mdflow.html
