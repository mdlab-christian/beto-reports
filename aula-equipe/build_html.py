#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o HTML único da aula da equipe, embutindo screenshots em base64."""
import base64, os, pathlib

SHOTS = pathlib.Path(__file__).parent / "shots"
OUT = pathlib.Path(__file__).parent / "aula-mdflow-equipe.html"

def b64(name):
    p = SHOTS / name
    data = p.read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()

# mapa logico -> arquivo
IMGS = {
    "hub": "01-mdzap-hub.png",
    "conversas": "02-julia-leads-conversas.png",
    "thread": "03-julia-thread.png",
    "templates": "10-mdzap-templates.png",
    "dashboard": "09-mdzap-dashboard.png",
    "vault": "11-mdzap-Gestão.png",
    "aud_nova": "05-auditoria-nova.png",
    "aud_hist": "06-auditoria-historico.png",
    "aud_tabela": "07-auditoria-tabela.png",
    "kanban": "12-crm-kanban.png",
    "prontos": "14-crm-colunas-3.png",
    "drawer_dados": "15-crm-drawer-dados.png",
    "drawer_restr": "16-crm-drawer-restricoes.png",
    "drawer_docs": "17-crm-drawer-documentos.png",
    "gerar_docs": "18-gerar-documentos.png",
    "dist_dash": "19-distribuicao.png",
    "dist_prep": "20-dist-ag-preparacao.png",
    "dist_aguard": "22-dist-ag-distribuicao.png",
    "fila_mia": "21-dist-fila-mia.png",
}
B = {k: b64(v) for k, v in IMGS.items()}

def fig(key, caption, point=None):
    p = f'<p class="point"><span>👉 Na aula, aponte:</span> {point}</p>' if point else ""
    return f'''<figure class="shot">
      <img src="{B[key]}" alt="{caption}" loading="lazy">
      <figcaption>{caption}</figcaption>
      {p}
    </figure>'''

