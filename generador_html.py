#!/usr/bin/env python3
"""
BUILD HTML V2 - version corregida:
- Emojis reales (no double-escaped)
- Correcto index del JSON (campo 'correct')
- Sin preguntas con < 2 opciones
- Shuffle de opciones al mostrar
- Verde neon CORRECTO / Rojo neon INCORRECTO automatico
- Confetti en correcto, icono X en incorrecto
- Auto-avance 2s
"""
import json

with open(r'C:\Users\GHOST1D\.gemini\antigravity\brain\2f09f0ca-32d6-4b4a-b5bc-4e7e88f98711\scratch\questions_data.json', 'r', encoding='utf-8') as f:
    all_q = json.load(f)

# Filtrar preguntas invalidas (menos de 2 opciones reales)
questions = []
for q in all_q:
    opts = [o for o in q.get('options', []) if o and o != '(Ver enunciado)']
    if len(opts) >= 2:
        questions.append({
            'question': q['question'],
            'options': opts[:4],
            'correct': q.get('correct', 0),
            'source': q.get('source', '')
        })

total = len(questions)
print(f"Preguntas validas: {total}")

def esc(text):
    """Escape for JS single-quoted string"""
    return (text
        .replace('\\', '\\\\')
        .replace("'", "\\'")
        .replace('\n', ' ')
        .replace('\r', '')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

# Build JS data array
js_lines = []
for q in questions:
    qtext = esc(q['question'])
    opts_js = ','.join(f"'{esc(o)}'" for o in q['options'])
    src = esc(q['source'])
    correct = min(q.get('correct', 0), len(q['options'])-1)
    js_lines.append(f"  {{q:'{qtext}',opts:[{opts_js}],src:'{src}',c:{correct}}}")

js_data = 'const QS=[' + ',\n'.join(js_lines) + '];'

sources = list(dict.fromkeys(q['source'] for q in questions))
src_options_html = '\n'.join(
    f'<option value="{esc(s)}">{s} ({sum(1 for q in questions if q["source"]==s)})</option>'
    for s in sources
)

html = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Evaluacion Integral Policial | ''' + str(total) + ''' Preguntas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --navy:#0a1628; --navy-mid:#132340; --navy-light:#1c3258;
  --gold:#c9a84c; --gold-bright:#e4c35a; --gold-dim:#8a7234;
  --neon-green:#39ff14; --neon-green-soft:#00e676;
  --green:#27ae60; --green-bg:#e8f8ef; --green-dark:#1e8449;
  --neon-red:#ff1744; --neon-red-soft:#ff5252;
  --red:#c0392b; --red-bg:#fce4e1; --red-dark:#922b21;
  --white:#ffffff; --gray-50:#f8f9fa; --gray-100:#eef0f2;
  --gray-200:#dde1e6; --gray-300:#bcc3cc; --gray-500:#6c757d;
  --gray-700:#3d4654; --gray-900:#1a1e26;
  --radius:6px;
  --font-display:'Barlow Condensed','Impact',sans-serif;
  --font-body:'Source Sans 3','Segoe UI',sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{height:100%;overflow:hidden;}
body{font-family:var(--font-body);background:var(--gray-100);color:var(--gray-900);display:flex;flex-direction:column;}

/* HEADER */
.header{
  background:linear-gradient(135deg,var(--navy) 0%,var(--navy-mid) 60%,var(--navy-light) 100%);
  color:var(--white);display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;height:54px;flex-shrink:0;
  box-shadow:0 3px 12px rgba(0,0,0,0.3);position:relative;z-index:20;
}
.header::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--gold),var(--gold-bright),var(--gold));}
.h-brand{display:flex;align-items:center;gap:12px;}
.h-shield{font-size:28px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3));}
.h-title{font-family:var(--font-display);font-size:20px;font-weight:700;letter-spacing:2px;text-transform:uppercase;}
.h-sub{font-size:11px;opacity:.7;letter-spacing:1px;text-transform:uppercase;}
.h-controls{display:flex;gap:6px;align-items:center;}
.hbtn{background:rgba(255,255,255,0.08);border:1px solid rgba(201,168,76,0.3);
  color:var(--gold-bright);padding:6px 14px;border-radius:var(--radius);
  cursor:pointer;font-family:var(--font-body);font-size:12px;font-weight:600;
  letter-spacing:.5px;transition:all .2s;text-transform:uppercase;}
