import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Planificación de Siembras — Prototipo V2",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Prototipo — Planificación de Siembras</title>
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

  header { background: var(--forest); color: #fff; padding: 12px 20px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }
  header h1 { font-size: 17px; margin:0; font-weight:600; }

  .toolbar { background: var(--panel); border-bottom:1px solid var(--line); padding:10px 18px;
    display:flex; align-items:center; gap:14px; flex-wrap:wrap; }
  .tabs { display:flex; gap:4px; }
  .tab { padding:5px 11px; border-radius:6px; border:1px solid var(--line); background:#fff;
    cursor:pointer; font-size:12px; font-weight:500; }
  .tab.active { background: var(--forest); color:#fff; border-color:var(--forest); }
  
  .field { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--muted); }
  .field select, .field input { padding:4px 7px; border:1px solid var(--line);
    border-radius:6px; font-size:12px; background:#fff; color: var(--ink); }

  .stat { background:#f0efe8; border:1px solid var(--line); border-radius:7px; padding:4px 10px; }
  .stat b { font-size:13px; color: var(--forest); display:block; }
  .stat span { font-size:10px; color:var(--muted); text-transform:uppercase; }

  button.primary { background: var(--forest); color:#fff; border:none; border-radius:6px;
    padding:6px 12px; font-size:12px; font-weight:600; cursor:pointer; }
  button.primary:hover { background: var(--forest-dim); }
  button.ghost { background:#fff; border:1px solid var(--line); border-radius:6px; padding:5px 10px;
    font-size:12px; cursor:pointer; }

  .grid-wrap { flex:1; overflow:auto; position:relative; background: var(--panel); }
  table.grid { border-collapse:collapse; table-layout:fixed; }
  table.grid th, table.grid td { border:1px solid #ece9de; text-align:center; }
  
  th.corner { position:sticky; top:0; left:0; z-index:10; background:#e8e5d8; width:90px; min-width:90px; height:50px; }
  th.lotehead { position:sticky; top:0; z-index:8; background:#f0efe8; width:75px; min-width:75px;
    font-weight:600; font-size:11px; padding:4px 2px; }
  th.lotehead .sub { font-size:9.5px; font-weight:normal; color:var(--muted); }
  
  td.weekcell { position:sticky; left:0; z-index:7; background:#f0efe8; width:90px; min-width:90px;
    font-weight:600; font-size:11px; height:26px; border-right:2px solid #c9c4b2; }
  
  td.cell { width:75px; height:26px; cursor:pointer; font-size:10px; position:relative; }
  td.cell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; }
  td.cell.planted { font-weight:700; }
  td.cell.conflict { background:var(--alert-bg) !important; color:var(--alert); }

  .popup { position:absolute; z-index:50; background:#fff; border:1px solid var(--line); border-radius:8px;
    box-shadow:0 8px 24px rgba(0,0,0,.18); padding:8px; min-width:170px; }
  .popup button { display:block; width:100%; text-align:left; padding:6px 8px; border:none; background:none;
    cursor:pointer; border-radius:5px; font-size:12px; margin-bottom:2px; }
  .popup button:hover { background:#f0efe8; }
  .popup .danger { color: var(--alert); }
  .popup select { width:100%; padding:5px; margin-bottom:6px; border:1px solid var(--line); border-radius:5px; }

  .modal-overlay { position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.4);
    z-index:100; display:flex; align-items:center; justify-content:center; }
  .modal { background:#fff; padding:18px; border-radius:8px; width:300px; box-shadow:0 10px 25px rgba(0,0,0,0.2); }
  .modal h3 { margin-top:0; font-size:15px; }
  .modal label { display:block; font-size:11px; color:var(--muted); margin-top:8px; }
  .modal input { width:100%; padding:6px; margin-top:2px; border:1px solid var(--line); border-radius:5px; }
  .modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:14px; }
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>Planificación de Siembras — Lotes en Columnas</h1>
    <button class="ghost" id="splitBtn">+ Dividir Lote (A/B)</button>
  </header>

  <div class="toolbar">
    <div class="tabs" id="fincaTabs"></div>
    <div class="field">Vegetal:
      <select id="vegFilter"><option value="">Todos</option></select>
    </div>
    <div class="field">Horizonte:
      <select id="yearsFilter">
        <option value="1">1 Año (52 sem)</option>
        <option value="2" selected>2 Años (104 sem)</option>
      </select>
    </div>
    <div class="stat"><b id="statArea">–</b><span>Área en Uso (ha)</span></div>
    <div class="stat"><b id="statProd">–</b><span>Prod. Proyectada</span></div>
    <div style="flex:1"></div>
    <button class="primary" id="exportBtn">Exportar Excel</button>
  </div>

  <div class="grid-wrap" id="gridWrap"></div>
</div>

<div id="modalWrap"></div>

<script>
let totalYears = 2;
let totalWeeks = 104;

const CICLOS = {
  Ejote:    { duracion: 12, cosechas: [[10,0.35],[11,0.42],[12,0.23]], rendimiento: 11500, color:'ejote' },
  Broccoli: { duracion: 15, cosechas: [[10,0.10],[11,0.20],[12,0.17],[13,0.10],[14,0.23],[15,0.20]], rendimiento: 8000, color:'broccoli' },
  Grano:    { duracion: 14, cosechas: [[11,0.30],[12,0.36],[13,0.24],[14,0.10]], rendimiento: 8500, color:'grano' },
  China:    { duracion: 13, cosechas: [[10,0.11],[11,0.45],[12,0.37],[13,0.07]], rendimiento: 7500, color:'china' },
  Dulce:    { duracion: 14, cosechas: [[11,0.10],[12,0.20],[13,0.41],[14,0.29]], rendimiento: 10000, color:'dulce' }
};
const VEG_ORDER = Object.keys(CICLOS);
const FINCAS = ['NP','CH','TM','PV','SM'];

let LOTES = [];
function initLotes() {
  let areaSeed = [1.0, 1.2, 0.8, 1.5, 1.1];
  let idCounter = 1;
  FINCAS.forEach(f => {
    for (let i = 1; i <= 6; i++) {
      LOTES.push({
        id: f + '-' + i,
        finca: f,
        nombre: f + '-' + i,
        area: areaSeed[idCounter % areaSeed.length]
      });
      idCounter++;
    }
  });
}
initLotes();

const plantings = {};
plantings['NP-1'] = [{start: 1, vegetal: 'Ejote'}, {start: 48, vegetal: 'Broccoli'}];
plantings['NP-2'] = [{start: 5, vegetal: 'Grano'}];

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
    if (start <= (p.start + pc.duracion - 1) && p.start <= (start + c.duracion - 1)) return true;
  }
  return false;
}

function harvestValue(planting, week, area){
  const c = CICLOS[planting.vegetal];
  const rel = week - planting.start + 1;
  const cosecha = c.cosechas.find(([w])=>w===rel);
  return cosecha ? area * c.rendimiento * cosecha[1] : 0;
}

let currentFinca = 'NP';
let selectedVegFilter = '';
let popupEl = null;

function closePopup(){ if (popupEl){ popupEl.remove(); popupEl=null; } }

function openCellPopup(cellEl, loteId, week, activePlanting){
  closePopup();
  const p = document.createElement('div');
  p.className = 'popup';

  if (!activePlanting) {
    p.innerHTML = `<div style="font-size:11px;color:var(--muted);margin-bottom:4px;">Sembrar en Sem ${week}</div>` +
      VEG_ORDER.map(v => `<button data-v="${v}">${v} (${CICLOS[v].duracion} sem)</button>`).join('');
    
    p.querySelectorAll('button').forEach(btn => {
      btn.onclick = () => {
        const veg = btn.dataset.v;
        if (hasConflict(loteId, week, veg)){
          alert('Existe conflicto con otro cultivo en esas semanas.');
          return;
        }
        plantings[loteId] = plantings[loteId] || [];
        plantings[loteId].push({start: week, vegetal: veg});
        closePopup(); render();
      };
    });
  } else {
    p.innerHTML = `<div style="font-size:11px;color:var(--muted);margin-bottom:4px;">Modificar / Cambiar</div>
      <select id="changeVegSelect">
        ${VEG_ORDER.map(v => `<option value="${v}" ${v===activePlanting.vegetal?'selected':''}>${v}</option>`).join('')}
      </select>
      <button id="btnUpdateVeg">Guardar Cambio</button>
      <button id="btnDeleteVeg" class="danger">Eliminar Siembra</button>`;

    p.querySelector('#btnUpdateVeg').onclick = () => {
      const newVeg = p.querySelector('#changeVegSelect').value;
      if (hasConflict(loteId, activePlanting.start, newVeg, activePlanting)){
        alert('La nueva duración genera conflicto con otro cultivo.');
        return;
      }
      activePlanting.vegetal = newVeg;
      closePopup(); render();
    };

    p.querySelector('#btnDeleteVeg').onclick = () => {
      plantings[loteId] = plantings[loteId].filter(x => x !== activePlanting);
      closePopup(); render();
    };
  }

  document.body.appendChild(p);
  const r = cellEl.getBoundingClientRect();
  p.style.left = (r.left + window.scrollX) + 'px';
  p.style.top = (r.bottom + window.scrollY + 2) + 'px';
  popupEl = p;
}

function openSplitModal(){
  const wrap = document.getElementById('modalWrap');
  wrap.innerHTML = `
    <div class="modal-overlay">
      <div class="modal">
        <h3>Dividir Lote en Sub-lotes</h3>
        <label>Seleccionar Lote a Dividir:</label>
        <select id="splitLoteSelect">
          ${LOTES.map(l => `<option value="${l.id}">${l.nombre} (${l.area} ha)</option>`).join('')}
        </select>
        <div class="modal-actions">
          <button class="ghost" onclick="document.getElementById('modalWrap').innerHTML=''">Cancelar</button>
          <button class="primary" id="confirmSplitBtn">Dividir Lote</button>
        </div>
      </div>
    </div>`;

  document.getElementById('confirmSplitBtn').onclick = () => {
    const targetId = document.getElementById('splitLoteSelect').value;
    const idx = LOTES.findIndex(l => l.id === targetId);
    if (idx !== -1) {
      const original = LOTES[idx];
      const halfArea = Number((original.area / 2).toFixed(2));
      
      const loteA = { id: original.id + 'A', finca: original.finca, nombre: original.nombre + 'A', area: halfArea };
      const loteB = { id: original.id + 'B', finca: original.finca, nombre: original.nombre + 'B', area: halfArea };

      LOTES.splice(idx, 1, loteA, loteB);
      
      if (plantings[original.id]) {
        plantings[loteA.id] = JSON.parse(JSON.stringify(plantings[original.id]));
        delete plantings[original.id];
      }
    }
    document.getElementById('modalWrap').innerHTML = '';
    render();
  };
}

function render(){
  totalYears = parseInt(document.getElementById('yearsFilter').value);
  totalWeeks = totalYears * 52;
  selectedVegFilter = document.getElementById('vegFilter').value;

  // Render Tabs
  const tabsWrap = document.getElementById('fincaTabs');
  tabsWrap.innerHTML = FINCAS.map(f => 
    `<div class="tab ${currentFinca===f?'active':''}" onclick="currentFinca='${f}';render();">${f}</div>`
  ).join('');

  const activeLotes = LOTES.filter(l => l.finca === currentFinca);
  const wrap = document.getElementById('gridWrap');

  let areaUsoTotal = 0;
  let prodTotal = 0;

  let tableHtml = `<table class="grid"><thead><tr><th class="corner">Semana / Año</th>`;
  activeLotes.forEach(l => {
    tableHtml += `<th class="lotehead">${l.nombre}<div class="sub">${l.area} ha</div></th>`;
  });
  tableHtml += `</tr></thead><tbody>`;

  for (let w = 1; w <= totalWeeks; w++) {
    const yearNum = Math.ceil(w / 52);
    const weekInYear = ((w - 1) % 52) + 1;
    tableHtml += `<tr><td class="weekcell">Sem ${w} <span style="font-size:9px;color:#777;">(A${yearNum}-W${weekInYear})</span></td>`;

    activeLotes.forEach(l => {
      const act = findActive(l.id, w);
      let cellStyle = '';
      let text = '';
      let isFilteredOut = false;

      if (act) {
        if (selectedVegFilter && act.vegetal !== selectedVegFilter) {
          isFilteredOut = true;
        } else {
          const c = CICLOS[act.vegetal];
          cellStyle = `background:var(--${c.color}-bg);color:var(--${c.color}-fg);`;
          if (act.start === w) text = act.vegetal;
          
          const val = harvestValue(act, w, l.area);
          if (val > 0) {
            text = Math.round(val/100)/10 + 'k';
            prodTotal += val;
          }
          if (w === 1 || act.start === w) areaUsoTotal += l.area;
        }
      }

      tableHtml += `<td class="cell ${act && !isFilteredOut?'planted':''}" style="${cellStyle}" data-lote="${l.id}" data-week="${w}">
        ${isFilteredOut ? '' : text}
      </td>`;
    });

    tableHtml += `</tr>`;
  }

  tableHtml += `</tbody></table>`;
  wrap.innerHTML = tableHtml;

  document.getElementById('statArea').textContent = areaUsoTotal.toFixed(1);
  document.getElementById('statProd').textContent = Math.round(prodTotal).toLocaleString('es-GT');

  wrap.querySelectorAll('td.cell').forEach(td => {
    td.onclick = (e) => {
      e.stopPropagation();
      const loteId = td.dataset.lote;
      const week = parseInt(td.dataset.week);
      const act = findActive(loteId, week);
      openCellPopup(td, loteId, week, act);
    };
  });
}

document.getElementById('vegFilter').innerHTML = '<option value="">Todos los vegetales</option>' + 
  VEG_ORDER.map(v => `<option value="${v}">${v}</option>`).join('');

document.getElementById('vegFilter').onchange = render;
document.getElementById('yearsFilter').onchange = render;
document.getElementById('splitBtn').onclick = openSplitModal;

document.getElementById('exportBtn').onclick = () => {
  const rows = [['Finca','Lote','Semana','Año','Vegetal','Produccion']];
  LOTES.forEach(l => {
    (plantings[l.id]||[]).forEach(p => {
      const c = CICLOS[p.vegetal];
      for(let rel=1; rel<=c.duracion; rel++){
        const w = p.start + rel - 1;
        const val = harvestValue(p, w, l.area);
        if(val > 0){
          rows.push([l.finca, l.nombre, w, Math.ceil(w/52), p.vegetal, Math.round(val)]);
        }
      }
    });
  });
  const ws = XLSX.utils.aoa_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Planificacion");
  XLSX.writeFile(wb, "Planificacion_Siembras.xlsx");
};

document.addEventListener('click', (e) => {
  if (popupEl && !popupEl.contains(e.target)) closePopup();
});

render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
