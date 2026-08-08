import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Planificación de Siembras — V10.11",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
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
<title>Planificación de Siembras</title>
<style>
  :root {
    --ink: #1b2e26;
    --paper: #f6f5f0;
    --panel: #ffffff;
    --line: #dcd8cc;
    --forest: #1f4e3d;
    --muted: #6b7268;
    --alert: #b3261e;
    --gap-bg: #fdf2f2;
    --split-head: #d9edf7;
    --split-head-fg: #1d394a;
    --ejote-bg: #ddebf7; --ejote-fg: #1f4e79;
    --broccoli-bg: #e2efda; --broccoli-fg: #375623;
    --grano-bg: #fce4d6; --grano-fg: #833c00;
    --china-bg: #e4dfec; --china-fg: #5f3f7a;
    --dulce-bg: #fff2cc; --dulce-fg: #7f6000;
    --inherited-bg: #fff3cd; --inherited-fg: #856404; --inherited-border: #ffeeba;
  }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; background: var(--paper); color: var(--ink);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 12px; height: 100%; overflow: hidden; }
  #app { display:flex; flex-direction:column; height:100vh; }

  header { background: var(--forest); color: #fff; padding: 10px 18px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }
  header h1 { font-size: 16px; margin:0; font-weight:600; }

  .toolbar { background: var(--panel); border-bottom:1px solid var(--line); padding:8px 14px;
    display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  
  .tool-section { display:flex; align-items:center; gap:6px; }
  .tool-divider { width:1px; height:24px; background:var(--line); margin:0 2px; }
  
  .tabs { display:flex; gap:3px; }
  .tab { padding:4px 9px; border-radius:5px; border:1px solid var(--line); background:#fff;
    cursor:pointer; font-size:11px; font-weight:600; }
  .tab.active { background: var(--forest); color:#fff; border-color:var(--forest); }
  
  .field-group { display:flex; flex-direction:column; gap:1px; }
  .field-group label { font-size:9.5px; font-weight:700; text-transform:uppercase; color:var(--forest); }
  
  .field select { padding:3px 6px; border:1px solid var(--line);
    border-radius:5px; font-size:11px; background:#fff; color: var(--ink); font-weight:500; }

  .multi-year-selector { display:flex; gap:6px; align-items:center; background:#f0efe8; padding:3px 6px; border-radius:5px; border:1px solid var(--line); }
  .multi-year-selector label { font-size:10.5px; cursor:pointer; display:flex; align-items:center; gap:2px; }

  .stat { background:#f0efe8; border:1px solid var(--line); border-radius:6px; padding:3px 8px; }
  .stat b { font-size:12px; color: var(--forest); display:block; }
  .stat span { font-size:9px; color:var(--muted); text-transform:uppercase; }

  .grid-wrap { flex:1; overflow:auto; position:relative; background: var(--panel); min-height: 500px; }
  table.grid { border-collapse:collapse; table-layout:fixed; width: max-content; }
  table.grid th, table.grid td { border:1px solid #ece9de; text-align:center; padding:0; }
  
  th.corner { position:sticky; top:0; left:0; z-index:10; background:#e8e5d8; width:50px; min-width:50px; height:45px; font-size:10px; }
  th.sumhead { position:sticky; top:0; left:50px; z-index:10; background:#cbe0d7; color:var(--forest); width:95px; min-width:95px; font-size:10px; font-weight:700; border-right:2px solid var(--forest); }
  
  th.lotehead { position:sticky; top:0; z-index:8; background:#f0efe8; width:45px; min-width:45px; max-width:45px;
    font-weight:700; font-size:10px; padding:2px 1px; overflow:hidden; }
  th.lotehead.is-split { background: var(--split-head); color: var(--split-head-fg); border-bottom: 2px solid #bce8f1; }
  th.lotehead .sub { font-size:8.5px; font-weight:normal; color:var(--muted); display:flex; align-items:center; justify-content:center; gap:2px; }
  th.lotehead.is-split .sub { color: #31708f; }
  
  .expand-btn { background:none; border:none; cursor:pointer; font-size:9px; padding:0 2px; color:var(--forest); font-weight:bold; }
  .expand-btn:hover { color:#000; }

  tr.year-divider td { background: var(--forest) !important; color:#fff !important; font-weight:700; font-size:11px; text-align:left; padding:3px 8px; position:sticky; left:0; z-index:9; }

  td.weekcell { position:sticky; left:0; z-index:7; background:#f0efe8; width:50px; min-width:50px; font-weight:600; font-size:10px; height:24px; }
  td.sumcell { position:sticky; left:50px; z-index:7; background:#e4f0ec; width:95px; min-width:95px; font-weight:700; font-size:10px; height:24px; border-right:2px solid var(--forest); color:var(--forest); }
  
  td.cell { width:45px; min-width:45px; max-width:45px; height:24px; cursor:pointer; font-size:8.5px; position:relative; user-select:none; overflow:hidden; }
  td.cell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; z-index:5; }
  td.cell.planted { font-weight:700; cursor:grab; }
  td.cell.inherited-occupancy { background-color: var(--inherited-bg); color: var(--inherited-fg); font-style: italic; border: 1px dashed var(--inherited-border); }
  td.cell.long-gap { background-color: var(--gap-bg); }
  td.cell.dragover { outline:2px dashed var(--forest); outline-offset:-2px; background:#e2f0d9 !important; }
  td.cell.drag-error { outline:2px dashed var(--alert) !important; background:#fbeae8 !important; cursor:not-allowed !important; }

  .cell-val { display:block; width:100%; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; font-size:8px; line-height:24px; }

  .popup { 
    position: fixed; 
    z-index: 9999; 
    background: #ffffff; 
    border: 1px solid var(--forest); 
    border-radius: 6px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22); 
    padding: 6px; 
    width: 180px;
    animation: fadeIn 0.1s ease-out;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
  .popup button { display:block; width:100%; text-align:left; padding:6px 8px; border:none; background:none;
    cursor:pointer; border-radius:4px; font-size:11px; margin-bottom:2px; font-weight:500; }
  .popup button:hover:not(:disabled) { background:#e8f0ec; color: var(--forest); }
  .popup button:disabled { opacity: 0.4; cursor: not-allowed; }
  .popup .danger { color: var(--alert); font-weight:700; border-bottom:1px solid var(--line); margin-bottom:4px; padding-bottom:4px; }
  .popup .action-btn { color: var(--forest); font-weight:700; border-top:1px solid var(--line); margin-top:4px; padding-top:4px; }
  .popup .msg-occupied { font-size: 10px; color: var(--alert); padding: 4px 6px; font-weight: 600; text-align: center; background: #fbeae8; border-radius: 4px; margin-bottom: 4px; }
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>Planificación de Siembras — Alertas Cruzadas A/B (V10.11)</h1>
  </header>

  <div class="toolbar">
    <div class="tool-section">
      <div class="tabs" id="fincaTabs"></div>
    </div>

    <div class="tool-divider"></div>

    <div class="tool-section">
      <div class="field-group">
        <label>📊 Resumen General</label>
        <div class="field">
          <select id="summaryVegFilter"><option value="">Todos</option></select>
        </div>
      </div>
    </div>

    <div class="tool-divider"></div>

    <div class="tool-section">
      <div class="field-group">
        <label>🌱 Matriz Planificación</label>
        <div class="field">
          <select id="loteVegFilter"><option value="">Ver Todos</option></select>
        </div>
      </div>
    </div>

    <div class="tool-divider"></div>

    <div class="tool-section">
      <div class="field-group">
        <label>📅 Años</label>
        <div class="multi-year-selector" id="yearCheckboxes"></div>
      </div>
    </div>

    <div class="tool-section" style="margin-left:auto;">
      <div class="stat"><b id="statArea">0</b><span>Área (ha)</span></div>
      <div class="stat"><b id="statProd">0</b><span>Prod. Total</span></div>
    </div>
  </div>

  <div class="grid-wrap" id="gridWrap"></div>
</div>

<script>
(function() {
  function init() {
    try {
      var AVAILABLE_YEARS = [2025, 2026, 2027, 2028];
      var selectedYears = [2026, 2027];

      var CICLOS = {
        Ejote:    { duracion: 12, cosechas: [[10,0.35],[11,0.42],[12,0.23]], rendimiento: 11500, color:'ejote' },
        Broccoli: { duracion: 15, cosechas: [[10,0.10],[11,0.20],[12,0.17],[13,0.10],[14,0.23],[15,0.20]], rendimiento: 8000, color:'broccoli' },
        Grano:    { duracion: 14, cosechas: [[11,0.30],[12,0.36],[13,0.24],[14,0.10]], rendimiento: 8500, color:'grano' },
        China:    { duracion: 13, cosechas: [[10,0.11],[11,0.45],[12,0.37],[13,0.07]], rendimiento: 7500, color:'china' },
        Dulce:    { duracion: 14, cosechas: [[11,0.10],[12,0.20],[13,0.41],[14,0.29]], rendimiento: 10000, color:'dulce' }
      };

      function getVegetableStyle(vegName) {
        var c = CICLOS[vegName];
        if (c && c.color) {
          return 'background:var(--' + c.color + '-bg);color:var(--' + c.color + '-fg);';
        }
        return 'background: #e0e0e0; color: #000;';
      }

      var VEG_ORDER = Object.keys(CICLOS);
      var FINCAS = ['NP','CH','TM','PV','SM'];

      var BASE_LOTES = [];
      var areaSeed = [1.0, 1.2, 0.8, 1.5, 1.1, 0.9, 1.3, 1.4];
      var idCounter = 1;
      FINCAS.forEach(function(f) {
        for (var i = 1; i <= 30; i++) {
          BASE_LOTES.push({
            id: f + '-' + i,
            finca: f,
            nombre: f + '-' + i,
            area: areaSeed[idCounter % areaSeed.length]
          });
          idCounter++;
        }
      });

      var expandedLots = {};
      var plantings = {};
      plantings['NP-1'] = [{year: 2026, weekInYear: 1, vegetal: 'Broccoli'}];
      plantings['NP-1A'] = [{year: 2026, weekInYear: 20, vegetal: 'Ejote'}];
      plantings['NP-1B'] = [{year: 2026, weekInYear: 20, vegetal: 'China'}];
      plantings['NP-5'] = [{year: 2026, weekInYear: 4, vegetal: 'Ejote'}];
      plantings['CH-1'] = [{year: 2026, weekInYear: 1, vegetal: 'China'}];

      var dragSource = null;
      var activePopup = null;

      function closePopup() {
        if (activePopup) { activePopup.remove(); activePopup = null; }
      }

      function absWeek(year, weekInYear) {
        return (year - 2020) * 52 + weekInYear;
      }

      function getActiveLotesForFinca(fincaName) {
        var result = [];
        var fincaBase = BASE_LOTES.filter(function(l) { return l.finca === fincaName; });
        
        fincaBase.forEach(function(l) {
          if (expandedLots[l.id]) {
            var halfArea = Number((l.area / 2).toFixed(2));
            result.push({ id: l.id + 'A', finca: fincaName, nombre: l.id + 'A', area: halfArea, parentId: l.id, isSplit: true });
            result.push({ id: l.id + 'B', finca: fincaName, nombre: l.id + 'B', area: halfArea, parentId: l.id, isSplit: true });
          } else {
            result.push({ id: l.id, finca: fincaName, nombre: l.nombre, area: l.area, parentId: null, isSplit: false });
          }
        });
        return result;
      }

      function getAllActiveLotesFlat() {
        var all = [];
        FINCAS.forEach(function(f) {
          all = all.concat(getActiveLotesForFinca(f));
        });
        return all;
      }

      function findActive(loteId, year, weekInYear){
        var list = plantings[loteId] || [];
        var currentAbs = absWeek(year, weekInYear);
        for (var i = 0; i < list.length; i++){
          var p = list[i];
          var c = CICLOS[p.vegetal];
          if (!c) continue;
          var startAbs = absWeek(p.year, p.weekInYear);
          if (currentAbs >= startAbs && currentAbs < startAbs + c.duracion) return p;
        }
        return null;
      }

      // Ocupación detallada bidireccional y jerárquica:
      // - Si es A o B: Muestra su siembra directa, O si el Lote Principal completo tiene siembra activa en esa semana (bloqueando A y B).
      // - Si es el Lote Principal: Muestra su siembra directa, O si A o B tienen actividad.
      function getDetailedOccupancy(loteId, year, weekInYear) {
        // 1. Revisión directa en el propio ID
        var direct = findActive(loteId, year, weekInYear);
        if (direct) {
          return { planting: direct, type: 'direct', sourceId: loteId };
        }

        // 2. Si es Lote Principal, verificar si A o B están activos
        if (!loteId.endsWith('A') && !loteId.endsWith('B')) {
          var subA = findActive(loteId + 'A', year, weekInYear);
          if (subA) return { planting: subA, type: 'inherited', sourceId: loteId + 'A' };
          var subB = findActive(loteId + 'B', year, weekInYear);
          if (subB) return { planting: subB, type: 'inherited', sourceId: loteId + 'B' };
        }

        // 3. Si es un sub-lote (A o B), verificar si el Lote Principal completo está ocupado
        if (loteId.endsWith('A') || loteId.endsWith('B')) {
          var baseId = loteId.slice(0, -1);
          var parentAct = findActive(baseId, year, weekInYear);
          if (parentAct) return { planting: parentAct, type: 'inherited', sourceId: baseId };
        }

        return null;
      }

      function canPlant(loteId, year, weekInYear, vegName, ignorePlanting) {
        var cycle = CICLOS[vegName];
        if (!cycle) return false;

        var startAbs = absWeek(year, weekInYear);
        var endAbs = startAbs + cycle.duracion - 1;

        var checkIds = [loteId];
        if (!loteId.endsWith('A') && !loteId.endsWith('B')) {
          checkIds.push(loteId + 'A', loteId + 'B');
        } else if (loteId.endsWith('A') || loteId.endsWith('B')) {
          var baseId = loteId.slice(0, -1);
          checkIds.push(baseId);
        }

        for (var r = 0; r < checkIds.length; r++) {
          var checkId = checkIds[r];
          var list = plantings[checkId] || [];
          for (var i = 0; i < list.length; i++) {
            var p = list[i];
            if (ignorePlanting && p === ignorePlanting && checkId === loteId) continue;

            var existingStart = absWeek(p.year, p.weekInYear);
            var existingEnd = existingStart + CICLOS[p.vegetal].duracion - 1;

            if (startAbs <= existingEnd && endAbs >= existingStart) {
              return false;
            }
          }
        }
        return true;
      }

      function harvestValue(planting, year, weekInYear, area){
        var c = CICLOS[planting.vegetal];
        if (!c) return 0;
        var currentAbs = absWeek(year, weekInYear);
        var startAbs = absWeek(planting.year, planting.weekInYear);
        var rel = currentAbs - startAbs + 1;
        var cosecha = c.cosechas.find(function(item){ return item[0] === rel; });
        return cosecha ? area * c.rendimiento * cosecha[1] : 0;
      }

      function getTotalHarvestAllFincas(year, weekInYear, targetVeg) {
        var sum = 0;
        var activeLots = getAllActiveLotesFlat();
        activeLots.forEach(function(l) {
          var list = plantings[l.id] || [];
          list.forEach(function(p) {
            if (!targetVeg || p.vegetal === targetVeg) {
              sum += harvestValue(p, year, weekInYear, l.area);
            }
          });
        });
        return sum;
      }

      var currentFinca = 'NP';
      var selectedSummaryVeg = '';
      var selectedLoteVeg = '';

      function render(){
        closePopup();
        var summarySelect = document.getElementById('summaryVegFilter');
        var loteSelect = document.getElementById('loteVegFilter');
        selectedSummaryVeg = summarySelect ? summarySelect.value : '';
        selectedLoteVeg = loteSelect ? loteSelect.value : '';

        var tabsWrap = document.getElementById('fincaTabs');
        tabsWrap.innerHTML = FINCAS.map(function(f){ 
          return '<div class="tab ' + (currentFinca===f?'active':'') + '" data-finca="' + f + '">' + f + '</div>';
        }).join('');

        tabsWrap.querySelectorAll('.tab').forEach(function(btn) {
          btn.onclick = function() {
            currentFinca = btn.dataset.finca;
            render();
          };
        });

        var activeLotes = getActiveLotesForFinca(currentFinca);
        var wrap = document.getElementById('gridWrap');

        var areaUsoTotal = 0;
        var prodTotal = 0;

        var sumColHeader = selectedSummaryVeg ? 'Total ' + selectedSummaryVeg : 'Total Fincas';

        var tableHtml = '<table class="grid"><thead><tr><th class="corner">Sem.</th><th class="sumhead">' + sumColHeader + '</th>';
        
        activeLotes.forEach(function(l) {
          var splitClass = l.isSplit ? ' is-split' : '';
          var baseId = l.isSplit ? l.parentId : l.id;
          
          tableHtml += '<th class="lotehead' + splitClass + '" data-lotid="' + l.id + '">' + 
            l.nombre + 
            '<div class="sub">' +
              (!l.isSplit ? '<button class="expand-btn" data-baseid="' + baseId + '" title="Desplegar A y B">▶</button>' : '<button class="expand-btn" data-baseid="' + baseId + '" title="Unificar Lote">▼</button>') +
              l.area + 'ha' +
            '</div>' +
          '</th>';
        });
        tableHtml += '</tr></thead><tbody>';

        if (selectedYears.length === 0) {
          tableHtml += '<tr><td colspan="' + (activeLotes.length + 2) + '" style="padding:15px;color:var(--muted);">Seleccione al menos un año.</td></tr>';
        } else {
          selectedYears.forEach(function(year) {
            tableHtml += '<tr class="year-divider"><td colspan="' + (activeLotes.length + 2) + '">Año ' + year + '</td></tr>';

            for (var w = 1; w <= 52; w++) {
              var globalHarvest = getTotalHarvestAllFincas(year, w, selectedSummaryVeg);
              var globalHarvestTxt = globalHarvest > 0 ? Math.round(globalHarvest).toLocaleString('es-GT') : '-';

              tableHtml += '<tr><td class="weekcell">' + w + '</td><td class="sumcell">' + globalHarvestTxt + '</td>';

              activeLotes.forEach(function(l) {
                var occupancy = getDetailedOccupancy(l.id, year, w);
                var cellStyle = '';
                var text = '';
                var isHiddenByLoteFilter = false;
                var cellClasses = ['cell'];

                if (occupancy) {
                  var act = occupancy.planting;
                  if (selectedLoteVeg && act.vegetal !== selectedLoteVeg) {
                    isHiddenByLoteFilter = true;
                  } else {
                    if (occupancy.type === 'direct') {
                      cellStyle = getVegetableStyle(act.vegetal);
                      cellClasses.push('planted');
                      if (act.year === year && act.weekInYear === w) {
                        text = act.vegetal;
                      }
                      var val = harvestValue(act, year, w, l.area);
                      if (val > 0) {
                        text = Math.round(val);
                        prodTotal += val;
                      }
                      if (w === 1 || (act.year === year && act.weekInYear === w)) areaUsoTotal += l.area;
                    } else {
                      // Ocupación heredada (ej. Lote principal ocupado bloquea A/B, o A/B ocupado bloquea Principal)
                      cellClasses.push('inherited-occupancy');
                      text = '[' + occupancy.sourceId.slice(-2) + ']';
                      if (w === 1 || (!l.isSplit && (act.year === year && act.weekInYear === w))) {
                        areaUsoTotal += l.area;
                      }
                    }
                  }
                }

                var isDraggable = occupancy && occupancy.type === 'direct' && occupancy.planting.year === year && occupancy.planting.weekInYear === w;

                tableHtml += '<td class="' + cellClasses.join(' ') + '" style="' + cellStyle + '" ' +
                  'draggable="' + (isDraggable ? 'true' : 'false') + '" ' +
                  'data-lote="' + l.id + '" data-year="' + year + '" data-week="' + w + '">' +
                  (isHiddenByLoteFilter ? '' : '<span class="cell-val">' + text + '</span>') +
                '</td>';
              });

              tableHtml += '</tr>';
            }
          });
        }

        tableHtml += '</tbody></table>';
        wrap.innerHTML = tableHtml;

        document.getElementById('statArea').textContent = areaUsoTotal.toFixed(1);
        document.getElementById('statProd').textContent = Math.round(prodTotal).toLocaleString('es-GT');

        bindGridEvents();
      }

      function bindGridEvents() {
        document.querySelectorAll('.expand-btn').forEach(function(btn) {
          btn.onclick = function(e) {
            e.stopPropagation();
            var baseId = btn.dataset.baseid;
            if (expandedLots[baseId]) {
              delete expandedLots[baseId];
            } else {
              expandedLots[baseId] = true;
            }
            render();
          };
        });

        var cells = document.querySelectorAll('td.cell');

        cells.forEach(function(cell) {
          cell.onclick = function(e) {
            e.stopPropagation();
            closePopup();

            var loteId = cell.dataset.lote;
            var yr = parseInt(cell.dataset.year);
            var wk = parseInt(cell.dataset.week);
            var occupancy = getDetailedOccupancy(loteId, yr, wk);
            var act = occupancy ? occupancy.planting : null;

            var pop = document.createElement('div');
            pop.className = 'popup';

            var rect = cell.getBoundingClientRect();
            var popWidth = 180;
            var popHeight = 220;

            var left = rect.right + 4;
            if (left + popWidth > window.innerWidth) {
              left = rect.left - popWidth - 4;
            }

            var top = rect.top;
            if (top + popHeight > window.innerHeight) {
              top = window.innerHeight - popHeight - 10;
            }

            pop.style.left = left + 'px';
            pop.style.top = top + 'px';

            if (occupancy) {
              if (occupancy.type === 'direct') {
                var btnDel = document.createElement('button');
                btnDel.className = 'danger';
                btnDel.textContent = '❌ Eliminar ' + act.vegetal;
                btnDel.onclick = function() {
                  plantings[loteId] = (plantings[loteId] || []).filter(function(p){ return p !== act; });
                  render();
                };
                pop.appendChild(btnDel);
              } else {
                var msgInherited = document.createElement('div');
                msgInherited.className = 'msg-occupied';
                msgInherited.textContent = 'Bloqueado por ' + occupancy.sourceId;
                pop.appendChild(msgInherited);
              }
            }

            VEG_ORDER.forEach(function(v) {
              var isStartWeek = act && occupancy.type === 'direct' && act.year === yr && act.weekInYear === wk;
              var isAllowed = canPlant(loteId, yr, wk, v, isStartWeek ? act : null);

              var btn = document.createElement('button');
              btn.textContent = (isStartWeek ? 'Cambiar a ' : '🌱 ') + v;
              btn.disabled = !isAllowed;

              if (!isAllowed) {
                btn.title = "Conflicto: El lote o sus dependencias están ocupadas";
              }

              btn.onclick = function() {
                if (!isAllowed) return;
                if (isStartWeek) {
                  act.vegetal = v;
                } else {
                  if (!plantings[loteId]) plantings[loteId] = [];
                  plantings[loteId].push({ year: yr, weekInYear: wk, vegetal: v });
                }
                render();
              };
              pop.appendChild(btn);
            });

            document.body.appendChild(pop);
            activePopup = pop;
          };

          cell.ondragstart = function(e) {
            var loteId = cell.dataset.lote;
            var yr = parseInt(cell.dataset.year);
            var wk = parseInt(cell.dataset.week);
            var occupancy = getDetailedOccupancy(loteId, yr, wk);
            
            if (occupancy && occupancy.type === 'direct' && occupancy.planting.year === yr && occupancy.planting.weekInYear === wk) {
              dragSource = { loteId: loteId, planting: occupancy.planting };
              e.dataTransfer.setData('text/plain', '');
            } else {
              e.preventDefault();
            }
          };

          cell.ondragover = function(e) {
            e.preventDefault();
            if (!dragSource) return;

            var targetLote = cell.dataset.lote;
            var targetYr = parseInt(cell.dataset.year);
            var targetWk = parseInt(cell.dataset.week);

            var isValid = canPlant(targetLote, targetYr, targetWk, dragSource.planting.vegetal, dragSource.planting);

            if (isValid) {
              cell.classList.add('dragover');
              cell.classList.remove('drag-error');
            } else {
              cell.classList.add('drag-error');
              cell.classList.remove('dragover');
            }
          };

          cell.ondragleave = function() {
            cell.classList.remove('dragover');
            cell.classList.remove('drag-error');
          };

          cell.ondrop = function(e) {
            e.preventDefault();
            cell.classList.remove('dragover');
            cell.classList.remove('drag-error');
            if (!dragSource) return;

            var targetLote = cell.dataset.lote;
            var targetYr = parseInt(cell.dataset.year);
            var targetWk = parseInt(cell.dataset.week);

            var isValid = canPlant(targetLote, targetYr, targetWk, dragSource.planting.vegetal, dragSource.planting);

            if (isValid) {
              if (dragSource.loteId !== targetLote) {
                plantings[dragSource.loteId] = (plantings[dragSource.loteId] || []).filter(function(p){ return p !== dragSource.planting; });
                if (!plantings[targetLote]) plantings[targetLote] = [];
                plantings[targetLote].push(dragSource.planting);
              }

              dragSource.planting.year = targetYr;
              dragSource.planting.weekInYear = targetWk;
            }

            dragSource = null;
            render();
          };
        });
      }

      document.body.onclick = function(e) {
        if (activePopup && !activePopup.contains(e.target)) {
          closePopup();
        }
      };

      document.getElementById('gridWrap').onscroll = function() {
        closePopup();
      };

      var optionsVegSummary = '<option value="">Todos</option>' + 
        VEG_ORDER.map(function(v){ return '<option value="' + v + '">' + v + '</option>'; }).join('');
      
      var optionsVegLote = '<option value="">Ver Todos</option>' + 
        VEG_ORDER.map(function(v){ return '<option value="' + v + '">' + v + '</option>'; }).join('');

      document.getElementById('summaryVegFilter').innerHTML = optionsVegSummary;
      document.getElementById('loteVegFilter').innerHTML = optionsVegLote;

      document.getElementById('summaryVegFilter').onchange = render;
      document.getElementById('loteVegFilter').onchange = render;

      var container = document.getElementById('yearCheckboxes');
      container.innerHTML = AVAILABLE_YEARS.map(function(yr) {
        var isChecked = selectedYears.indexOf(yr) !== -1 ? 'checked' : '';
        return '<label><input type="checkbox" value="' + yr + '" ' + isChecked + '> ' + yr + '</label>';
      }).join('');

      container.querySelectorAll('input').forEach(function(chk) {
        chk.onchange = function() {
          selectedYears = Array.from(container.querySelectorAll('input:checked')).map(function(i){ return parseInt(i.value); }).sort();
          render();
        };
      });

      render();
    } catch (err) {
      document.getElementById('gridWrap').innerHTML = '<div style="color:red; padding:20px;"><b>Error de JavaScript:</b><br>' + err.message + '</div>';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