.hbtn:hover{background:rgba(201,168,76,0.15);border-color:var(--gold);transform:translateY(-1px);}
.h-menu{font-size:24px;cursor:pointer;padding:4px 8px;color:var(--gold-bright);user-select:none;}

/* STATS */
.stats{background:var(--white);border-bottom:1px solid var(--gray-200);
  display:flex;justify-content:center;gap:40px;padding:10px 24px;flex-shrink:0;
  box-shadow:0 1px 3px rgba(0,0,0,0.12);}
.stat{text-align:center;}
.sv{font-family:var(--font-display);font-size:22px;font-weight:700;line-height:1;}
.sv.vq{color:var(--navy);} .sv.vok{color:var(--green);} .sv.vfail{color:var(--red);} .sv.vpts{color:var(--gold-dim);}
.sl{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;color:var(--gray-500);margin-top:2px;}

/* FILTER */
.fbar{background:var(--gray-50);padding:8px 24px;border-bottom:1px solid var(--gray-200);
  display:flex;align-items:center;gap:14px;flex-shrink:0;flex-wrap:wrap;}
.fbar label{font-size:12px;font-weight:600;color:var(--gray-500);text-transform:uppercase;letter-spacing:.5px;}
.fbar select,.fbar input{padding:6px 12px;border:1px solid var(--gray-200);border-radius:var(--radius);
  font-family:var(--font-body);font-size:13px;background:var(--white);}
.fbar select:focus,.fbar input:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgba(201,168,76,0.15);}
#fcount{font-size:12px;font-weight:700;color:var(--green);}

/* MAIN */
.main{flex:1;display:flex;overflow:hidden;position:relative;}

/* QUESTION PANEL */
.qpanel{flex:1;display:flex;flex-direction:column;padding:24px;overflow-y:auto;background:var(--gray-100);}
.qcard{background:var(--white);border:1px solid var(--gray-200);border-radius:10px;
  flex:1;display:flex;flex-direction:column;box-shadow:0 4px 12px rgba(0,0,0,0.15);
  overflow:hidden;position:relative;}
.qsrc{padding:8px 24px;background:var(--gray-50);border-bottom:1px solid var(--gray-200);
  font-size:11px;font-weight:600;color:var(--gray-500);text-transform:uppercase;letter-spacing:1px;}
.qtext{padding:28px 32px;font-size:16px;line-height:1.7;color:var(--gray-900);
  flex-shrink:0;max-height:42%;overflow-y:auto;border-bottom:2px solid var(--gold);}
.qopts{padding:20px 32px;flex:1;overflow-y:auto;}

/* OPTIONS */
.opt{display:flex;align-items:flex-start;gap:14px;padding:14px 18px;margin-bottom:8px;
  cursor:pointer;border-radius:8px;transition:all .2s;
  border:2px solid var(--gray-200);background:var(--white);}
