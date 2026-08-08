import base64
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title='Cropplaner - Sistema Integral y Catálogos',
    layout='wide',
    initial_sidebar_state='collapsed',
)

st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Cargar datos de Siesa Plan.xlsx para los catálogos
@st.cache_data
def cargar_excel_siesa():
  excel_path = 'Siesa Plan.xlsx'
  df_rend = pd.read_excel(excel_path, sheet_name='Rendimientos', header=1)

  df_raw_curva = pd.read_excel(
      excel_path, sheet_name='Rendimiento por vegetal', header=None
  )
  header_row = df_raw_curva.iloc[1, 2:7].values
  df_curva = df_raw_curva.iloc[2:, [1, 2, 3, 4, 5, 6]].copy()
  df_curva.columns = ['Semana'] + list(header_row)
  df_curva['Semana'] = pd.to_numeric(df_curva['Semana'], errors='coerce')
  df_curva = df_curva.dropna(subset=['Semana']).set_index('Semana')

  return df_rend, df_curva


df_rendimientos, df_curvas = cargar_excel_siesa()

# --- MENÚ PRINCIPAL DE NAVEGACIÓN ---
menu_principal = st.selectbox(
    'Seleccione el Módulo de Cropplaner',
    [
        '🌱 Cropplaner Principal (V11.0)',
        '📂 Catálogo de Fincas y Lotes (Áreas Reales)',
        '📊 Catálogo de Rendimientos y Vegetales (Siesa Plan)',
    ],
    label_visibility='collapsed',
)

