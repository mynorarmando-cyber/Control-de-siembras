import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Planificación de Siembras — Prototipo V9",
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
  .field select { padding:4px 7px; border:1px solid var(--line);
    border-radius:6px; font-size:12px; background:#fff; color: var(--ink); }

  .multi-year-selector { display:flex; gap:8px; align-items:center; background:#f0efe8; padding:3px 8px; border-radius:6px; border:1px solid var(--line); }
  .multi-year-selector label { font-size:11px; cursor:pointer; display:flex; align-items:center; gap:3px; }

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
  
  th.corner { position:sticky; top:0; left:0; z-index:10; background:#e8e5d8; width:70px; min-width:70px; height:50px; }
  th.sumhead { position:sticky; top:0; left:70px; z-index:10; background:#cbe0d7; color:var(--forest); width:130px; min-width:130px; font-size:11px; font-weight:700; border-right:2px solid var(--forest); }
  th.lotehead { position:sticky; top:0; z-index:8; background:#f0efe8; width:80px; min-width:80px;
    font-weight:600; font-size:11px; padding:4px 2px; }
  th.lotehead .sub { font-size:9.5px; font-weight:normal; color:var(--muted); }
  
  tr.year-divider td { background: var(--forest) !important; color:#fff !important; font-weight:700; font-size:12px; text-align:left; padding:4px 12px; position:sticky; left:0; z-index:9; }

  td.weekcell { position:sticky; left:0; z-index:7; background:#f0efe8; width:70px; min-width:70px;
    font-weight:600; font-size:11px; height:26px; }
  td.sumcell { position:sticky; left:70px; z-index:7; background:#e4f0ec; width:130px; min-width:130px;
    font-weight:700; font-size:11px; height:26px; border-right:2px solid var(--forest); color:var(--forest); }
  
  td.cell { width:80px; height:26px; cursor:pointer; font-size:10px; position:relative; }
  td.cell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; }
  td.cell.planted { font-weight:700; }
  td.cell.draggable { cursor:grab; }
  td.cell.dragover { outline:2px dashed var(--forest); outline-offset:-2px; background:#e2f0d9 !important; }
  td.cell.conflict { background:var(--alert-bg) !important; color:var(--alert); }

  .popup { position:absolute; z-index:50; background:#fff; border:1px solid var(--line); border-radius:8px;
    box-shadow:0 8px 24px rgba(0,0,0,.18); padding:8px; min-width:180px; }
  .popup button { display:block; width:100%; text-align:left; padding:6px 8px; border:none; background:none;
    cursor:pointer; border-radius:5px; font-size:12px; margin-bottom:2px; }
  .popup button:hover { background:#f0efe8; }
  .popup .danger { color: var(--alert); font-weight:600; border-bottom:1px solid var(--line); margin-bottom:6px; padding-bottom:6px; }

  .modal-overlay { position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.4);
    z-index:100; display:flex; align-items:center; justify-content:center; }
  .modal { background:#fff; padding:18px; border-radius:8px; width:300px; box-shadow:0 10px 25px rgba(0,0,0,0.2); }
  .modal h3 { margin-top:0; font-size:15px; }
  .modal label { display:block; font-size:11px; color:var(--muted); margin-top:8px; }
  .modal input, .modal select { width:100%; padding:6px; margin-top:2px; border:1px solid var(--line); border-radius:5px; }
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
    <div class="field">Sumar Resumen:
      <select id="summaryVegFilter"><option value="">Todos los vegetales</option></select>
    </div>
    <div class="field">Filtrar Lotes:
      <select id="loteVegFilter"><option value="">Ver Todos</option></select>
    </div>
    <div class="field">Años:
      <div class="multi-year-selector" id="yearCheckboxes"></div>
    </div>
    <div class="stat"><b id="statArea">–</b><span>Área (ha)</span></div>
    <div class="stat"><b id="statProd">–</b><span>Prod. Proyectada</span></div>
    <div style="flex:1"></div>
    <button class="primary" id="exportBtn">Exportar Excel</button>
  </div>

  <div class="grid-wrap" id="gridWrap"></div>
</div>

<div id="modalWrap"></div>

<script>
const AVAILABLE_YEARS = [2025, 2026, 2027, 2028];
let selectedYears = [2026, 2027];

const CICLOS = {
  Ejote:    { duracion: 12, cosechas: [[10,0.35],[11,0.42],[12,0.23]], rendimiento: 11500, color:'ejote' },
  Broccoli: { duracion: 15, cosechas: [[10,0.10],[11,0.20],[12,0.17],[13,0.10],[14,0.23],[15,0.20]], rendimiento: 8000, color:'broccoli' },
  Grano:    { duracion: 14, cosechas: [[11,0.30],[12,0.36],[13,0.24],[14,0.10]], rendimiento: 8500, color:'grano' },
  China:    { duracion: 13, cosechas: [[10,0.11],[11,0.45],[12,0.37],[13,0.07]], rendimiento: 7500, color:'china' },
  Dulce:    { duracion: 14, cosechas: [[11,0.10],[12,0.20],[13,0.41],[14,0.29]], rendimiento: 10000, color:'dulce' }
};

function getVegetableStyle(vegName) {
  const c = CICLOS[vegName];
  if (c && c.color) {
    return `background:var(--${c.color}-bg);color:var(--${c.color}-fg);`;
  }
  let hash = 0;
  for (let i = 0; i < vegName.length; i++) hash = vegName.charCodeAt(i) + ((hash << 5) - hash);
  const hue = Math.abs(hash % 360);
  return `background: hsl(${hue}, 65%, 88%); color: hsl(${hue}, 80%, 20%);`;
}

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
plantings['NP-1'] = [{year: 2026, weekInYear: 1, vegetal: 'Broccoli'}, {year: 2026, weekInYear: 20, vegetal: 'Broccoli'}];
plantings['CH-1'] = [{year: 2026, weekInYear: 1, vegetal: 'China'}];
plantings['TM-1'] = [{year: 2026, weekInYear: 2, vegetal: 'China'}];
plantings['PV-1'] = [{year: 2027, weekInYear: 5, vegetal: 'China'}];

let dragSource = null;

function absWeek(year, weekInYear) {
  return (year - 2020) * 52 + weekInYear;
}

function findActive(loteId, year, weekInYear){
  const list = plantings[loteId] || [];
  const currentAbs = absWeek(year, weekInYear);
  for (const p of list){
    const c = CICLOS[p.vegetal];
    if (!c) continue;
    const startAbs = absWeek(p.year, p.weekInYear);
    if (currentAbs >= startAbs && currentAbs < startAbs + c.duracion) return p;
  }
  return null;
}

function hasConflict(loteId, year, weekInYear, vegetal, ignore){
  const c = CICLOS[vegetal];
  if (!c) return false;
  const list = (plantings[loteId]||[]).filter(p=>p!==ignore);
  const startAbs = absWeek(year, weekInYear);
  for (const p of list){
    const pc = CICLOS[p.vegetal];
    if (!pc) continue;
    const pStartAbs = absWeek(p.year, p.weekInYear);
    if (startAbs <= (pStartAbs + pc.duracion - 1) && pStartAbs <= (startAbs + c.duracion - 1)) return true;
  }
  return false;
}

// Alerta preventiva cuando se siembra Broccoli de forma consecutiva
function isConsecutiveBroccoli(loteId, year, weekInYear, vegetal, ignore){
  if (vegetal !== 'Broccoli') return false;
  const list = (plantings[loteId] || []).filter(p => p !== ignore);
  const currentAbs = absWeek(year, weekInYear);
  
  // Buscar siembras anteriores en el tiempo
  const previousPlantings = list
    .filter(p => absWeek(p.year, p.weekInYear) < currentAbs)
    .sort((a,b) => absWeek(b.year, b.weekInYear) - absWeek(a.year, a.weekInYear));
    
  if (previousPlantings.length > 0 && previousPlantings[0].vegetal === 'Broccoli') {
    return true;
  }
  return false;
}

function harvestValue(planting, year, weekInYear, area){
  const c = CICLOS[planting.vegetal];
  if (!c) return 0;
  const currentAbs = absWeek(year, weekInYear);
  const startAbs = absWeek(planting.year, planting.weekInYear);
  const rel = currentAbs - startAbs + 1;
  const cosecha = c.cosechas.find(([w])=>w===rel);
  return cosecha ? area * c.rendimiento * cosecha[1] : 0;
}

function getTotalHarvestAllFincas(year, weekInYear, targetVeg) {
  let sum = 0;
  LOTES.forEach(l => {
    const list = plantings[l.id] || [];
    list.forEach(p => {
      if (!targetVeg || p.vegetal === targetVeg) {
        sum += harvestValue(p, year, weekInYear, l.area);
      }
    });
  });
  return sum;
}

let currentFinca = 'NP';
let selectedSummaryVeg = '';
let selectedLoteVeg = '';
let popupEl = null;

function closePopup(){ if (popupEl){ popupEl.remove(); popupEl=null; } }

function addPlantingWithValidation(loteId, year, weekInYear, veg, existingPlanting = null) {
  if (hasConflict(loteId, year, weekInYear, veg, existingPlanting)){
    alert('Existe conflicto con otro cultivo activo en esas semanas.');
    return false;
  }
  if (isConsecutiveBroccoli(loteId, year, weekInYear, veg, existingPlanting)){
    alert('⚠️ ALERTA DE MONOCULTIVO:\nEstá sembrando BROCCOLI inmediatamente después de un cultivo previo de Broccoli en este lote.');
  }
  
  if (existingPlanting) {
    existingPlanting.vegetal = veg;
  } else {
    plantings[loteId] = plantings[loteId] || [];
    plantings[loteId].push({year, weekInYear, vegetal: veg});
  }
  return true;
}

function openCellPopup(cellEl, loteId, year, weekInYear, activePlanting){
  closePopup();
  const p = document.createElement('div');
  p.className = 'popup';

  if (!activePlanting) {
    p.innerHTML = `<div style="font-size:11px;color:var(--muted);margin-bottom:4px;">Sembrar en ${year} — Sem ${weekInYear}</div>` +
      VEG_ORDER.map(v => `<button data-v="${v}">${v} (${CICLOS[v].duracion} sem)</button>`).join('');
    
    p.querySelectorAll('button').forEach(btn => {
      btn.onclick = () => {
        const veg = btn.dataset.v;
        if (addPlantingWithValidation(loteId, year, weekInYear, veg)) {
          closePopup(); render();
        }
      };
    });
  } else {
    const availableVegs = VEG_ORDER.filter(v => v !== activePlanting.vegetal);
    
    p.innerHTML = `
      <div style="font-size:11px;color:var(--muted);margin-bottom:4px;">Actual: <b>${activePlanting.vegetal}</b> (${activePlanting.year} - Sem ${activePlanting.weekInYear})</div>
      <button id="btnDeleteVeg" class="danger">Eliminar Siembra</button>
      <div style="font-size:10.5px;color:var(--muted);margin:4px 0 2px;">Cambiar a otro vegetal:</div>
      ${availableVegs.map(v => `<button data-v="${v}">Cambiar a ${v} (${CICLOS[v].duracion} sem)</button>`).join('')}
    `;

    p.querySelector('#btnDeleteVeg').onclick = () => {
      plantings[loteId] = plantings[loteId].filter(x => x !== activePlanting);
      closePopup(); render();
    };

    p.querySelectorAll('button[data-v]').forEach(btn => {
      btn.onclick = () => {
        const newVeg = btn.dataset.v;
        if (addPlantingWithValidation(loteId, activePlanting.year, activePlanting.weekInYear, newVeg, activePlanting)) {
          closePopup(); render();
        }
      };
    });
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

function initYearSelectorUI() {
  const container = document.getElementById('yearCheckboxes');
  container.innerHTML = AVAILABLE_YEARS.map(yr => `
    <label>
      <input type="checkbox" value="${yr}" ${selectedYears.includes(yr)?'checked':''}>
      ${yr}
    </label>
  `).join('');

  container.querySelectorAll('input').forEach(chk => {
    chk.onchange = () => {
      selectedYears = Array.from(container.querySelectorAll('input:checked')).map(i => parseInt(i.value)).sort();
      render();
    };
  });
}

function render(){
  selectedSummaryVeg = document.getElementById('summaryVegFilter').value;
  selectedLoteVeg = document.getElementById('loteVegFilter').value;

  const tabsWrap = document.getElementById('fincaTabs');
  tabsWrap.innerHTML = FINCAS.map(f => 
    `<div class="tab ${currentFinca===f?'active':''}" onclick="currentFinca='${f}';render();">${f}</div>`
  ).join('');

  const activeLotes = LOTES.filter(l => l.finca === currentFinca);
  const wrap = document.getElementById('gridWrap');

  let areaUsoTotal = 0;
  let prodTotal = 0;

  const sumColHeader = selectedSummaryVeg ? `Total ${selectedSummaryVeg} (Todas Fincas)` : 'Total Todos Vegetales';

  let tableHtml = `<table class="grid"><thead><tr>
    <th class="corner">Semana</th>
    <th class="sumhead">${sumColHeader}</th>`;
  
  activeLotes.forEach(l => {
    tableHtml += `<th class="lotehead">${l.nombre}<div class="sub">${l.area} ha</div></th>`;
  });
  tableHtml += `</tr></thead><tbody>`;

  if (selectedYears.length === 0) {
    tableHtml += `<tr><td colspan="${activeLotes.length + 2}" style="padding:20px;color:var(--muted);">Seleccione al menos un año en el filtro.</td></tr>`;
  } else {
    selectedYears.forEach(year => {
      tableHtml += `<tr class="year-divider"><td colspan="${activeLotes.length + 2}">Año ${year}</td></tr>`;

      for (let w = 1; w <= 52; w++) {
        // Total Consolidado (Resumen)
        const globalHarvest = getTotalHarvestAllFincas(year, w, selectedSummaryVeg);
        const globalHarvestTxt = globalHarvest > 0 ? Math.round(globalHarvest).toLocaleString('es-GT') : '-';

        tableHtml += `<tr>
          <td class="weekcell">${w}</td>
          <td class="sumcell">${globalHarvestTxt}</td>`;

        // Renderizado de Lotes con su filtro independiente
        activeLotes.forEach(l => {
          const act = findActive(l.id, year, w);
          let cellStyle = '';
          let text = '';
          let isStartCell = false;
          let isHiddenByLoteFilter = false;

          if (act) {
            if (selectedLoteVeg && act.vegetal !== selectedLoteVeg) {
              isHiddenByLoteFilter = true;
            } else {
              cellStyle = getVegetableStyle(act.vegetal);
              if (act.year === year && act.weekInYear === w) {
                text = act.vegetal;
                isStartCell = true;
              }
              
              const val = harvestValue(act, year, w, l.area);
              if (val > 0) {
                text = Math.round(val/100)/10 + 'k';
                prodTotal += val;
              }
              if (w === 1 || (act.year === year && act.weekInYear === w)) areaUsoTotal += l.area;
            }
          }

          const draggableAttr = (isStartCell && !isHiddenByLoteFilter) ? 'draggable="true"' : '';
          const draggableClass = (isStartCell && !isHiddenByLoteFilter) ? 'draggable' : '';

          tableHtml += `<td class="cell ${act && !isHiddenByLoteFilter?'planted':''} ${draggableClass}" ${draggableAttr} style="${cellStyle}" data-lote="${l.id}" data-year="${year}" data-week="${w}">
            ${isHiddenByLoteFilter ? '' : text}
          </td>`;
        });

        tableHtml += `</tr>`;
      }
    });
  }

  tableHtml += `</tbody></table>`;
  wrap.innerHTML = tableHtml;

  document.getElementById('statArea').textContent = areaUsoTotal.toFixed(1);
  document.getElementById('statProd').textContent = Math.round(prodTotal).toLocaleString('es-GT');

  wrap.querySelectorAll('td.cell').forEach(td => {
    const loteId = td.dataset.lote;
    const year = parseInt(td.dataset.year);
    const week = parseInt(td.dataset.week);

    td.onclick = (e) => {
      e.stopPropagation();
      const act = findActive(loteId, year, week);
      openCellPopup(td, loteId, year, week, act);
    };

    td.ondragstart = (e) => {
      const act = findActive(loteId, year, week);
      if (act && act.year === year && act.weekInYear === week) {
        dragSource = { loteId, planting: act };
        e.dataTransfer.setData('text/plain', '');
      }
    };

    td.ondragover = (e) => {
      e.preventDefault();
      if (dragSource && dragSource.loteId === loteId) {
        td.classList.add('dragover');
      }
    };

    td.ondragleave = () => {
      td.classList.remove('dragover');
    };

    td.ondrop = (e) => {
      e.preventDefault();
      td.classList.remove('dragover');
      if (!dragSource) return;

      const { loteId: srcLote, planting } = dragSource;
      if (srcLote !== loteId) {
        dragSource = null;
        return;
      }

      if (hasConflict(loteId, year, week, planting.vegetal, planting)) {
        td.classList.add('conflict');
        setTimeout(() => td.classList.remove('conflict'), 800);
        dragSource = null;
        return;
      }

      if (isConsecutiveBroccoli(loteId, year, week, planting.vegetal, planting)) {
        alert('⚠️ ALERTA DE MONOCULTIVO:\nMoviendo BROCCOLI inmediatamente después de otro cultivo de Broccoli en este lote.');
      }

      planting.year = year;
      planting.weekInYear = week;
      dragSource = null;
      render();
    };
  });
}

// Llenar selectores de vegetales
const optionsVeg = '<option value="">Todos los vegetales</option>' + 
  VEG_ORDER.map(v => `<option value="${v}">${v}</option>`).join('');

document.getElementById('summaryVegFilter').innerHTML = optionsVeg;
document.getElementById('loteVegFilter').innerHTML = '<option value="">Ver Todos</option>' + 
  VEG_ORDER.map(v => `<option value="${v}">${v}</option>`).join('');

document.getElementById('summaryVegFilter').onchange = render;
document.getElementById('loteVegFilter').onchange = render;
document.getElementById('splitBtn').onclick = openSplitModal;

document.getElementById('exportBtn').onclick = () => {
  const rows = [['Finca','Lote','Año','Semana del Año','Vegetal','Produccion']];
  LOTES.forEach(l => {
    (plantings[l.id]||[]).forEach(p => {
      const c = CICLOS[p.vegetal];
      if (!c) return;
      for(let rel=0; rel<c.duracion; rel++){
        let abs = absWeek(p.year, p.weekInYear) + rel;
        let yr = 2020 + Math.floor(abs / 52);
        let wk = (abs % 52);
        if (wk === 0) { wk = 52; yr -= 1; }
        
        const val = harvestValue(p, yr, wk, l.area);
        if(val > 0){
          rows.push([l.finca, l.nombre, yr, wk, p.vegetal, Math.round(val)]);
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

initYearSelectorUI();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