.opt:hover{background:#f0f4ff;border-color:var(--navy-light);transform:translateX(4px);}
.opt.selected{background:#e8eef8;border-color:var(--navy);}
.opt.correct{background:#e6ffe6;border-color:var(--neon-green-soft);box-shadow:0 0 16px rgba(57,255,20,0.35);}
.opt.incorrect{background:#ffe6e6;border-color:var(--neon-red-soft);box-shadow:0 0 16px rgba(255,23,68,0.35);}
.opt.wascorrect{background:#e6ffe6;border-color:var(--neon-green-soft);box-shadow:0 0 8px rgba(57,255,20,0.2);opacity:.85;}
.ocirc{width:22px;height:22px;border:2px solid var(--gray-300);border-radius:50%;
  flex-shrink:0;margin-top:1px;display:flex;align-items:center;justify-content:center;
  transition:all .2s;font-size:13px;font-weight:700;}
.opt.selected .ocirc{border-color:var(--navy);background:var(--navy);color:var(--white);}
.opt.selected .ocirc::after{content:'';width:8px;height:8px;background:var(--white);border-radius:50%;}
.opt.correct .ocirc{border-color:var(--neon-green-soft);background:var(--neon-green-soft);color:var(--white);}
.opt.correct .ocirc::after{content:'\2713';font-size:14px;}
.opt.incorrect .ocirc{border-color:var(--neon-red-soft);background:var(--neon-red-soft);color:var(--white);}
.opt.incorrect .ocirc::after{content:'\2717';font-size:14px;}
.opt.wascorrect .ocirc{border-color:var(--neon-green-soft);background:var(--neon-green-soft);color:var(--white);}
.opt.wascorrect .ocirc::after{content:'\2713';font-size:14px;}
.otxt{font-size:15px;line-height:1.5;color:var(--gray-700);}
.opt.selected .otxt{color:var(--navy);font-weight:600;}
.opt.correct .otxt{color:var(--green-dark);font-weight:700;}
.opt.incorrect .otxt{color:var(--red-dark);font-weight:600;text-decoration:line-through;}
.opt.wascorrect .otxt{color:var(--green-dark);font-weight:600;}

/* RESULT OVERLAY */
.roverlay{display:none;position:absolute;inset:0;z-index:5;
  justify-content:center;align-items:center;flex-direction:column;
  animation:rpop .5s ease;}
.roverlay.show{display:flex;}
.roverlay.rcorrect{background:radial-gradient(circle,rgba(57,255,20,0.18) 0%,rgba(0,230,118,0.09) 70%,transparent 100%);}
.roverlay.rincorrect{background:radial-gradient(circle,rgba(255,23,68,0.14) 0%,rgba(255,82,82,0.07) 70%,transparent 100%);}
@keyframes rpop{0%{opacity:0;transform:scale(.5)} 60%{transform:scale(1.08)} 100%{opacity:1;transform:scale(1)}}
.rico{font-size:88px;margin-bottom:8px;animation:bounce .6s ease;}
@keyframes bounce{0%{transform:translateY(-30px);opacity:0} 55%{transform:translateY(10px)} 75%{transform:translateY(-6px)} 100%{transform:translateY(0);opacity:1}}
.rtxt{font-family:var(--font-display);font-size:46px;font-weight:800;letter-spacing:4px;
  text-transform:uppercase;animation:glow 1.5s ease infinite alternate;}
.rtxt.rg{color:var(--neon-green);}
.rtxt.rr{color:var(--neon-red);}
@keyframes glow{from{text-shadow:0 0 10px currentColor,0 0 20px currentColor} to{text-shadow:0 0 25px currentColor,0 0 50px currentColor,0 0 80px currentColor}}
.rsub{font-family:var(--font-display);font-size:16px;font-weight:600;color:var(--gray-500);margin-top:8px;letter-spacing:1px;}

/* CONFETTI */
.cbox{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:6;}
.conf{position:absolute;width:10px;height:10px;top:-10px;animation:cfall 2s ease-in forwards;}
@keyframes cfall{0%{transform:translateY(0) rotate(0deg);opacity:1} 100%{transform:translateY(110vh) rotate(720deg);opacity:0}}

/* BOTTOM */
.bottom{background:var(--white);padding:14px 24px;
  display:flex;justify-content:center;align-items:center;gap:16px;
  border-top:1px solid var(--gray-200);flex-shrink:0;
  box-shadow:0 -2px 8px rgba(0,0,0,0.06);}
.btn{padding:11px 28px;font-family:var(--font-display);font-size:16px;
  font-weight:600;letter-spacing:1px;text-transform:uppercase;
  border:2px solid var(--gray-200);border-radius:var(--radius);
  cursor:pointer;transition:all .2s;background:var(--white);color:var(--gray-700);}
.btn:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.15);}
.btnmain{background:var(--navy);color:var(--gold-bright);border-color:var(--navy);
  padding:13px 52px;font-size:18px;}
.btnmain:hover{background:var(--navy-mid);}
.btnmain:disabled{opacity:.35;cursor:not-allowed;transform:none;box-shadow:none;}
.btnnav{padding:11px 16px;font-size:20px;color:var(--navy);}

/* SIDEBAR */
.sidebar{width:230px;background:var(--white);border-left:3px solid var(--navy);
  display:flex;flex-direction:column;flex-shrink:0;
  transition:margin-right .35s cubic-bezier(.4,0,.2,1);z-index:10;
  box-shadow:-4px 0 16px rgba(0,0,0,0.08);}
.sidebar.collapsed{margin-right:-230px;}
.sbhead{background:var(--navy);color:var(--gold-bright);padding:12px 16px;
  font-family:var(--font-display);font-size:15px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.sbhead .shelp{cursor:pointer;font-size:16px;opacity:.7;}
.sbbody{flex:1;overflow-y:auto;}
.sbi{padding:8px 16px;font-size:13px;cursor:pointer;border-bottom:1px solid var(--gray-100);
  transition:all .15s;display:flex;justify-content:space-between;align-items:center;color:var(--gray-700);}
.sbi:hover{background:var(--gray-50);}
.sbi.active{background:#e8eef8;color:var(--navy);font-weight:700;border-left:3px solid var(--gold);}
.sbi.ok{background:#d4ffd4;color:#0a6b2e;}
.sbi.fail{background:#ffd4d4;color:#8b1a1a;}
.sbico{font-size:11px;font-weight:700;}

/* TOGGLE */
.toggle{position:absolute;right:230px;top:50%;transform:translateY(-50%);
  width:26px;height:56px;background:var(--navy);color:var(--gold-bright);
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;border-radius:8px 0 0 8px;font-size:14px;z-index:11;
  transition:right .35s cubic-bezier(.4,0,.2,1);user-select:none;}
.toggle.collapsed{right:0;}

/* MODAL */
.moverlay{display:none;position:fixed;inset:0;background:rgba(10,22,40,0.75);
  z-index:100;justify-content:center;align-items:center;backdrop-filter:blur(4px);}
.moverlay.show{display:flex;}
.modal{background:var(--white);border-radius:16px;padding:40px 48px;
  max-width:500px;width:90%;text-align:center;
  box-shadow:0 8px 32px rgba(0,0,0,0.2);border-top:4px solid var(--gold);}
.modal h2{font-family:var(--font-display);font-size:24px;font-weight:700;
  color:var(--navy);margin-bottom:20px;text-transform:uppercase;letter-spacing:1px;}
.bscore{font-family:var(--font-display);font-size:64px;font-weight:800;margin:16px 0;line-height:1;}
.bscore.pass{color:var(--green);} .bscore.fail{color:var(--red);}
.modal p{font-size:15px;color:var(--gray-500);margin:6px 0;}
.modal .btn{margin:10px 6px 0;}

@media(max-width:768px){
  .sidebar{width:190px;} .sidebar.collapsed{margin-right:-190px;}
  .toggle{right:190px;} .toggle.collapsed{right:0;}
  .stats{gap:16px;padding:8px 12px;} .sv{font-size:18px;}
  .qtext{padding:18px 20px;font-size:14px;}
  .rtxt{font-size:30px;} .rico{font-size:60px;}
}
@media print{
  .sidebar,.toggle,.stats,.fbar,.bottom,.h-controls{display:none !important;}
  body{overflow:visible;height:auto;}
}
</style>
</head>
<body>

<div class="header">
  <div class="h-brand">
    <span class="h-shield">&#x1F6E1;</span>
    <div>
      <div class="h-title">Evaluacion Integral Policial</div>
      <div class="h-sub">Mediacion &bull; Mandatorios &bull; Competencias &bull; Estandares &bull; Desarrollado por <strong>GHOST1D</strong></div>
    </div>
  </div>
  <div class="h-controls">
    <button class="hbtn" onclick="shuffleQs()">&#x1F500; Mezclar</button>
    <button class="hbtn" onclick="resetAll()">&#x21BB; Reiniciar</button>
    <button class="hbtn" onclick="showResults()">&#x1F4CA; Resultados</button>
    <span class="h-menu" onclick="toggleSB()">&#x2630;</span>
  </div>
</div>

<div class="stats">
  <div class="stat"><div class="sv vq"><span id="scur">1</span> / <span id="stot">''' + str(total) + '''</span></div><div class="sl">Cuestion</div></div>
  <div class="stat"><div class="sv vok" id="sok">0</div><div class="sl">Aciertos</div></div>
  <div class="stat"><div class="sv vfail" id="sfail">0</div><div class="sl">Fallos</div></div>
  <div class="stat"><div class="sv vpts" id="spts">0</div><div class="sl">Puntos</div></div>
</div>

<div class="fbar">
  <label>Fuente:</label>
  <select id="fsrc" onchange="applyF()">
    <option value="__all__">Todas (''' + str(total) + ''')</option>
    ''' + src_options_html + '''
  </select>
  <label>Buscar:</label>
  <input type="text" id="fsearch" placeholder="Palabra clave..." oninput="applyF()" style="width:200px;">
  <span id="fcount"></span>
</div>

<div class="main">
  <div class="qpanel">
    <div class="qcard" id="qcard">
      <div class="qsrc" id="qsrc"></div>
      <div class="qtext" id="qtext"></div>
      <div class="qopts" id="qopts"></div>
      <div class="roverlay" id="ro">
        <div class="rico" id="rico"></div>
        <div class="rtxt" id="rtxt"></div>
        <div class="rsub" id="rsub"></div>
      </div>
      <div class="cbox" id="cbox"></div>
    </div>
  </div>
  <div class="toggle" id="tog" onclick="toggleSB()">&#x25C0;</div>
  <div class="sidebar" id="sb">
    <div class="sbhead">
      <span>Cuestiones</span>
      <span class="shelp" onclick="alert('Verde = Acierto\nRojo = Fallo\nAzul = Actual')">?</span>
    </div>
    <div class="sbbody" id="sblist"></div>
  </div>
</div>

<div class="bottom">
  <button class="btn btnnav" onclick="prevQ()">&#x25C0;</button>
  <button class="btn btnmain" id="btnans" onclick="contestar()" disabled>CONTESTAR</button>
  <button class="btn btnnav" onclick="nextQ()">&#x25B6;</button>
</div>

<div class="moverlay" id="mov">
  <div class="modal">
    <h2>Resultados de la Evaluacion</h2>
    <div class="bscore" id="rscore">0%</div>
    <p id="rdet"></p>
    <p id="rbrk"></p>
    <br>
    <button class="btn" onclick="closeR()">Cerrar</button>
    <button class="btn" style="background:#fce4e1;border-color:#c0392b;color:#922b21" onclick="closeR();resetAll()">Reiniciar</button>
  </div>
</div>

<script>
''' + js_data + '''

let sdCache={}, fIdx=[], pos=0, selOpt=-1, ans={}, okN=0, failN=0;

function shuffle(a){
  const r=[...a];
  for(let i=r.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[r[i],r[j]]=[r[j],r[i]];}
  return r;
}

function prepQ(qi){
  if(sdCache[qi]) return;
  const q=QS[qi];
  const ord=shuffle(q.opts.map((_,i)=>i));
  sdCache[qi]={ord, ci: ord.indexOf(q.c)};
}

function init(){
  fIdx=QS.map((_,i)=>i);
  sdCache={};
  buildSB();
  showQ(0);
}

function showQ(p){
  if(p<0||p>=fIdx.length) return;
  pos=p; selOpt=-1;
  const qi=fIdx[p], q=QS[qi];
  prepQ(qi);
  const sd=sdCache[qi], st=ans[qi];

  document.getElementById('qsrc').innerHTML='&#x1F4CB; '+q.src;
  document.getElementById('qtext').textContent=q.q;

  const ro=document.getElementById('ro');
  ro.className='roverlay';
  document.getElementById('cbox').innerHTML='';

  const od=document.getElementById('qopts');
  od.innerHTML='';
  sd.ord.forEach((origIdx,di)=>{
    const d=document.createElement('div');
    let cls='opt';
    if(st){
      const sel=ans[qi+'_s'];
      if(di===sd.ci) cls=(di===sel&&st==='ok')?'opt correct':'opt wascorrect';
      else if(di===sel&&st==='fail') cls='opt incorrect';
    }
    d.className=cls;
    d.innerHTML='<div class="ocirc"></div><div class="otxt">'+q.opts[origIdx]+'</div>';
    if(!st) d.onclick=()=>pick(di);
    od.appendChild(d);
  });

  document.getElementById('scur').textContent=p+1;
  document.getElementById('stot').textContent=fIdx.length;

  const ba=document.getElementById('btnans');
  if(st){ba.style.display='none';}
  else{ba.style.display='';ba.disabled=true;}

  document.querySelectorAll('.sbi').forEach((el,i)=>el.classList.toggle('active',i===p));
  const ae=document.querySelector('.sbi.active');
  if(ae) ae.scrollIntoView({block:'nearest'});
}

function pick(oi){
  selOpt=oi;
  document.querySelectorAll('.opt').forEach((el,i)=>el.classList.toggle('selected',i===oi));
  document.getElementById('btnans').disabled=false;
}

function spawnConfetti(){
  const box=document.getElementById('cbox');
  box.innerHTML='';
  const cols=['#39ff14','#00e676','#ffeb3b','#00bcd4','#e040fb','#ff9800','#76ff03','#ffffff'];
  for(let i=0;i<60;i++){
    const c=document.createElement('div');
    c.className='conf';
    c.style.left=Math.random()*100+'%';
    c.style.backgroundColor=cols[Math.floor(Math.random()*cols.length)];
    c.style.animationDelay=Math.random()*0.9+'s';
    c.style.animationDuration=(1.4+Math.random()*0.8)+'s';
    c.style.width=(5+Math.random()*9)+'px';
    c.style.height=(5+Math.random()*9)+'px';
    c.style.borderRadius=Math.random()>.5?'50%':'2px';
    box.appendChild(c);
  }
}

function contestar(){
  if(selOpt<0) return;
  const qi=fIdx[pos], sd=sdCache[qi];
  ans[qi+'_s']=selOpt;
  const ok=selOpt===sd.ci;
  const ro=document.getElementById('ro');

  if(ok){
    ans[qi]='ok'; okN++;
    ro.className='roverlay show rcorrect';
    document.getElementById('rico').textContent='\U0001F389';
    document.getElementById('rtxt').className='rtxt rg';
    document.getElementById('rtxt').textContent='\u00A1CORRECTO!';
    document.getElementById('rsub').textContent='+1 Punto';
    spawnConfetti();
  } else {
    ans[qi]='fail'; failN++;
    ro.className='roverlay show rincorrect';
    document.getElementById('rico').textContent='\u274C';
    document.getElementById('rtxt').className='rtxt rr';
    document.getElementById('rtxt').textContent='INCORRECTO';
    document.getElementById('rsub').textContent='Revisa el tema';
  }

  const opts=document.querySelectorAll('.opt');
  sd.ord.forEach((origIdx,di)=>{
    opts[di].onclick=null;
    if(di===sd.ci){
      opts[di].className=(ok&&di===selOpt)?'opt correct':'opt wascorrect';
    }
    if(di===selOpt&&!ok) opts[di].className='opt incorrect';
  });

  document.getElementById('btnans').style.display='none';
  updStats(); updSBI(pos);

  setTimeout(()=>{
    ro.className='roverlay';
    document.getElementById('cbox').innerHTML='';
    if(pos<fIdx.length-1) nextQ();
  }, 2000);
}

function nextQ(){if(pos<fIdx.length-1) showQ(pos+1);}
function prevQ(){if(pos>0) showQ(pos-1);}
function goQ(p){showQ(p);}

function updStats(){
  document.getElementById('sok').textContent=okN;
  document.getElementById('sfail').textContent=failN;
  document.getElementById('spts').textContent=okN;
}

function buildSB(){
  const l=document.getElementById('sblist');
  l.innerHTML='';
  fIdx.forEach((qi,p)=>{
    const d=document.createElement('div');
    const st=ans[qi];
    d.className='sbi'+(p===0?' active':'')+(st==='ok'?' ok':st==='fail'?' fail':'');
    d.id='sb'+p;
    const ico=st==='ok'?'\u2713':st==='fail'?'\u2717':'';
    d.innerHTML='<span>Escoger '+(p+1)+'</span><span class="sbico">'+ico+'</span>';
    d.onclick=()=>goQ(p);
    l.appendChild(d);
  });
}

function updSBI(p){
  const qi=fIdx[p], d=document.getElementById('sb'+p);
  if(!d) return;
  d.className='sbi'+(p===pos?' active':'');
  const st=ans[qi];
  if(st==='ok'){d.classList.add('ok');d.querySelector('.sbico').textContent='\u2713';}
  else if(st==='fail'){d.classList.add('fail');d.querySelector('.sbico').textContent='\u2717';}
}

function toggleSB(){
  const s=document.getElementById('sb'), t=document.getElementById('tog');
  s.classList.toggle('collapsed');
  t.classList.toggle('collapsed');
  t.innerHTML=s.classList.contains('collapsed')?'&#x25B6;':'&#x25C0;';
}

function shuffleQs(){
  for(let i=fIdx.length-1;i>0;i--){
    const j=Math.floor(Math.random()*(i+1));
    [fIdx[i],fIdx[j]]=[fIdx[j],fIdx[i]];
  }
  sdCache={};
  buildSB(); showQ(0);
}

function resetAll(){
  ans={}; okN=0; failN=0; sdCache={};
  updStats();
  fIdx=QS.map((_,i)=>i);
  buildSB(); showQ(0);
}

function applyF(){
  const sf=document.getElementById('fsrc').value;
  const st=document.getElementById('fsearch').value.toLowerCase().trim();
  fIdx=[];
  QS.forEach((q,i)=>{
    if(sf!=='__all__'&&q.src!==sf) return;
    if(st&&!q.q.toLowerCase().includes(st)) return;
    fIdx.push(i);
  });
  document.getElementById('fcount').textContent=fIdx.length+' preguntas';
  buildSB(); showQ(0);
}

function showResults(){
  const tot=fIdx.length, resp=okN+failN;
  const pct=resp>0?Math.round((okN/resp)*100):0;
  const sc=document.getElementById('rscore');
  sc.textContent=pct+'%';
  sc.className='bscore '+(pct>=60?'pass':'fail');
  document.getElementById('rdet').textContent='Respondidas: '+resp+' de '+tot;
  document.getElementById('rbrk').innerHTML=
    '\u2705 Aciertos: <b>'+okN+'</b> &nbsp;|&nbsp; \u274C Fallos: <b>'+failN+'</b> &nbsp;|&nbsp; Pendientes: <b>'+(tot-resp)+'</b>';
  document.getElementById('mov').classList.add('show');
}
function closeR(){document.getElementById('mov').classList.remove('show');}

document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key==='ArrowDown'){e.preventDefault();nextQ();}
  else if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();prevQ();}
  else if(e.key==='Enter'){
    e.preventDefault();
    const b=document.getElementById('btnans');
    if(b.style.display!=='none'&&!b.disabled) contestar();
  }
  else if(e.key>='1'&&e.key<='9'){
    const oi=parseInt(e.key)-1;
    const qi=fIdx[pos];
    if(!ans[qi]&&oi<QS[qi].opts.length) pick(oi);
  }
});

init();
</script>
</body>
</html>'''

out = r'C:\Users\GHOST1D\.gemini\antigravity\scratch\test_mediacion_policial.html'
# Remove surrogate characters before writing
html_clean = html.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='replace')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html_clean)

print(f"OK - HTML generado: {out}")
print(f"Total preguntas: {total}")
from collections import Counter
c = Counter(len(q['options']) for q in questions)
for n,cnt in sorted(c.items()):
    print(f"  {n} opts: {cnt}")