if menu_principal == '🌱 Cropplaner Principal (V11.0)':
  html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <title>Planificación de Siembras - V11.0</title>
    <style>
      :root {
        --ink: #1b2e26; --paper: #f6f5f0; --panel: #ffffff; --line: #dcd8cc;
        --forest: #1f4e3d; --muted: #6b7268; --alert: #b3261e; --gap-bg: #fbeae8;
        --split-head: #d9edf7; --split-head-fg: #1d394a;
        --ejote-bg: #ddebf7; --ejote-fg: #1f4e79;
        --broccoli-bg: #e2efda; --broccoli-fg: #375623;
        --grano-bg: #fce4d6; --grano-fg: #833c00;
        --china-bg: #e4dfec; --china-fg: #5f3f7a;
        --dulce-bg: #fff2cc; --dulce-fg: #7f6000;
      }
      * { box-sizing: border-box; }
      html, body { margin:0; padding:0; background: var(--paper); color: var(--ink);
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 12px; height: 100vh; overflow: hidden; }
      #app { display:flex; flex-direction:column; height:100vh; width:100vw; }
      header { background: var(--forest); color: #fff; padding: 8px 16px; display:flex; align-items:center; justify-content:space-between; }
      header h1 { font-size: 15px; margin:0; font-weight:600; }
      .toolbar { background: var(--panel); border-bottom:1px solid var(--line); padding:6px 12px;
        display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
      .tool-section { display:flex; align-items:center; gap:6px; }
      .tool-divider { width:1px; height:22px; background:var(--line); margin:0 2px; }
      .tabs { display:flex; gap:3px; }
      .tab { padding:4px 10px; border-radius:4px; border:1px solid var(--line); background:#fff;
        cursor:pointer; font-size:11px; font-weight:600; }
      .tab.active { background: var(--forest); color:#fff; border-color:var(--forest); }
      .field-group { display:flex; flex-direction:column; gap:1px; }
      .field-group label { font-size:9px; font-weight:700; text-transform:uppercase; color:var(--forest); }
      .field select { padding:2px 4px; border:1px solid var(--line); border-radius:4px; font-size:11px; background:#fff; }
      .stat { background:#f0efe8; border:1px solid var(--line); border-radius:4px; padding:2px 6px; text-align:right; }
      .stat b { font-size:11px; color: var(--forest); display:block; }
      .stat span { font-size:8.5px; color:var(--muted); text-transform:uppercase; }
      .grid-wrap { flex:1; overflow:auto; position:relative; background: var(--panel); width:100%; height: calc(100vh - 90px); }
      table.grid { border-collapse:collapse; table-layout:fixed; width: max-content; }
      table.grid th, table.grid td { border:1px solid #ece9de; text-align:center; padding:0; }
      th.corner { position:sticky; top:0; left:0; z-index:10; background:#e8e5d8; width:45px; min-width:45px; height:40px; font-size:9.5px; }
      th.sumhead { position:sticky; top:0; left:45px; z-index:10; background:#cbe0d7; color:var(--forest); width:85px; min-width:85px; font-size:9.5px; font-weight:700; border-right:2px solid var(--forest); }
      th.lotehead { position:sticky; top:0; z-index:8; background:#f0efe8; width:42px; min-width:42px; max-width:42px; font-weight:700; font-size:9.5px; padding:2px 1px; }
      th.lotehead .sub { font-size:8px; font-weight:normal; color:var(--muted); }
      tr.year-divider td { background: var(--forest) !important; color:#fff !important; font-weight:700; font-size:10.5px; text-align:left; padding:3px 8px; position:sticky; left:0; z-index:9; }
      td.weekcell { position:sticky; left:0; z-index:7; background:#f0efe8; width:45px; min-width:45px; font-weight:600; font-size:9.5px; height:22px; }
      td.sumcell { position:sticky; left:45px; z-index:7; background:#e4f0ec; width:85px; min-width:85px; font-weight:700; font-size:9.5px; height:22px; border-right:2px solid var(--forest); color:var(--forest); }
      td.cell { width:42px; min-width:42px; max-width:42px; height:22px; cursor:pointer; font-size:8px; position:relative; user-select:none; }
      td.cell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; z-index:5; }
      td.cell.Ejote { background-color: var(--ejote-bg); color: var(--ejote-fg); font-weight:700; }
      td.cell.Broccoli { background-color: var(--broccoli-bg); color: var(--broccoli-fg); font-weight:700; }
      td.cell.Grano { background-color: var(--grano-bg); color: var(--grano-fg); font-weight:700; }
      td.cell.China { background-color: var(--china-bg); color: var(--china-fg); font-weight:700; }
      td.cell.Dulce { background-color: var(--dulce-bg); color: var(--dulce-fg); font-weight:700; }
      .cell-val { display:block; width:100%; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; line-height:22px; }
    </style>
    </head>
    <body>
    <div id="app">
      <header>
        <h1>Planificación de Siembras — V11.0</h1>
      </header>
      <div class="toolbar">
        <div class="tool-section"><div class="tabs" id="fincaTabs"></div></div>
        <div class="tool-divider"></div>
        <div class="tool-section"><div class="field-group"><label>🌱 Filtrar Vegetal</label><div class="field"><select id="vegFilter"><option value="">Todos</option><option value="Ejote">Ejote</option><option value="Broccoli">Broccoli</option><option value="Grano">Grano</option><option value="China">China</option><option value="Dulce">Dulce</option></select></div></div></div>
        <div class="tool-section" style="margin-left:auto;">
          <div class="stat"><b id="statArea">0.0 ha</b><span>Área Total</span></div>
        </div>
      </div>
      <div class="grid-wrap" id="gridWrap"></div>
    </div>
    <script>
    (function() {
      function init() {
        var YEARS = [2026, 2027];
        var FINCAS = ['NP','CH','TM','PV','SM'];
        var LOTES = [];
        var idC = 1;
        FINCAS.forEach(function(f) {
          var count = (f === 'NP') ? 40 : 20;
          for (var i = 1; i <= count; i++) {
            LOTES.push({ id: f + '-' + i, finca: f, nombre: f + '-' + i, area: 1.0 });
            idC++;
          }
        });
        
        var plantings = {
          'NP-1': [{year: 2026, weekInYear: 5, vegetal: 'Broccoli'}],
          'NP-2': [{year: 2026, weekInYear: 8, vegetal: 'Ejote'}],
          'NP-3': [{year: 2026, weekInYear: 12, vegetal: 'Grano'}]
        };
        
        var currentFinca = 'NP';
        var selectedVeg = '';

        function render() {
          var tabsWrap = document.getElementById('fincaTabs');
          tabsWrap.innerHTML = FINCAS.map(function(f){ 
            return '<div class="tab ' + (currentFinca===f?'active':'') + '" data-finca="' + f + '">' + f + '</div>'; 
          }).join('');
          tabsWrap.querySelectorAll('.tab').forEach(function(btn) {
            btn.onclick = function() { currentFinca = btn.dataset.finca; render(); };
          });

          var filteredLotes = LOTES.filter(function(l){ return l.finca === currentFinca; });

          var html = '<table class="grid"><thead><tr>';
          html += '<th class="corner">Sem \\ Lote</th>';
          html += '<th class="sumhead">Total Prod</th>';
          
          filteredLotes.forEach(function(l) {
            html += '<th class="lotehead">' + l.nombre + '<div class="sub">' + l.area + 'h</div></th>';
          });
          html += '</tr></thead><tbody>';

          YEARS.forEach(function(year) {
            html += '<tr class="year-divider"><td colspan="' + (filteredLotes.length + 2) + '">AÑO ' + year + '</td></tr>';
            for (var w = 1; w <= 52; w++) {
              html += '<tr>';
              html += '<td class="weekcell">S' + w + '</td>';
              html += '<td class="sumcell">-</td>';

              filteredLotes.forEach(function(l) {
                var pList = plantings[l.id] || [];
                var matched = pList.find(function(p){ return p.year === year && p.weekInYear === w; });
                var cssClass = matched ? ('cell ' + matched.vegetal) : 'cell';
                var valStr = matched ? matched.vegetal.substring(0,3).toUpperCase() : '';
                
                if (selectedVeg && matched && matched.vegetal !== selectedVeg) {
                  cssClass += ' dimmed';
                }

                html += '<td class="' + cssClass + '" data-lote="' + l.id + '" data-year="' + year + '" data-week="' + w + '">';
                html += '<span class="cell-val">' + valStr + '</span>';
                html += '</td>';
              });
              html += '</tr>';
            }
          });
          html += '</tbody></table>';

          document.getElementById('gridWrap').innerHTML = html;
          document.getElementById('statArea').innerText = (filteredLotes.length * 1.0).toFixed(1) + ' ha';

          document.querySelectorAll('.grid td.cell').forEach(function(td) {
            td.onclick = function() {
              var lid = td.dataset.lote;
              var yr = parseInt(td.dataset.year);
              var wk = parseInt(td.dataset.week);
              
              if (!plantings[lid]) plantings[lid] = [];
              var idx = plantings[lid].findIndex(function(p){ return p.year === yr && p.weekInYear === wk; });
              
              const vegList = ['Broccoli', 'Ejote', 'Grano', 'China', 'Dulce'];
              if (idx >= 0) {
                plantings[lid].splice(idx, 1);
              } else {
                plantings[lid].push({year: yr, weekInYear: wk, vegetal: vegList[Math.floor(Math.random() * vegList.length)]});
              }
              render();
            };
          });
        }

        document.getElementById('vegFilter').onchange = function(e) {
          selectedVeg = e.target.value;
          render();
        };

        render();
      }
      if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); } else { init(); }
    })();
    </script>
    </body>
    </html>
    """

  # Codificar el contenido HTML en Base64 para cargarlo de forma segura y moderna con components.iframe
  b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
  components.iframe(
      f'data:text/html;base64,{b64_html}', height=850, scrolling=True
  )

elif menu_principal == '📂 Catálogo de Fincas y Lotes (Áreas Reales)':
  st.subheader('🌱 Gestión de Catálogo de Fincas y Lotes con Áreas Reales')
  st.markdown(
      'Aquí puedes modificar las áreas reales de los lotes existentes o'
      ' **agregar una nueva finca** con sus respectivos lotes.'
  )

  finca_gestion = st.selectbox(
      'Seleccionar Finca a Editar',
      ['NP (Finca Principal 1-40)', 'CH', 'TM', 'PV', 'SM', '➕ Agregar Nueva Finca'],
  )

  if finca_gestion == '➕ Agregar Nueva Finca':
    nueva_finca_nombre = st.text_input('Nombre de la Nueva Finca')
    num_lotes_nuevo = st.number_input(
        'Cantidad de Lotes', min_value=1, max_value=100, value=10
    )
    if st.button('Crear Finca'):
      st.success(
          f'¡Finca "{nueva_finca_nombre}" creada con {num_lotes_nuevo} lotes'
          ' exitosamente!'
      )
  else:
    finc_key = finca_gestion.split(' ')[0]
    st.markdown(f'### Lotes de la Finca: {finc_key}')

    num_lotes = 40 if finc_key == 'NP' else 20
    prefix = finc_key

    if f'lotes_{finc_key}' not in st.session_state:
      st.session_state[f'lotes_{finc_key}'] = pd.DataFrame({
          'Lote': [f'{prefix}-{i}' for i in range(1, num_lotes + 1)],
          'Área Teórica (ha)': [1.0] * num_lotes,
          'Área Real (ha)': [1.0] * num_lotes,
      })

    df_lotes_editado = st.data_editor(
        st.session_state[f'lotes_{finc_key}'], key=f'editor_{finc_key}', hide_index=True
    )
    st.session_state[f'lotes_{finc_key}'] = df_lotes_editado

elif menu_principal == '📊 Catálogo de Rendimientos y Vegetales (Siesa Plan)':
  st.subheader('📈 Datos extraídos del archivo Siesa Plan.xlsx')

  tab_r, tab_c = st.tabs(
      ['Rendimientos Semanales', 'Curva de Producción por Vegetal']
  )

  with tab_r:
    st.markdown('### Hoja: Rendimientos')
    st.dataframe(df_rendimientos, use_container_width=True)

  with tab_c:
    st.markdown('### Hoja: Rendimiento por vegetal')
    st.dataframe(df_curvas, use_container_width=True)
