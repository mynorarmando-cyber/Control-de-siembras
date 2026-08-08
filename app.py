import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Planificación de Siembras — V10.1",
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
    --ejote-bg: #ddebf7; --ejote-fg: #1f4e79;
    --broccoli-bg: #e2efda; --broccoli-fg: #375623;
    --grano-bg: #fce4d6; --grano-fg: #833c00;
    --china-bg: #e4dfec; --china-fg: #5f3f7a;
    --dulce-bg: #fff2cc; --dulce-fg: #7f6000;
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
  
  /* Ancho ajustado a 45px por columna */
  th.lotehead { position:sticky; top:0; z-index:8; background:#f0efe8; width:45px; min-width:45px; max-width:45px;
    font-weight:700; font-size:10px; padding:2px 1px; overflow:hidden; }
  th.lotehead .sub { font-size:8.5px; font-weight:normal; color:var(--muted); }
  
  tr.year-divider td { background: var(--forest) !important; color:#fff !important; font-weight:700; font-size:11px; text-align:left; padding:3px 8px; position:sticky; left:0; z-index:9; }

  td.weekcell { position:sticky; left:0; z-index:7; background:#f0efe8; width:50px; min-width:50px; font-weight:600; font-size:10px; height:24px; }
  td.sumcell { position:sticky; left:50px; z-index:7; background:#e4f0ec; width:95px; min-width:95px; font-weight:700; font-size:10px; height:24px; border-right:2px solid var(--forest); color:var(--forest); }
  
  td.cell { width:45px; min-width:45px; max-width:45px; height:24px; cursor:pointer; font-size:8.5px; position:relative; user-select:none; overflow:hidden; }
  td.cell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; z-index:5; }
  td.cell.planted { font-weight:700; cursor:grab; }
  td.cell.dragover { outline:2px dashed var(--forest); outline-offset:-2px; background:#e2f0d9 !important; }

  .cell-val { display:block; width:100%; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; font-size:8px; line-height:24px; }

  .popup { position:absolute; z-index:50; background:#fff; border:1px solid var(--line); border-radius:6px;
    box-shadow:0 6px 20px rgba(0,0,0,.18); padding:6px; min-width:140px; }
  .popup button { display:block; width:100%; text-align:left; padding:5px 7px; border:none; background:none;
    cursor:pointer; border-radius:4px; font-size:11px; margin-bottom:2px; }
  .popup button:hover { background:#f0efe8; }
  .popup .danger { color: var(--alert); font-weight:600; border-bottom:1px solid var(--line); margin-bottom:4px; padding-bottom:4px; }
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>Planificación de Siembras — Columnas Angostas (45px)</h1>
  </header>

  <div class="toolbar">
    <div class="tool-section">
      <div class="tabs" id="fincaTabs"></div>
    </div>

    <div class="tool-divider"></div>

    <div class="tool-section">
      <div class="field-group">
        <label>📊 Resumen General (Todas)</label>
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

      var LOTES = [];
      var areaSeed = [1.0, 1.2, 0.8, 1.5, 1.1, 0.9, 1.3, 1.4];
      var idCounter = 1;
      FINCAS.forEach(function(f) {
        for (var i = 1; i <= 30; i++) {
          LOTES.push({
            id: f + '-' + i,
            finca: f,
            nombre: f + '-' + i,
            area: areaSeed[idCounter % areaSeed.length]
          });
          idCounter++;
        }
      });

      var plantings = {};
      plantings['NP-1'] = [{year: 2026, weekInYear: 1, vegetal: 'Broccoli'}, {year: 2026, weekInYear: 20, vegetal: 'Broccoli'}];
      plantings['NP-5'] = [{year: 2026, weekInYear: 4, vegetal: 'Ejote'}];
      plantings['CH-1'] = [{year: 2026, weekInYear: 1, vegetal: 'China'}];
      plantings['TM-12'] = [{year: 2026, weekInYear: 2, vegetal: 'China'}];

      var dragSource = null;
      var activePopup = null;

      function closePopup() {
        if (activePopup) { activePopup.remove(); activePopup = null; }
      }

      function absWeek(year, weekInYear) {
        return (year - 2020) * 52 + weekInYear;
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
        LOTES.forEach(function(l) {
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

        var activeLotes = LOTES.filter(function(l){ return l.finca === currentFinca; });
        var wrap = document.getElementById('gridWrap');

        var areaUsoTotal = 0;
        var prodTotal = 0;

        var sumColHeader = selectedSummaryVeg ? 'Total ' + selectedSummaryVeg : 'Total Fincas';

        var tableHtml = '<table class="grid"><thead><tr><th class="corner">Sem.</th><th class="sumhead">' + sumColHeader + '</th>';
        
        activeLotes.forEach(function(l) {
          tableHtml += '<th class="lotehead">' + l.nombre + '<div class="sub">' + l.area + 'ha</div></th>';
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
                var act = findActive(l.id, year, w);
                var cellStyle = '';
                var text = '';
                var isHiddenByLoteFilter = false;

                if (act) {
                  if (selectedLoteVeg && act.vegetal !== selectedLoteVeg) {
                    isHiddenByLoteFilter = true;
                  } else {
                    cellStyle = getVegetableStyle(act.vegetal);
                    if (act.year === year && act.weekInYear === w) {
                      text = act.vegetal;
                    }
                    
                    var val = harvestValue(act, year, w, l.area);
                    if (val > 0) {
                      text = Math.round(val); // Número entero directo (ej. 3500)
                      prodTotal += val;
                    }
                    if (w === 1 || (act.year === year && act.weekInYear === w)) areaUsoTotal += l.area;
                  }
                }

                tableHtml += '<td class="cell ' + (act && !isHiddenByLoteFilter ? 'planted' : '') + '" style="' + cellStyle + '" ' +
                  'draggable="' + (act ? 'true' : 'false') + '" ' +
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
        var cells = document.querySelectorAll('td.cell');

        cells.forEach(function(cell) {
          cell.onclick = function(e) {
            e.stopPropagation();
            closePopup();

            var loteId = cell.dataset.lote;
            var yr = parseInt(cell.dataset.year);
            var wk = parseInt(cell.dataset.week);
            var act = findActive(loteId, yr, wk);

            var pop = document.createElement('div');
            pop.className = 'popup';
            pop.style.left = Math.min(e.pageX - document.getElementById('gridWrap').scrollLeft, window.innerWidth - 160) + 'px';
            pop.style.top = (e.pageY - document.getElementById('gridWrap').scrollTop) + 'px';

            if (act) {
              var btnDel = document.createElement('button');
              btnDel.className = 'danger';
              btnDel.textContent = 'Eliminar ' + act.vegetal;
              btnDel.onclick = function() {
                plantings[loteId] = (plantings[loteId] || []).filter(function(p){ return p !== act; });
                render();
              };
              pop.appendChild(btnDel);
            }

            VEG_ORDER.forEach(function(v) {
              var btn = document.createElement('button');
              btn.textContent = (act ? 'Cambiar a ' : 'Sembrar ') + v;
              btn.onclick = function() {
                if (act) {
                  act.vegetal = v;
                } else {
                  if (!plantings[loteId]) plantings[loteId] = [];
                  plantings[loteId].push({ year: yr, weekInYear: wk, vegetal: v });
                }
                render();
              };
              pop.appendChild(btn);
            });

            document.getElementById('gridWrap').appendChild(pop);
            activePopup = pop;
          };

          cell.ondragstart = function(e) {
            var loteId = cell.dataset.lote;
            var yr = parseInt(cell.dataset.year);
            var wk = parseInt(cell.dataset.week);
            var act = findActive(loteId, yr, wk);
            if (act) {
              dragSource = { loteId: loteId, planting: act };
              e.dataTransfer.setData('text/plain', '');
            } else {
              e.preventDefault();
            }
          };

          cell.ondragover = function(e) {
            e.preventDefault();
            cell.classList.add('dragover');
          };

          cell.ondragleave = function() {
            cell.classList.remove('dragover');
          };

          cell.ondrop = function(e) {
            e.preventDefault();
            cell.classList.remove('dragover');
            if (!dragSource) return;

            var targetYr = parseInt(cell.dataset.year);
            var targetWk = parseInt(cell.dataset.week);

            dragSource.planting.year = targetYr;
            dragSource.planting.weekInYear = targetWk;

            dragSource = null;
            render();
          };
        });
      }

      document.getElementById('gridWrap').onclick = function() {
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
