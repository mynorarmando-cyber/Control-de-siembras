import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title='Cropplaner - Gestión Agrícola', page_icon='🌱', layout='wide'
)

st.title('🌱 Cropplaner: Sistema Integral de Planificación Agrícola')


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

# --- BARRA LATERAL: GESTIÓN DE FINCAS Y LOTES ---
st.sidebar.header('📂 Configuración de Fincas y Lotes')

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

# --- PESTAÑAS PRINCIPALES DE CROPLANER ---
tab1, tab2, tab3 = st.tabs(
    ['📊 Matriz y Proyección', '📈 Rendimientos', '🌿 Curva de Producción']
)

with tab1:
  st.subheader('Simulación y Proyección de Siembra por Lote')

  col1, col2, col3 = st.columns(3)
  with col1:
    lote_seleccionado = st.selectbox(
        'Seleccione Lote', df_lotes_activo['Lote'].tolist()
    )
  with col2:
    cultivo_seleccionado = st.selectbox(
        'Seleccione Cultivo', ['Ejote', 'Brocoli', 'China', 'Dulce', 'Grano']
    )
  with col3:
    sem_siembra = st.number_input(
        'Semana de Siembra (1-53)', min_value=1, max_value=53, value=1
    )

  # Obtener el área real del lote seleccionado
  area_real_lote = float(
      df_lotes_activo.loc[
          df_lotes_activo['Lote'] == lote_seleccionado, 'Area Real (ha)'
      ].values[0]
  )
  st.info(
      f'Lote Activo: **{lote_seleccionado}** | Área Real Configurada:'
      f' **{area_real_lote} ha**'
  )

  if st.button('Calcular Proyección de Cosecha'):
    # Lógica de cálculo basada en rendimiento y curva
    proyeccion_data = []
    cultivo_key = cultivo_seleccionado

    for semana_curva, row in df_curvas.iterrows():
      pct = row.get(cultivo_key, 0)
      if pd.notna(pct) and pct > 0:
        # Semana del año en la que cae la cosecha
        sem_ano = ((sem_siembra + int(semana_curva) - 2) % 53) + 1
        # Obtener rendimiento base de esa semana
        rend_row = df_rendimientos.loc[
            df_rendimientos['Semana'] == sem_ano, cultivo_key
        ]
        rend_base = (
            float(rend_row.values[0]) if not rend_row.empty else 10000.0
        )

        volumen_estimado = area_real_lote * rend_base * pct
        proyeccion_data.append({
            'Semana Cosecha (Año)': sem_ano,
            'Semana Desarrollo': semana_curva,
            '% Curva': pct,
            'Rendimiento Base': rend_base,
            'Volumen Estimado': volumen_estimado,
        })

    df_proj = pd.DataFrame(proyeccion_data)
    if not df_proj.empty:
      st.success('¡Proyección calculada con éxito!')
      st.dataframe(df_proj, use_container_width=True)
      st.line_chart(
          df_proj.set_index('Semana Cosecha (Año)')['Volumen Estimado']
      )
    else:
      st.warning(
          'No se encontraron datos de curva válidos para este cultivo en las'
          ' semanas posteriores.'
      )

with tab2:
  st.markdown('### Catálogo Base: Rendimientos por Semana')
  st.dataframe(df_rendimientos, use_container_width=True)

with tab3:
  st.markdown('### Catálogo Base: Curva de Producción por Vegetal')
  st.dataframe(df_curvas, use_container_width=True)