HTML = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MdFlow — Aula da Equipe · Da entrada do lead à distribuição</title>
<style>
  :root {{
    --bg:#12100e; --card:#1a1714; --surface:#1f1b17; --sidebar:#0d0b09;
    --fg:#f0ece4; --muted:#9a9088; --primary:#20c997; --primary-dim:#178a6a;
    --border:#322c25; --warning:#f0a82e; --danger:#e5484d; --success:#30a46c;
    --orgao:#f0a82e; --empresa:#7c8cff; --midas:#20c997;
    --radius:14px; --maxw:1000px;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; scroll-padding-top:72px; }}
  body {{
    margin:0; background:var(--bg); color:var(--fg);
    font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    line-height:1.65; font-size:16px;
  }}
  h1,h2,h3 {{ font-family:'Manrope',sans-serif; line-height:1.2; letter-spacing:-.02em; }}
  code, .mono {{ font-family:'JetBrains Mono',ui-monospace,Menlo,monospace; }}
  a {{ color:var(--primary); }}

  /* NAV */
  .topbar {{
    position:sticky; top:0; z-index:30; background:rgba(13,11,9,.92);
    backdrop-filter:blur(10px); border-bottom:1px solid var(--border);
  }}
  .topbar-inner {{ max-width:var(--maxw); margin:0 auto; padding:12px 20px;
    display:flex; align-items:center; gap:14px; flex-wrap:wrap; }}
  .logo {{ font-family:'Manrope'; font-weight:800; color:var(--primary); font-size:20px; }}
  .logo span {{ color:var(--fg); }}
  .nav {{ display:flex; gap:6px; flex-wrap:wrap; margin-left:auto; }}
  .nav a {{ color:var(--muted); text-decoration:none; font-size:13px; padding:5px 10px;
    border-radius:8px; white-space:nowrap; }}
  .nav a:hover {{ color:var(--fg); background:var(--surface); }}

  .wrap {{ max-width:var(--maxw); margin:0 auto; padding:0 20px; }}

  /* HERO */
  .hero {{ padding:64px 0 40px; text-align:center; }}
  .hero .kicker {{ color:var(--primary); font-weight:700; letter-spacing:.08em;
    text-transform:uppercase; font-size:13px; }}
  .hero h1 {{ font-size:42px; margin:14px 0 10px; }}
  .hero p.sub {{ color:var(--muted); font-size:19px; max-width:680px; margin:0 auto; }}
  .hero .meta {{ margin-top:26px; display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }}
  .pill {{ background:var(--surface); border:1px solid var(--border); border-radius:999px;
    padding:7px 15px; font-size:13px; color:var(--muted); }}
  .pill b {{ color:var(--fg); }}

  /* SECTIONS */
  section {{ padding:40px 0; border-top:1px solid var(--border); }}
  .sec-num {{ display:inline-flex; align-items:center; justify-content:center;
    width:38px; height:38px; border-radius:10px; background:var(--primary);
    color:#04221a; font-family:'Manrope'; font-weight:800; font-size:18px; }}
  .sec-head {{ display:flex; align-items:center; gap:14px; margin-bottom:6px; }}
  .sec-head h2 {{ font-size:28px; margin:0; }}
  .sec-lead {{ color:var(--muted); font-size:17px; margin:0 0 22px; }}
  h3 {{ font-size:20px; margin:30px 0 8px; }}

  /* SCREENSHOTS */
  figure.shot {{ margin:20px 0; }}
  figure.shot img {{ width:100%; border-radius:var(--radius); border:1px solid var(--border);
    box-shadow:0 14px 40px rgba(0,0,0,.45); display:block; }}
  figure.shot figcaption {{ color:var(--muted); font-size:14px; margin-top:10px;
    padding-left:12px; border-left:3px solid var(--primary); }}
  .point {{ font-size:14px; background:rgba(32,201,151,.07); border:1px solid rgba(32,201,151,.25);
    border-radius:10px; padding:10px 14px; margin-top:12px; color:var(--fg); }}
  .point span {{ color:var(--primary); font-weight:700; }}

  /* CALLOUTS */
  .box {{ border-radius:var(--radius); padding:16px 20px; margin:18px 0; border:1px solid var(--border);
    background:var(--card); }}
  .box.info {{ border-left:4px solid var(--primary); }}
  .box.warn {{ border-left:4px solid var(--warning); }}
  .box.rule {{ border-left:4px solid var(--empresa); }}
  .box h4 {{ margin:0 0 6px; font-size:15px; font-family:'Manrope'; }}
  .box.info h4 {{ color:var(--primary); }}
  .box.warn h4 {{ color:var(--warning); }}
  .box.rule h4 {{ color:var(--empresa); }}
  .box p {{ margin:6px 0; }}
  .box ul {{ margin:8px 0; padding-left:20px; }}
  .box li {{ margin:4px 0; }}

  /* FLUXOGRAMA */
  .flow {{ display:flex; flex-wrap:wrap; align-items:stretch; gap:0; margin:24px 0; }}
  .step {{ flex:1 1 0; min-width:130px; background:var(--surface); border:1px solid var(--border);
    border-radius:12px; padding:14px 12px; text-align:center; position:relative; }}
  .step .ico {{ font-size:22px; }}
  .step .t {{ font-family:'Manrope'; font-weight:700; font-size:14px; margin-top:4px; }}
  .step .d {{ font-size:12px; color:var(--muted); margin-top:3px; }}
  .arrow {{ align-self:center; color:var(--primary); font-size:22px; padding:0 6px; }}
  .flow.vert {{ flex-direction:column; }}
  .flow.vert .arrow {{ transform:rotate(90deg); padding:4px 0; }}

  /* TABELA */
  table {{ width:100%; border-collapse:collapse; margin:18px 0; font-size:14px; }}
  th,td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--border); }}
  th {{ color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase;
    letter-spacing:.04em; }}
  td .tag {{ display:inline-block; padding:2px 8px; border-radius:6px; font-size:11px;
    font-family:'JetBrains Mono'; }}
  .tag.midas {{ background:rgba(32,201,151,.15); color:var(--midas); }}
  .tag.orgao {{ background:rgba(240,168,46,.15); color:var(--orgao); }}
  .tag.empresa {{ background:rgba(124,140,255,.15); color:var(--empresa); }}

  /* TIER cards */
  .tiers {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:18px 0; }}
  .tier {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; }}
  .tier .badge {{ font-family:'JetBrains Mono'; font-size:11px; padding:3px 9px; border-radius:6px; }}
  .tier h4 {{ margin:10px 0 6px; font-family:'Manrope'; }}
  .tier p {{ font-size:13px; color:var(--muted); margin:0; }}
  .tier code {{ color:var(--fg); font-size:12px; }}

  /* PLAYBOOK */
  .pb {{ background:linear-gradient(180deg, rgba(32,201,151,.06), transparent); }}
  .recipe {{ counter-reset:step; }}
  .recipe .r {{ display:flex; gap:16px; margin:16px 0; align-items:flex-start; }}
  .recipe .r .n {{ flex:0 0 34px; height:34px; border-radius:50%; background:var(--primary);
    color:#04221a; font-family:'Manrope'; font-weight:800; display:flex; align-items:center;
    justify-content:center; }}
  .recipe .r .c h4 {{ margin:4px 0 4px; font-family:'Manrope'; font-size:16px; }}
  .recipe .r .c p {{ margin:0; color:var(--muted); font-size:14px; }}
  .tmpl {{ background:var(--sidebar); border:1px solid var(--border); border-radius:12px;
    padding:18px 20px; margin:18px 0; font-size:14px; }}
  .tmpl .label {{ color:var(--primary); font-family:'JetBrains Mono'; font-size:12px; }}
  .tmpl .ex {{ color:var(--muted); font-style:italic; }}

  footer {{ padding:40px 0 60px; border-top:1px solid var(--border); color:var(--muted);
    font-size:13px; text-align:center; }}

  .who {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:18px 0; }}
  .who .p {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; }}
  .who .p h4 {{ margin:0 0 4px; color:var(--primary); font-family:'Manrope'; }}
  .who .p p {{ margin:0; font-size:14px; color:var(--muted); }}

  @media (max-width:640px) {{
    .hero h1 {{ font-size:30px; }}
    .nav {{ display:none; }}
    .who {{ grid-template-columns:1fr; }}
    .flow {{ flex-direction:column; }}
    .flow .arrow {{ transform:rotate(90deg); }}
  }}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-inner">
    <div class="logo">md<span>flow</span></div>
    <nav class="nav">
      <a href="#intro">Visão geral</a>
      <a href="#mdzap">1 · MdZap & Julia</a>
      <a href="#auditoria">2 · Auditoria</a>
      <a href="#crm">3 · CRM</a>
      <a href="#docs">4 · Documentos</a>
      <a href="#procuracao">5 · Procuração</a>
      <a href="#distribuicao">6 · Distribuição</a>
      <a href="#playbook">7 · Playbook</a>
    </nav>
  </div>
