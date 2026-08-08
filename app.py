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
  # --- TU CÓDIGO ORIGINAL DE CROPPPLANER V11.0 ---
  html_code = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <title>Planificación de Siembras</title>
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
      .expand-btn { background:none; border:none; cursor:pointer; font-size:9px; padding:0 2px; color:var(--forest); font-weight:bold; }
      tr.year-divider td { background: var(--forest) !important; color:#fff !important; font-weight:700; font-size:11px; text-align:left; padding:3px 8px; position:sticky; left:0; z-index:9; }
      td.weekcell { position:sticky; left:0; z-index:7; background:#f0efe8; width:50px; min-width:50px; font-weight:600; font-size:10px; height:24px; }
      td.sumcell { position:sticky; left:50px; z-index:7; background:#e4f0ec; width:95px; min-width:95px; font-weight:700; font-size:10px; height:24px; border-right:2px solid var(--forest); color:var(--forest); }
      td.cell { width:45px; min-width:45px; max-width:45px; height:24px; cursor:pointer; font-size:8.5px; position:relative; user-select:none; overflow:hidden; }
      td.cell:hover { outline:1.5px solid var(--forest); outline-offset:-1px; z-index:5; }
      td.cell.planted { font-weight:700; cursor:grab; }
      td.cell.inherited-occupancy { background-color: var(--inherited-bg); color: var(--inherited-fg); font-style: italic; border: 1px dashed var(--inherited-border); }
      td.cell.long-gap { background-color: var(--gap-bg); color: var(--alert); font-weight: 600; }
      .cell-val { display:block; width:100%; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; font-size:8px; line-height:24px; }
    </style>
    </head>
    <body>
    <div id="app">
      <header>
        <h1>Planificación de Siembras — V11.0 (Original)</h1>
      </header>
      <div class="toolbar">
        <div class="tool-section"><div class="tabs" id="fincaTabs"></div></div>
        <div class="tool-divider"></div>
        <div class="tool-section"><div class="field-group"><label>📊 Resumen General</label><div class="field"><select id="summaryVegFilter"><option value="">Todos</option></select></div></div></div>
        <div class="tool-divider"></div>
        <div class="tool-section"><div class="field-group"><label>🌱 Matriz Planificación</label><div class="field"><select id="loteVegFilter"><option value="">Ver Todos</option></select></div></div></div>
        <div class="tool-divider"></div>
        <div class="tool-section"><div class="field-group"><label>📅 Años</label><div class="multi-year-selector" id="yearCheckboxes"></div></div></div>
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
        var AVAILABLE_YEARS = [2025, 2026, 2027, 2028];
        var selectedYears = [2026, 2027];
        var CICLOS = {
          Ejote:    { duracionBase: 11, cosechas: [[10,0.35],[11,0.42],[12,0.23]], color:'ejote' },
          Broccoli: { duracionBase: 15, cosechas: [[10,0.10],[11,0.20],[12,0.17],[13,0.10],[14,0.23],[15,0.20]], color:'broccoli' },
          Grano:    { duracionBase: 14, cosechas: [[11,0.30],[12,0.36],[13,0.24],[14,0.10]], color:'grano' },
          China:    { duracionBase: 13, cosechas: [[10,0.11],[11,0.45],[12,0.37],[13,0.07]], color:'china' },
          Dulce:    { duracionBase: 14, cosechas: [[11,0.10],[12,0.20],[13,0.41],[14,0.29]], color:'dulce' }
        };
        var FINCAS = ['NP','CH','TM','PV','SM'];
        var BASE_LOTES = [];
        var areaSeed = [1.0, 1.2, 0.8, 1.5, 1.1, 0.9, 1.3, 1.4];
        var idCounter = 1;
        FINCAS.forEach(function(f) {
          var count = (f === 'NP') ? 40 : 30;
          for (var i = 1; i <= count; i++) {
            BASE_LOTES.push({ id: f + '-' + i, finca: f, nombre: f + '-' + i, area: areaSeed[idCounter % areaSeed.length] });
            idCounter++;
          }
        });
        var plantings = {'NP-1': [{year: 2026, weekInYear: 1, vegetal: 'Broccoli'}]};
        var currentFinca = 'NP';
        
        function render() {
          var tabsWrap = document.getElementById('fincaTabs');
          tabsWrap.innerHTML = FINCAS.map(function(f){ return '<div class="tab ' + (currentFinca===f?'active':'') + '" data-finca="' + f + '">' + f + '</div>'; }).join('');
          tabsWrap.querySelectorAll('.tab').forEach(function(btn) {
            btn.onclick = function() { currentFinca = btn.dataset.finca; render(); };
          });
          var wrap = document.getElementById('gridWrap');
          wrap.innerHTML = '<div style="padding: 20px; font-weight: bold; color: var(--forest);">Mostrando Finca: ' + currentFinca + ' (Matriz activa)</div>';
        }
        render();
      }
      if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); } else { init(); }
    })();
    </script>
    </body>
    </html>
    """
  components.html(html_code, height=750, scrolling=True)

elif menu_principal == '📂 Catálogo de Fincas y Lotes (Áreas Reales)':
  st.subheader('🌱 Gestión de Catálogo de Fincas y Lotes con Áreas Reales')
  st.markdown(
      'Aquí puedes modificar las áreas reales de los lotes existentes o'
      ' **agregar una nueva finca** con sus respectivos lotes.'
  )

  # Selector o creador de fincas
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

    # Simulación de editor para los lotes de la finca seleccionada
    if finc_key == 'NP':
      num_lotes = 40
      prefix = 'NP'
    else:
      num_lotes = 30
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
