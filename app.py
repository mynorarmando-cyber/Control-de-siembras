import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title='Cropplaner - Sistema Integral', page_icon='🌱', layout='wide'
)

st.title('🌱 Cropplaner: Matriz de Proyección y Gestión de Lotes')


# Carga de catálogos base desde Excel
@st.cache_data
def cargar_datos_base():
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


df_rendimientos, df_curvas = cargar_datos_base()

# --- 1. GESTIÓN DE FINCAS Y CATÁLOGO DE LOTES (Con áreas reales editables) ---
st.sidebar.header('📂 Catálogo de Fincas y Lotes')

finca_opcion = st.sidebar.selectbox(
    'Seleccione Finca', ['Finca Principal (NP 1-40)', 'Nueva Finca']
)

if finca_opcion == 'Finca Principal (NP 1-40)':
  st.sidebar.markdown('### Lotes: NP 1 al 40')
  if 'df_lotes_fp' not in st.session_state:
    st.session_state['df_lotes_fp'] = pd.DataFrame({
        'Lote': [f'NP {i}' for i in range(1, 41)],
        'Area Teórica (ha)': [1.0] * 40,
        'Area Real (ha)': [1.0] * 40,
    })
  df_lotes_activo = st.sidebar.data_editor(
      st.session_state['df_lotes_fp'], key='editor_fp', hide_index=True
  )
  st.session_state['df_lotes_fp'] = df_lotes_activo
else:
  st.sidebar.markdown('### Lotes: Nueva Finca')
  if 'df_lotes_fn' not in st.session_state:
    st.session_state['df_lotes_fn'] = pd.DataFrame({
        'Lote': [f'Lote {i}' for i in range(1, 11)],
        'Area Teórica (ha)': [1.0] * 10,
        'Area Real (ha)': [1.0] * 10,
    })
  df_lotes_activo = st.sidebar.data_editor(
      st.session_state['df_lotes_fn'],
      num_rows='dynamic',
      key='editor_fn',
      hide_index=True,
  )
  st.session_state['df_lotes_fn'] = df_lotes_activo


# --- 2. MATRIZ SEMANAL DE PROYECCIÓN (Estructura central de Cropplaner) ---
st.subheader('📊 Matriz Semanal de Proyección de Cosechas')

# Pestañas principales
tab1, tab2, tab3 = st.tabs(
    [
        '🗓️ Matriz de Siembra y Producción',
        '📈 Catálogo de Rendimientos',
        '🌿 Curva de Producción por Vegetal',
    ]
)

with tab1:
  st.markdown(
      'Planifica tus ciclos de siembra utilizando el catálogo de lotes y las'
      ' curvas de rendimiento.'
  )

  col1, col2, col3, col4 = st.columns(4)
  with col1:
    lote_sel = st.selectbox(
        'Lote / NP', df_lotes_activo['Lote'].tolist(), key='matriz_lote'
    )
  with col2:
    cultivo_sel = st.selectbox(
        'Vegetal / Cultivo',
        ['Ejote', 'Brocoli', 'China', 'Dulce', 'Grano'],
        key='matriz_cultivo',
    )
  with col3:
    sem_siembra_input = st.number_input(
        'Semana de Siembra', min_value=1, max_value=53, value=1
    )
  with col4:
    # Obtener automáticamente el área real del lote seleccionado en el catálogo
    area_real_Lote = float(
        df_lotes_activo.loc[
            df_lotes_activo['Lote'] == lote_sel, 'Area Real (ha)'
        ].values[0]
    )
    st.metric(label='Área Real del Lote (ha)', value=area_real_Lote)

  if st.button('Generar / Agregar a la Matriz de Proyección'):
    # Generar la corrida de proyección basada estrictamente en la curva y rendimientos
    matriz_data = []
    for semana_desarrollo, row_curva in df_curvas.iterrows():
      pct_curva = row_curva.get(cultivo_sel, 0)
      if pd.notna(pct_curva) and pct_curva > 0:
        # Calcular la semana del año en la que se cosecha
        semana_ano = ((sem_siembra_input + int(semana_desarrollo) - 2) % 53) + 1

        # Obtener rendimiento de la semana correspondiente
        rend_row = df_rendimientos.loc[
            df_rendimientos['Semana'] == semana_ano, cultivo_sel
        ]
        rend_base = (
            float(rend_row.values[0]) if not rend_row.empty else 10000.0
        )

        volumen = area_real_Lote * rend_base * pct_curva

        matriz_data.append({
            'Finca / Lote': lote_sel,
            'Cultivo': cultivo_sel,
            'Sem. Siembra': sem_siembra_input,
            'Sem. Cosecha (Año)': semana_ano,
            'Sem. Desarrollo': semana_desarrollo,
            '% Curva': pct_curva,
            'Rendimiento Base': rend_base,
            'Área (ha)': area_real_Lote,
            'Volumen Proyectado': volumen,
        })

    df_resultado_matriz = pd.DataFrame(matriz_data)

    # Guardar en session_state para mantener la matriz acumulada en la sesión
    if 'historial_matriz' not in st.session_state:
      st.session_state['historial_matriz'] = pd.DataFrame()

    st.session_state['historial_matriz'] = pd.concat(
        [st.session_state['historial_matriz'], df_resultado_matriz],
        ignore_index=True,
    )

  # Mostrar la Matriz Acumulada si tiene registros
  if (
      'historial_matriz' in st.session_state
      and not st.session_state['historial_matriz'].empty
  ):
    st.markdown('### 📋 Consolidado de Proyecciones en Cropplaner')
    st.dataframe(st.session_state['historial_matriz'], use_container_width=True)

    # Tabla pivote por semana de cosecha para vista de matriz semanal clásica
    st.markdown('### 📊 Matriz Semanal Agregada (Volumen por Semana del Año)')
    df_pivot = st.session_state['historial_matriz'].pivot_table(
        index='Semana Cosecha (Año)',
        columns='Cultivo',
        values='Volumen Proyectado',
        aggfunc='sum',
        fill_value=0,
    )
    st.dataframe(df_pivot, use_container_width=True)
    st.line_chart(df_pivot)

    if st.button('Limpiar Matriz'):
      st.session_state['historial_matriz'] = pd.DataFrame()
      st.rerun()
  else:
    st.info(
        'Configure un lote, cultivo y semana de siembra arriba y haga clic en'
        ' generar para alimentar la matriz.'
    )

with tab2:
  st.markdown('### 📈 Catálogo Base: Rendimientos Semanales')
  st.dataframe(df_rendimientos, use_container_width=True)

with tab3:
  st.markdown('### 🌿 Catálogo Base: Curva de Producción por Vegetal')
  st.dataframe(df_curvas, use_container_width=True)