</div>

<div class="wrap">

  <!-- HERO -->
  <div class="hero" id="top">
    <div class="kicker">Treinamento da equipe · MdFlow</div>
    <h1>Como funciona o sistema, do começo ao fim</h1>
    <p class="sub">Da hora em que o lead manda a primeira mensagem no WhatsApp até o processo ser distribuído na Justiça — passo a passo, com telas reais do nosso sistema.</p>
    <div class="meta">
      <span class="pill">Para: <b>Vinícius</b> & <b>Cátia</b></span>
      <span class="pill">Foco: <b>Dados</b> e <b>Documentos</b></span>
      <span class="pill">Telas reais do <b>MdFlow</b></span>
    </div>
  </div>

  <!-- INTRO / VISÃO GERAL -->
  <section id="intro">
    <div class="sec-head"><span class="sec-num">0</span><h2>A jornada de um lead, em uma olhada</h2></div>
    <p class="sec-lead">Antes de entrar em cada tela, entenda o caminho completo. Tudo que vocês fazem no dia a dia é uma etapa desta esteira.</p>

    <div class="flow">
      <div class="step"><div class="ico">📣</div><div class="t">Anúncio</div><div class="d">Site/criativo capta o lead</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">💬</div><div class="t">WhatsApp + código</div><div class="d">Lead manda o código com o CPF</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🤖</div><div class="t">Julia (MdZap)</div><div class="d">Atende, pede documentos</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🔍</div><div class="t">Auditoria</div><div class="d">Consulta restrições no CPF</div></div>
    </div>
    <div class="flow">
      <div class="step"><div class="ico">🗂️</div><div class="t">CRM</div><div class="d">Atendente revisa dados e docs</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">✍️</div><div class="t">Procuração</div><div class="d">Cliente assina pelo ZapSign</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🛡️</div><div class="t">Davi valida</div><div class="d">Confere docs antes de protocolar</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">⚖️</div><div class="t">Mia distribui</div><div class="d">Protocola o processo no EPROC</div></div>
    </div>

    <div class="box info">
      <h4>Por que entender a esteira inteira?</h4>
      <p>Vocês mexem em duas estações dela. Mas quando se sabe <b>de onde o dado veio</b> e <b>para onde ele vai</b>, fica muito mais fácil perceber quando algo está errado — e por isso esta aula foca justamente em <b>dados</b> e <b>documentos</b>.</p>
    </div>

    <div class="who">
      <div class="p"><h4>Vinícius — MdZap (Julia / SDR Leads)</h4><p>Acompanha as conversas da Julia, assume quando precisa, confere os documentos que chegam e cuida do atendimento inicial.</p></div>
      <div class="p"><h4>Cátia — CRM (+ Vinícius)</h4><p>Confere e completa os dados do lead, organiza os documentos, gera procurações e prepara o lead para virar processo.</p></div>
    </div>

    <div class="box warn">
      <h4>O sistema é nosso — e ainda está em evolução</h4>
      <p>O MdFlow é um sistema próprio, em versão beta. Algumas coisas funcionam redondas, outras ainda dão erro. A boa notícia: <b>podemos adaptar o que for preciso</b>. É exatamente por isso que existe a seção de <a href="#playbook">Playbook</a> no fim — para vocês registrarem o que melhorar.</p>
    </div>
  </section>

  <!-- 1 · MDZAP -->
  <section id="mdzap">
    <div class="sec-head"><span class="sec-num">1</span><h2>MdZap & a Julia</h2></div>
    <p class="sec-lead">O MdZap é a nossa central de WhatsApp. Cada "agente" é um número com uma função. O que nos interessa aqui é o <b>Julia Leads</b> — onde os leads novos caem e a Julia atende sozinha.</p>

    {fig("hub", "Tela inicial do MdZap: cada card é um número de WhatsApp com uma função diferente.", "que <b>Julia Leads</b> é o único onde a IA atende sozinha. Os de Acordos e Atendimento são manuais, operados por pessoas.")}

    <h3>De onde vem o lead — e o papel do código</h3>
    <p>O lead chega de um anúncio. No criativo há um link que abre o WhatsApp já com uma <b>mensagem pronta contendo um código</b> (e o CPF dentro dele). Esse código é a chave de tudo:</p>
    <div class="box rule">
      <h4>As 3 regras de ouro da Julia</h4>
      <ul>
        <li><b>Sem código, sem Julia.</b> Se alguém manda uma mensagem "fria", sem o código, a Julia <b>não responde</b> — o contato fica parado aguardando uma pessoa.</li>
        <li><b>O código cadastra o lead.</b> Na primeira mensagem com código, a Julia já cria o lead no sistema. Ela só consegue conversar porque o lead existe.</li>
        <li><b>O código tem o CPF.</b> É a partir dele que a Julia dispara a auditoria de crédito automaticamente.</li>
      </ul>
    </div>

    {fig("conversas", "Lista de conversas do Julia Leads, com os filtros por estágio no topo.", "os contadores de estágio — <b>Ag. Humano</b>, <b>Ag. Docs</b>, <b>Ag. Assinatura</b>, <b>Assinados</b>. É o termômetro da fila: mostra em que ponto cada lead está.")}

    <h3>Como a Julia conversa</h3>
    <p>Aberta uma conversa, você vê tudo o que a Julia já fez. Ela se apresenta, explica a auditoria gratuita e pede os documentos — começando pelo de identificação (RG ou CNH).</p>

    {fig("thread", "Conversa real: a Julia pedindo o documento e os avisos no topo da thread.", "os dois avisos amarelos: <b>“Restrições detectadas — aguardando revisão”</b> (a auditoria já rodou) e <b>“Janela de 24h encerrada”</b> (precisa de um Template para reabrir a conversa). Repare também no <b>CPF</b> já preenchido no topo.")}

    <div class="box info">
      <h4>A "janela de 24 horas" do WhatsApp</h4>
      <p>O WhatsApp só deixa enviar mensagem livre por 24h após o último contato do cliente. Passou disso, é preciso usar um <b>Template</b> (mensagem pré-aprovada). Por isso existe a aba de Templates 👇</p>
    </div>

    {fig("templates", "Aba Templates: mensagens HSM prontas para reabrir a conversa e cobrar pendências.", "que cada template é uma pendência específica — <b>Documento de Identificação</b>, <b>Comprovante de Residência</b>, <b>Assinatura da Procuração</b>, <b>Carteira de Trabalho</b>. Basta clicar em <b>Disparar</b>.")}

    <h3>As outras abas — para que serve cada uma</h3>
    <table>
      <tr><th>Aba</th><th>Para que serve</th></tr>
      <tr><td><b>Conversas</b></td><td>O dia a dia — todas as conversas e a fila por estágio.</td></tr>
      <tr><td><b>Dashboard</b></td><td>Números do dia: leads, procurações enviadas/assinadas, documentos recebidos.</td></tr>
      <tr><td><b>Telemetria</b></td><td>Saúde técnica da Julia (tempos de resposta, falhas).</td></tr>
      <tr><td><b>Templates</b></td><td>As mensagens prontas para reabrir a janela de 24h.</td></tr>
      <tr><td><b>Contatos</b></td><td>A agenda — todos os números, separados por Pessoas e Escritórios.</td></tr>
      <tr><td><b>Gestão</b></td><td>O "cérebro" da Julia — onde se edita como ela pensa e responde.</td></tr>
    </table>

    {fig("dashboard", "Dashboard do SDR Leads: visão rápida do funil do dia.", "os cartões <b>Proc. assinadas</b> e <b>Documentos Recebidos</b> (classificados automaticamente pela Julia em Identificação / Comprovante).")}

    {fig("vault", "Aba Gestão: o “Vault da Julia” — os arquivos que definem o comportamento dela.", "que o jeito da Julia falar e as regras dela ficam aqui (SOUL, STYLE, e as habilidades: recepção, objeção, follow-up...). É aqui que ajustamos o comportamento dela — e é disso que trata o Playbook no fim.")}
  </section>

  <!-- 2 · AUDITORIA -->
  <section id="auditoria">
    <div class="sec-head"><span class="sec-num">2</span><h2>A auditoria e as restrições</h2></div>
    <p class="sec-lead">A auditoria é a consulta que descobre se o CPF do lead tem restrições (nome sujo). É o coração do nosso serviço — e a origem dos dados de todo processo.</p>

    {fig("aud_nova", "Tela de Nova Auditoria: informa-se o CPF, escolhe-se o bureau e a consulta roda.", "que hoje usamos o bureau <b>ApiFull (CPF Completo)</b> a R$ 2,99. A Julia dispara essa mesma consulta sozinha, usando o CPF que veio no código.")}

    {fig("aud_tabela", "Histórico de auditorias: cada linha é um CPF consultado.", "a coluna <b>Restrições</b>: <b>“Processáveis”</b> (nome sujo, dá processo) vs <b>“Limpo”</b> (nome limpo). Essa é a diferença que decide se o lead vira processo ou é parabenizado e encerrado.")}

    <div class="box info">
      <h4>Como a restrição vira dado no sistema (automático)</h4>
      <p>Quando a auditoria encontra restrições, o sistema <b>cadastra cada empresa sozinho</b> dentro do lead: nome da empresa, valor, data e fonte. Ninguém digita isso à mão. Você confere e aprova — veremos essa tela no CRM, no próximo bloco.</p>
    </div>

    {fig("aud_hist", "Volume de auditorias dos últimos 30 dias.", "apenas para mostrar o volume — são milhares de consultas. Não precisa se aprofundar aqui.")}
  </section>

  <!-- 3 · CRM -->
  <section id="crm">
    <div class="sec-head"><span class="sec-num">3</span><h2>O CRM — onde o lead vira cliente</h2></div>
    <p class="sec-lead">O CRM organiza todos os leads em colunas (estágios). É a estação principal da Cátia: conferir dados, revisar restrições, organizar documentos.</p>

    {fig("kanban", "CRM em formato de colunas (Pipeline). Cada card é um lead.", "as colunas como uma esteira: <b>Novos → Em Atendimento → Ag. Documentos → Ag. Assinatura → Triagem → Prontos</b>. E nos cards os contadores de <b>restrições</b> e <b>processos</b>, além do advogado responsável.")}

    <div class="box info">
      <h4>As colunas, na ordem</h4>
      <ul>
        <li><b>Novos</b> — acabaram de chegar.</li>
        <li><b>Em Atendimento</b> — a Julia (ou a pessoa) está conversando.</li>
        <li><b>Ag. Documentos</b> — falta algum documento do cliente.</li>
        <li><b>Ag. Assinatura</b> — procuração enviada, esperando o cliente assinar.</li>
        <li><b>Triagem / Prontos</b> — dados e docs completos, pronto para virar processo.</li>
      </ul>
    </div>

    {fig("prontos", "Coluna “Prontos”: o lead já tem tudo e aparece o botão Distribuir.", "o botão <b>Distribuir</b> — é a ponte do CRM para a Distribuição. Quando o lead está aqui, o trabalho de dados e documentos foi bem feito.")}

    <h3>O drawer do lead — a ficha completa</h3>
    <p>Clicando num card, abre a ficha do lead pela lateral. É onde tudo sobre aquela pessoa fica guardado, organizado em abas.</p>

    {fig("drawer_dados", "Aba Dados: os dados pessoais e o endereço do cliente.", "que <b>todos esses campos</b> (Nome, CPF, RG, Nascimento, Profissão, Endereço completo) são os mesmos que entram na petição inicial. Campo vazio ou errado aqui = problema na inicial lá na frente.")}

    <div class="box warn">
      <h4>Por que os dados precisam estar certos</h4>
      <p>Cada dado da aba Dados vira um <b>placeholder</b> (uma lacuna) na petição inicial: nome, CPF, endereço, profissão... Se o endereço estiver incompleto, por exemplo, a inicial sai errada — e o sistema nem consegue saber em qual estado/comarca distribuir. <b>Conferir dados é conferir a qualidade do processo.</b></p>
    </div>

    {fig("drawer_restr", "Aba Restrições: as empresas que negativaram o cliente, cadastradas pela auditoria.", "o resumo no topo (<b>Total</b>, <b>Processáveis</b>, <b>Valor Total</b>) e cada empresa com sua <b>fonte</b> (SCPC/Boa Vista) e a marca <b>Processável</b> ou <b>Não processável</b>. Só as processáveis viram ação judicial.")}
  </section>

  <!-- 4 · DOCUMENTOS -->
  <section id="docs">
    <div class="sec-head"><span class="sec-num">4</span><h2>Documentos & os "tiers"</h2></div>
    <p class="sec-lead">Cada documento do cliente tem um lugar e um nome certo. Entender essa organização evita o erro mais comum: documento que não chega à etapa seguinte.</p>

    {fig("drawer_docs", "Aba Documentos do lead: cada arquivo tem um número e um nome padronizado.", "o padrão do nome: <b>“3 - CNH NOME”</b>, <b>“4 - Comprovante de Residência NOME”</b>, <b>“5 - Situação Cadastral CPF NOME”</b>. O número na frente é o <b>tier</b> (a ordem/categoria) e o nome do cliente vem sempre no fim. Por isso o sistema reconhece e organiza tudo no Drive.")}

    <div class="box info">
      <h4>O que é o "tier" de um documento</h4>
      <p>Pense no tier como a <b>gaveta numerada</b> de cada tipo de documento. O sistema usa esse número para saber qual documento é qual e para onde ele vai. Um arquivo com nome fora do padrão pode <b>não ser reconhecido</b> e ficar parado — é por isso que a nomenclatura importa tanto.</p>
    </div>

    <h3>O fluxo de um documento</h3>
    <div class="flow">
      <div class="step"><div class="ico">📥</div><div class="t">Cliente envia</div><div class="d">Foto/PDF no WhatsApp</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🔎</div><div class="t">Julia lê</div><div class="d">Identifica o tipo (CNH, comprovante...)</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🏷️</div><div class="t">Nomeia no padrão</div><div class="d">"N - Tipo NOME"</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">📁</div><div class="t">Salva no Drive</div><div class="d">Vinculado ao lead</div></div>
    </div>

    <div class="box warn">
      <h4>O erro nº 1 a evitar</h4>
      <p>Documento ilegível, cortado, ou que não é o que o cliente disse. Se a Julia não conseguir ler, ela pede de novo. Quando vocês conferem manualmente, é isso que olham: <b>está legível? é o documento certo? o nome bate com o cliente?</b></p>
    </div>
  </section>

  <!-- 5 · PROCURAÇÃO -->
  <section id="procuracao">
    <div class="sec-head"><span class="sec-num">5</span><h2>Procuração & as iniciais</h2></div>
    <p class="sec-lead">Com dados e documentos prontos, geramos os documentos jurídicos. Aqui é onde os dados que vocês conferiram viram, de fato, a base do processo.</p>

    {fig("gerar_docs", "Modal “Gerar Documentos”: os pacotes gerados para o cliente, um por empresa.", "as etiquetas de tipo — <b>Midas</b>, <b>Órgão</b> e <b>Empresa</b>. Cada restrição vira um pacote (procuração + contrato + termo de veracidade). E a <b>OAB do advogado</b> (131163/RS) aparece embaixo.")}

    <div class="tiers">
      <div class="tier"><span class="badge" style="background:rgba(32,201,151,.15);color:var(--midas)">Midas</span>
        <h4>Contrato Midas</h4><p>O contrato do cliente com a Midas. Gerado uma vez por cliente.</p></div>
      <div class="tier"><span class="badge" style="background:rgba(240,168,46,.15);color:var(--orgao)">Órgão</span>
        <h4>Contra o bureau</h4><p>Ex.: Boa Vista. Procuração e termos contra o órgão que mantém a restrição.</p></div>
      <div class="tier"><span class="badge" style="background:rgba(124,140,255,.15);color:var(--empresa)">Empresa</span>
        <h4>Contra cada credor</h4><p>Ex.: Lojas Lebes, Mercado Pago. Um pacote para cada empresa que negativou.</p></div>
    </div>

    <h3>Como a assinatura funciona</h3>
    <div class="flow">
      <div class="step"><div class="ico">📝</div><div class="t">Gera os pacotes</div><div class="d">Procuração + contrato + termo</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🔗</div><div class="t">Envia o link</div><div class="d">ZapSign pelo MdZap</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">⏰</div><div class="t">Follow-up</div><div class="d">Julia cobra em 1h e 24h</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">✅</div><div class="t">Assinou</div><div class="d">Lead vira cliente</div></div>
    </div>

    <div class="box info">
      <h4>Os "placeholders" da inicial</h4>
      <p>A petição é um modelo com lacunas. Cada lacuna é preenchida automaticamente com um dado do lead: <code>{{nome}}</code>, <code>{{cpf}}</code>, <code>{{endereço}}</code>, <code>{{profissão}}</code>, <code>{{empresa ré}}</code>, <code>{{valor}}</code>... É por isso que insistimos tanto: <b>dado preenchido certo no CRM = inicial gerada certa, sem retrabalho.</b></p>
    </div>
  </section>

  <!-- 6 · DISTRIBUIÇÃO -->
  <section id="distribuicao">
    <div class="sec-head"><span class="sec-num">6</span><h2>Distribuição — o Davi e a Mia</h2></div>
    <p class="sec-lead">É a última etapa: levar o processo pronto até o protocolo na Justiça (EPROC). Dois agentes cuidam disso — o Davi confere, a Mia protocola.</p>

    {fig("dist_dash", "Central de Distribuição: a visão geral dos processos a caminho da Justiça.", "as abas <b>Ag. Preparação</b>, <b>Ag. Distribuição</b> e <b>Fila Mia</b>, e os números do dia (quantos foram distribuídos hoje).")}

    <h3>O Davi — o conferente</h3>
    <p>Quando o lead é distribuído pelo CRM, ele cai em <b>"Aguardando preparação"</b>. Ali existe o botão <b>"Validar com Davi"</b>: o Davi confere se os documentos e dados estão completos antes de virar petição.</p>

    {fig("dist_prep", "Aba Ag. Preparação: o botão “Validar com Davi” e o status “Aguardando Davi”.", "o botão <b>Validar com Davi</b> e, no card, o status <b>Aguardando Davi</b> + os botões <b>Gerar Petição</b> e <b>Enviar</b>. Hoje quem opera isso é o Gustavo, mas é assim que funciona.")}

    <div class="box rule">
      <h4>O que é o Davi</h4>
      <p>Um agente que faz a <b>conferência final dos documentos</b> antes do protocolo. Ele é a trava de segurança: se faltar documento ou um dado estiver errado, ele segura — evitando que um processo saia com erro.</p>
    </div>

    <h3>A Mia — a distribuidora</h3>
    <p>Validado pelo Davi, o processo vai para <b>"Ag. Distribuição"</b>. A Mia é quem entra no EPROC e <b>protocola de verdade</b>, sozinha.</p>

    {fig("dist_aguard", "Aba Ag. Distribuição: a fila de processos prontos para a Mia protocolar.", "a coluna <b>Petição</b> (“Petição OK”), o <b>Advogado</b> por estado (SP, RS) e o botão <b>Distribuir Todos</b>, que entrega a fila para a Mia.")}

    {fig("fila_mia", "Fila Mia: o desempenho do robô que protocola os processos.", "que a Mia já protocolou <b>110 processos</b> com tempo médio de <b>~2 minutos</b> cada. É o tipo de trabalho repetitivo que o robô faz por nós.")}

    <div class="box warn">
      <h4>Sobre os advogados — por que nem sempre é automático</h4>
      <p>O processo precisa ser distribuído por um advogado <b>do estado certo</b> (a comarca do cliente). O sistema escolhe o advogado pela <b>localização do lead</b>. Se o <b>endereço estiver incompleto</b>, ele não sabe o estado — e aí o advogado <b>não é atribuído automaticamente</b>. De novo: tudo volta para a qualidade do dado de endereço. 📍</p>
    </div>

    <div class="flow vert" style="max-width:560px;margin:24px auto;">
      <div class="step"><div class="ico">🗂️</div><div class="t">CRM → Distribuir</div><div class="d">Lead pronto entra na distribuição</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">🛡️</div><div class="t">Davi valida</div><div class="d">Confere docs e dados · gera petição</div></div>
      <div class="arrow">→</div>
      <div class="step"><div class="ico">⚖️</div><div class="t">Mia protocola</div><div class="d">Entra no EPROC e distribui</div></div>
    </div>
  </section>

  <!-- 7 · PLAYBOOK -->
  <section id="playbook" class="pb">
    <div class="sec-head"><span class="sec-num">7</span><h2>O Playbook — como pedir melhorias</h2></div>
    <p class="sec-lead">Esta é a parte mais importante para o futuro. Como o sistema é nosso e está em evolução, vocês são os olhos no dia a dia. Mas dizer "queria que tivesse isso" não basta — precisamos de um <b>playbook</b>.</p>

    <div class="box info">
      <h4>O que é um playbook (e por que ele facilita tudo)</h4>
      <p>É um registro organizado dos erros que vocês encontram e de como o sistema <b>deveria</b> ter se comportado. Com um playbook em mãos, o Gustavo corrige rápido — sem precisar adivinhar o que aconteceu nem perguntar item por item. <b>Um bom relato hoje = uma correção amanhã.</b></p>
    </div>

    <h3>Como montar um relato — a receita</h3>
    <div class="recipe">
      <div class="r"><div class="n">1</div><div class="c"><h4>Print da tela</h4><p>Toda observação começa com uma captura de tela do que aconteceu. Sem print, fica difícil entender.</p></div></div>
      <div class="r"><div class="n">2</div><div class="c"><h4>O que aconteceu</h4><p>Descreva em uma frase o problema. Ex.: "a Julia pediu o documento de novo, mas o cliente já tinha enviado".</p></div></div>
      <div class="r"><div class="n">3</div><div class="c"><h4>O que era para acontecer</h4><p>Diga o comportamento esperado. Ex.: "ela deveria ter reconhecido que aquilo era uma CNH e seguido em frente".</p></div></div>
      <div class="r"><div class="n">4</div><div class="c"><h4>Um exemplo concreto</h4><p>Se der, mostre como a resposta certa seria. Quanto mais concreto, mais rápido o ajuste.</p></div></div>
      <div class="r"><div class="n">5</div><div class="c"><h4>Junte tudo num HTML</h4><p>Vão acumulando os relatos numa conversa com o ChatGPT. No fim, peçam para gerar um HTML — esse é o playbook que vocês me entregam.</p></div></div>
    </div>

    <h3>Modelo de relato (copie e preencha)</h3>
    <div class="tmpl">
      <p><span class="label">📍 ONDE:</span> &nbsp;(qual tela / aba / conversa)<br>
      <span class="ex">Ex.: MdZap · Julia Leads · conversa do cliente Fulano</span></p>
      <p><span class="label">📸 PRINT:</span> &nbsp;(anexar a captura de tela)</p>
      <p><span class="label">⚠️ O QUE ACONTECEU:</span><br>
      <span class="ex">Ex.: O cliente mandou a CNH, mas a Julia pediu o documento de identificação de novo.</span></p>
      <p><span class="label">✅ O QUE ERA PARA ACONTECER:</span><br>
      <span class="ex">Ex.: A Julia deveria reconhecer a CNH (está escrito "Carteira Nacional de Habilitação") e seguir para o comprovante de residência.</span></p>
      <p><span class="label">💡 SUGESTÃO (opcional):</span><br>
      <span class="ex">Ex.: Se o documento tiver "Habilitação" escrito e estiver legível, aceitar como CNH válida.</span></p>
    </div>

    <div class="box rule">
      <h4>Dois tipos de relato</h4>
      <ul>
        <li><b>Erro</b> — algo que funcionou diferente do esperado (o exemplo da CNH acima).</li>
        <li><b>Melhoria</b> — algo que não é erro, mas facilitaria a vida ("seria ótimo se este botão estivesse aqui"). Também vale registrar!</li>
      </ul>
    </div>

    <div class="box info">
      <h4>Resumindo o combinado</h4>
      <p>Vão guardando print + relato ao longo da semana → no fim, viram um HTML (o playbook) → me entregam. Assim a gente melhora o sistema de verdade, no ritmo de vocês, sem ninguém ficar refém de "passar coisa por coisa".</p>
    </div>
  </section>

  <footer>
    <p>MdFlow · Material de treinamento interno · Telas reais capturadas em 29/05/2026<br>
    Uso interno — contém dados de clientes. Não compartilhar fora da equipe.</p>
  </footer>

</div>
</body>
</html>'''

OUT.write_text(HTML, encoding="utf-8")
size_mb = OUT.stat().st_size / 1024 / 1024
print(f"OK -> {OUT} ({size_mb:.2f} MB)")
