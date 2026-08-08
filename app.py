import streamlit as st
import streamlit.components.v1 as components

# Configuración de página completa
st.set_page_config(
    page_title="Planificación de Siembras — Prototipo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyectar CSS para eliminar márgenes predeterminados de Streamlit
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    iframe {
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Código HTML, CSS y JavaScript del prototipo interactivo
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Prototipo — Planificación de siembras</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<style>
  :root {
    --ink: #1b2e26;
    --paper: #f6f5f0;
    --panel: #ffffff;
    --line: #dcd8cc;
    --forest: #1f4e3d;
    --forest-dim: #3a6b57;
    --muted: #6b7268;
    --alert: #b3261e;
    --alert-bg: #fbdedc;
    --ejote-bg: #ddebf7; --ejote-fg: #1f4e79;
    --broccoli-bg: #e2efda; --broccoli-fg: #375623;
    --grano-bg: #fce4d6; --grano-fg: #833c00;
    --china-bg: #e4dfec; --china-fg: #5f3f7a;
    --dulce-bg: #fff2cc; --dulce-fg: #7f6000;
  }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; background: var(--paper); color: var(--ink);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 13px; height: 100%; overflow: hidden; }
  #app { display:flex; flex-direction:column; height:100vh; }

  header { background: var(--forest); color: #fff; padding: 14px 20px 12px;
    display:flex; align-items:baseline; justify-content:space-between; flex-wrap:wrap; gap:8px; }
  header h1 { font-size: 17px; margin:0; font-weight:600; letter-spacing:.2px; }
  header .sub { font-size: 11.5px; color: #cfe3da; margin-top:2px; }

  .toolbar { background: var(--panel); border-bottom:1px solid var(--line); padding:10px 18px;
    display:flex; align-items:center; gap:18px; flex-wrap:wrap; }
  .tabs { display:flex; gap:4px; }
  .tab { padding:6px 13px; border-radius:7px; border:1px solid var(--line); background:#fff;
    cursor:pointer; font-size:12.5px; color:var(--ink); font-weight:500; }
  .tab.active { background: var(--forest); color:#fff; border-color:var(--forest); }
  .field { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--muted); }
  .field select, .field input[type=text] { padding:5px 8px; border:1px solid var(--line);
    border-radius:6px; font-size:12.5px; background:#fff; color: var(--ink); }
  .stat { background:#f0efe8; border:1px solid var(--line); border-radius:8px; padding:6px 12px; }
  .stat b { font-size:14px; color: var(--forest); display:block; }
  .stat span { font-size:10.5px; color:var(--muted); text-transform:uppercase; letter-spacing:.4px; }
  button.primary { background: var(--forest); color:#fff; border:none; border-radius:7px;
    padding:8px 14px; font-size:12.5px; font-weight:600; cursor:pointer; }
  button.primary:hover { background: var(--forest-dim); }
  button.ghost { background:#fff; border:1px solid var(--line); border-radius:7px; padding:7px 12px;
    font-size:12px; cursor:pointer; color:var(--ink); }

  .legend { display:flex; gap:10px; padding:8px 18px; background:var(--panel); border-bottom:1px solid var(--line);
    font-size:11.5px; align-items:center; flex-wrap:wrap; }
  .chip { display:flex; align-items:center; gap:5px; }
  .swatch { width:12px; height:12px; border-radius:3px; display:inline-block; }

  .grid-wrap { flex:1; overflow:auto; position:relative; background: var(--panel); }
  table.grid { border-collapse:collapse; table-layout:fixed; }
  table.grid th, table.grid td { border:1px solid #ece9de; padding:0; }
  th.corner { position:sticky; top:0; left:0; z-index:5; background:var(--panel); width:150px; min-width:150px; }
  th.weekhead { position:sticky; top:0; z-index:3; background:#f0efe8; width:34px; min-width:34px;
    font-weight:500; color:var(--muted); font-size:9.5px; text-align:center; padding:3px 0; }
  th.weekhead.month-start { border-left:2px solid #c9c4b2; }
  td.lotecell { position:sticky; left:0; z-index:2; background:var(--panel); width:150px; min-width:150px;
    padding:4px 8px; font-size:11.5px; border-right:2px solid #c9c4b2; }
  td.lotecell .fname { color:var(--forest); font-weight:700; font-size:9.5px; letter-spacing:.3px; }
  td.lotecell .lname { font-weight:600; }
  td.lotecell .area { color:var(--muted); font-size:10px; }
  td.weekcell { width:34px; height:24px; cursor:pointer; text-align:center; vertical-align:middle;
    font-size:9px; color:#333; position:relative; }
  td.weekcell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; }
  td.weekcell.planted { font-weight:700; cursor:grab; }
  td.weekcell.conflict { background:var(--alert-bg) !important; color:var(--alert); }
  td.weekcell.dragover { outline:2px dashed var(--forest); outline-offset:-2px; }

  .popup { position:absolute; z-index:50; background:#fff; border:1px solid var(--line); border-radius:8px;
    box-shadow:0 8px 24px rgba(0,0,0,.18); padding:8px; min-width:150px; }
  .popup button { display:block; width:100%; text-align:left; padding:6px 8px; border:none; background:none;
    cursor:pointer; border-radius:5px; font-size:12px; margin-bottom:2px; }
  .popup button:hover { background:#f0efe8; }
  .popup .danger { color: var(--alert); }
  .popup .hint { font-size:10px; color:var(--muted); padding:4px 8px 6px; border-top:1px solid var(--line); margin-top:4px; }

  footer { background:#fff; border-top:1px solid var(--line); padding:6px 18px; font-size:10.5px; color:var(--muted); }
</style>
</head>
<body>
<div id="app">
  <header>
    <div>
      <h1>Planificación de siembras — prototipo</h1>
      <div class="sub">150 lotes de ejemplo · datos ilustrativos</div>
    </div>
    <div class="sub">150 lotes × 106 semanas en tiempo real</div>
  </header>

  <div class="toolbar">
    <div class="tabs" id="fincaTabs"></div>
    <div class="field">Vegetal a sumar
      <select id="vegFilter"><option value="">Todos</option></select>
    </div>
    <div class="stat"><b id="statArea">–</b><span>Área en uso (ha)</span></div>
    <div class="stat"><b id="statLibre">–</b><span>Área libre (ha)</span></div>
    <div class="stat"><b id="statProd">–</b><span>Producción acumulada</span></div>
    <div style="flex:1"></div>
    <button class="ghost" id="agronomoToggle">Vista agrónomo (solo lectura)</button>
    <button class="primary" id="exportBtn">Exportar reporte a Excel</button>
  </div>

  <div class="legend" id="legend"></div>

  <div class="grid-wrap" id="gridWrap"></div>

  <footer>Clic en una semana vacía para sembrar · clic y arrastra el inicio de un ciclo para moverlo · clic en un ciclo para ver opciones</footer>
</div>

<script>
const N_WEEKS = 106;
const START_DATE = new Date(2025, 11, 29);

const CICLOS = {
  Ejote:    { duracion: 12, cosechas: [[10,0.35],[11,0.42],[12,0.23]],                         rendimiento: 11500, color:'ejote' },
  Broccoli: { duracion: 15, cosechas: [[10,0.10],[11,0.20],[12,0.17],[13,0.10],[14,0.23],[15,0.20]], rendimiento: 8000,  color:'broccoli' },
  Grano:    { duracion: 14, cosechas: [[11,0.30],[12,0.36],[13,0.24],[14,0.10]],                rendimiento: 8500,  color:'grano' },
  China:    { duracion: 13, cosechas: [[10,0.11],[11,0.45],[12,0.37],[13,0.07]],                rendimiento: 7500,  color:'china' },
  Dulce:    { duracion: 14, cosechas: [[11,0.10],[12,0.20],[13,0.41],[14,0.29]],                rendimiento: 10000, color:'dulce' },
};
const VEG_ORDER = Object.keys(CICLOS);
const FINCAS = ['NP','CH','TM','PV','SM'];
const FINCA_COUNTS = { NP:50, CH:25, TM:25, PV:25, SM:25 };

function genLotes() {
  const lotes = [];
  let n = 1;
  const areaSeed = [0.93,1.12,1.07,0.9,1.0,1.01,0.73,0.9,1.08,0.78,1.0,1.34,1.05,1.4,0.65,1.16,1.12,1.0,1.14,0.85];
  FINCAS.forEach(f => {
    for (let i=0;i<FINCA_COUNTS[f];i++){
      lotes.push({ id: f+'-'+(i+1), finca:f, nombre:String(i+1), area: areaSeed[(n)%areaSeed.length] , n});
      n++;
    }
  });
  return lotes;
}
const LOTES = genLotes();

const plantings = {};
[[0,'Ejote',1],[1,'Grano',1],[2,'China',1],[3,'Broccoli',5],[4,'Dulce',3],
 [50,'Ejote',1],[51,'Grano',8],[75,'Broccoli',1],[100,'China',1],[125,'Dulce',1]].forEach(([idx,veg,wk])=>{
  const l = LOTES[idx]; if(!l) return;
  plantings[l.id] = plantings[l.id] || [];
  plantings[l.id].push({start: wk, vegetal: veg});
});

function findActive(loteId, week){
  const list = plantings[loteId] || [];
  for (const p of list){
    const c = CICLOS[p.vegetal];
    if (week >= p.start && week < p.start + c.duracion) return p;
  }
  return null;
}

function hasConflict(loteId, start, vegetal, ignore){
  const c = CICLOS[vegetal];
  const list = (plantings[loteId]||[]).filter(p=>p!==ignore);
  for (const p of list){
    const pc = CICLOS[p.vegetal];
    const aStart=start, aEnd=start+c.duracion-1;
    const bStart=p.start, bEnd=p.start+pc.duracion-1;
    if (aStart <= bEnd && bStart <= aEnd) return true;
  }
  return false;
}

function harvestValue(planting, week, area){
  const c = CICLOS[planting.vegetal];
  const rel = week - planting.start + 1;
  const cosecha = c.cosechas.find(([w])=>w===rel);
  if (!cosecha) return 0;
  return area * c.rendimiento * cosecha[1];
}

let currentFinca = '';
let agronomoMode = false;

function visibleLotes(){
  return currentFinca ? LOTES.filter(l=>l.finca===currentFinca) : LOTES;
}

function buildTabs(){
  const wrap = document.getElementById('fincaTabs');
  wrap.innerHTML = '';
  const mkTab = (label, val) => {
    const b = document.createElement('div');
    b.className = 'tab' + (currentFinca===val ? ' active':'');
    b.textContent = label;
    b.onclick = () => { currentFinca = val; render(); };
    wrap.appendChild(b);
  };
  mkTab('Todas', '');
  FINCAS.forEach(f => mkTab(f + ' (' + FINCA_COUNTS[f] + ')', f));
}

function buildVegFilter(){
  const sel = document.getElementById('vegFilter');
  sel.innerHTML = '<option value="">Todos</option>' +
    VEG_ORDER.map(v=>`<option value="${v}">${v}</option>`).join('');
  sel.onchange = () => render();
}

function buildLegend(){
  const el = document.getElementById('legend');
  el.innerHTML = VEG_ORDER.map(v =>
    `<div class="chip"><span class="swatch" style="background:var(--${CICLOS[v].color}-bg);border:1px solid var(--${CICLOS[v].color}-fg)"></span>${v} (${CICLOS[v].duracion} sem)</div>`
  ).join('') + '<div class="chip"><span class="swatch" style="background:var(--alert-bg);border:1px solid var(--alert)"></span>Conflicto</div>';
}

let popupEl = null;
function closePopup(){ if (popupEl){ popupEl.remove(); popupEl=null; } }

function openPlantPopup(cellEl, loteId, week){
  closePopup();
  const p = document.createElement('div');
  p.className = 'popup';
  p.innerHTML = `<div style="font-size:11px;color:var(--muted);padding:2px 8px 6px;">Sembrar en semana ${week}</div>` +
    VEG_ORDER.map(v=>`<button data-v="${v}">${v} (${CICLOS[v].duracion} sem)</button>`).join('');
  document.body.appendChild(p);
  const r = cellEl.getBoundingClientRect();
  p.style.left = (r.left + window.scrollX) + 'px';
  p.style.top = (r.bottom + window.scrollY + 4) + 'px';
  p.querySelectorAll('button').forEach(btn=>{
    btn.onclick = () => {
      const veg = btn.dataset.v;
      if (hasConflict(loteId, week, veg)){
        alert('Esa semana choca con un ciclo activo en este lote.');
        return;
      }
      plantings[loteId] = plantings[loteId] || [];
      plantings[loteId].push({start: week, vegetal: veg});
      closePopup();
      render();
    };
  });
  popupEl = p;
}

function openManagePopup(cellEl, loteId, planting){
  closePopup();
  const p = document.createElement('div');
  p.className = 'popup';
  p.innerHTML = `<div style="font-size:11px;color:var(--muted);padding:2px 8px 6px;">${planting.vegetal} · siembra semana ${planting.start}</div>
    <button data-a="move">Mover (arrastra el inicio del ciclo)</button>
    <button data-a="del" class="danger">Eliminar siembra</button>
    <div class="hint">También puedes arrastrar la celda de inicio directamente a otra semana.</div>`;
  document.body.appendChild(p);
  const r = cellEl.getBoundingClientRect();
  p.style.left = (r.left + window.scrollX) + 'px';
  p.style.top = (r.bottom + window.scrollY + 4) + 'px';
  p.querySelector('[data-a=del]').onclick = () => {
    plantings[loteId] = (plantings[loteId]||[]).filter(x=>x!==planting);
    closePopup(); render();
  };
  p.querySelector('[data-a=move]').onclick = () => { closePopup(); };
  popupEl = p;
}

let dragInfo = null;

function render(){
  buildTabs();
  const lotes = visibleLotes();
  const wrap = document.getElementById('gridWrap');

  const vegSel = document.getElementById('vegFilter').value;
  let areaUso=0, areaLibre=0, prodTotal=0;
  lotes.forEach(l=>{
    if (findActive(l.id, 1)) areaUso += l.area; else areaLibre += l.area;
    (plantings[l.id]||[]).forEach(p=>{
      if (vegSel && p.vegetal!==vegSel) return;
      const c = CICLOS[p.vegetal];
      for (let rel=1; rel<=c.duracion; rel++){
        const w = p.start+rel-1;
        prodTotal += harvestValue(p, w, l.area);
      }
    });
  });
  document.getElementById('statArea').textContent = areaUso.toFixed(1);
  document.getElementById('statLibre').textContent = areaLibre.toFixed(1);
  document.getElementById('statProd').textContent = Math.round(prodTotal).toLocaleString('es-GT');

  const table = document.createElement('table');
  table.className = 'grid';
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  const corner = document.createElement('th');
  corner.className='corner'; corner.textContent='Lote';
  trh.appendChild(corner);
  for (let w=1; w<=N_WEEKS; w++){
    const th = document.createElement('th');
    th.className='weekhead' + (((w-1)%53)===0 ? ' month-start':'');
    th.textContent = w;
    trh.appendChild(th);
  }
  thead.appendChild(trh);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  lotes.forEach(l=>{
    const tr = document.createElement('tr');
    const tdl = document.createElement('td');
    tdl.className='lotecell';
    tdl.innerHTML = `<div class="fname">${l.finca}</div><div class="lname">Lote ${l.nombre}</div><div class="area">${l.area.toFixed(2)} ha</div>`;
    tr.appendChild(tdl);
    for (let w=1; w<=N_WEEKS; w++){
      const td = document.createElement('td');
      td.className='weekcell';
      const act = findActive(l.id, w);
      if (act){
        const c = CICLOS[act.vegetal];
        td.classList.add('planted');
        td.style.background = `var(--${c.color}-bg)`;
        td.style.color = `var(--${c.color}-fg)`;
        const isStart = (act.start===w);
        if (isStart){ td.textContent = act.vegetal.slice(0,2); td.draggable = !agronomoMode; }
        else {
          const val = harvestValue(act, w, l.area);
          if (val>0) td.textContent = Math.round(val/100)/10 + 'k';
        }
        if (!agronomoMode){
          td.onclick = (e) => { e.stopPropagation(); if (isStart) openManagePopup(td, l.id, act); };
          td.ondragstart = (e) => { dragInfo = {loteId:l.id, planting:act}; e.dataTransfer.setData('text','x'); };
        }
      } else if (!agronomoMode) {
        td.onclick = (e) => { e.stopPropagation(); openPlantPopup(td, l.id, w); };
      }
      if (!agronomoMode){
        td.ondragover = (e) => { e.preventDefault(); td.classList.add('dragover'); };
        td.ondragleave = () => td.classList.remove('dragover');
        td.ondrop = (e) => {
          e.preventDefault(); td.classList.remove('dragover');
          if (!dragInfo) return;
          const { loteId, planting } = dragInfo;
          if (loteId !== l.id){ dragInfo=null; return; }
          if (hasConflict(loteId, w, planting.vegetal, planting)){
            td.classList.add('conflict');
            setTimeout(()=>td.classList.remove('conflict'), 700);
            dragInfo=null; return;
          }
          planting.start = w;
          dragInfo = null;
          render();
        };
      }
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.innerHTML = '';
  wrap.appendChild(table);
}

document.getElementById('agronomoToggle').onclick = () => {
  agronomoMode = !agronomoMode;
  document.getElementById('agronomoToggle').textContent = agronomoMode
    ? 'Salir de vista agrónomo' : 'Vista agrónomo (solo lectura)';
  if (agronomoMode && !currentFinca) currentFinca = FINCAS[0];
  render();
};

document.getElementById('exportBtn').onclick = () => {
  const lotes = visibleLotes();
  const rows = [['Finca','Lote','Área_ha','Semana','Fecha','Vegetal','Producción']];
  lotes.forEach(l=>{
    (plantings[l.id]||[]).forEach(p=>{
      const c = CICLOS[p.vegetal];
      for (let rel=1; rel<=c.duracion; rel++){
        const w = p.start+rel-1;
        const val = harvestValue(p, w, l.area);
        if (val>0){
          const d = new Date(START_DATE); d.setDate(d.getDate() + (w-1)*7);
          rows.push([l.finca, l.nombre, l.area, w, d.toLocaleDateString('es-GT'), p.vegetal, Math.round(val)]);
        }
      }
    });
  });
  const wsData = XLSX.utils.aoa_to_sheet(rows);
  const wbOut = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wbOut, wsData, 'Reporte planificación');
  XLSX.writeFile(wbOut, 'Reporte_Planificacion.xlsx');
};

document.addEventListener('click', (e)=>{
  if (popupEl && !popupEl.contains(e.target)) closePopup();
});

buildVegFilter();
buildLegend();
render();
</script>
</body>
</html>
"""

# Renderizar el componente web en pantalla completa
components.html(html_code, height=900, scrolling=True)
