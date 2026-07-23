import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(
    page_title="Matriz Agrícola Interactiva",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Matriz Semanal de Planificación Agrícola")
st.caption("Selecciona el vegetal directamente desde el menú desplegable en la semana donde iniciará la siembra. Toda la curva se calculará automáticamente abajo.")

# ---------------------------------------------------------
# 1. PARÁMETROS DE CULTIVOS Y CURVAS DE COSECHA
# ---------------------------------------------------------
if 'vegetales_db' not in st.session_state:
    st.session_state['vegetales_db'] = {
        'Ejote': {
            'duracion_total': 11,
            'descanso_post': 2,
            'cosecha_pct': {9: 0.30, 10: 0.45, 11: 0.25}
        },
        'Broccoli': {
            'duracion_total': 14,
            'descanso_post': 3,
            'cosecha_pct': {11: 0.20, 12: 0.50, 13: 0.30}
        },
        'Zucchini': {
            'duracion_total': 10,
            'descanso_post': 2,
            'cosecha_pct': {7: 0.30, 8: 0.40, 9: 0.30}
        }
    }

RENDIMIENTO_BASE_KG_HA = 11000

# Lotes Iniciales Base
LOTES_BASE = [
    {'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05},
    {'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80},
    {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20},
    {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90},
]

# ---------------------------------------------------------
# 2. INICIALIZAR MATRIZ DE TRABAJO (S1 a S52)
# ---------------------------------------------------------
if 'matriz_entrada' not in st.session_state:
    filas = []
    for l in LOTES_BASE:
        f = {'Finca': l['Finca'], 'Lote': l['Lote'], 'Área (Ha)': l['Area_Ha']}
        for s in range(1, 53):
            f[f"S{s}"] = ""
        filas.append(f)
    
    # Cargar siembras iniciales de ejemplo
    filas[0]['S2'] = 'Ejote'
    filas[1]['S5'] = 'Broccoli'
    st.session_state['matriz_entrada'] = pd.DataFrame(filas)

# Pestañas de la Aplicación
tab_matriz, tab_config_veg, tab_config_lotes = st.tabs([
    "📋 Planificación por Matriz (S1 a S52)", 
    "🌱 Gestionar Vegetales y Curvas", 
    "🚜 Gestionar Fincas y Lotes"
])

# =========================================================
# PESTAÑA 1: MATRIZ INTERACTIVA Y CÁLCULO DE CURVAS
# =========================================================
with tab_matriz:
    df_trabajo = st.session_state['matriz_entrada']

    # Configuración de AgGrid
    gb = GridOptionsBuilder.from_dataframe(df_trabajo)
    gb.configure_default_column(editable=True, groupable=True)

    # Fijar columnas informativas a la izquierda
    gb.configure_column("Finca", editable=False, pinned="left", width=90)
    gb.configure_column("Lote", editable=False, pinned="left", width=100)
    gb.configure_column("Área (Ha)", editable=False, pinned="left", width=100)

    # Configurar columnas S1-S52 con menú desplegable de vegetales
    opciones_vegetales = [""] + list(st.session_state['vegetales_db'].keys())

    for s in range(1, 53):
        gb.configure_column(
            f"S{s}",
            cellEditor='agSelectCellEditor',
            cellEditorParams={'values': opciones_vegetales},
            width=85
        )

    grid_options = gb.build()

    st.subheader("📋 Matriz Semanal de Entrada (Doble clic en una celda para elegir el vegetal)")

    # Renderizado simplificado y 100% compatible
    grid_response = AgGrid(
        df_trabajo,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=False,
        height=260
    )

    # Actualizar estado global con los datos editados
    df_actualizado = pd.DataFrame(grid_response['data'])
    st.session_state['matriz_entrada'] = df_actualizado

    # ---------------------------------------------------------
    # PROCESAMIENTO Y EXPANSIÓN AUTOMÁTICA DE LA CURVA
    # ---------------------------------------------------------
    registros_cosecha = []
    matriz_proyectada = []
    conflictos = []

    for idx, row in df_actualizado.iterrows():
        finca = str(row['Finca'])
        lote = str(row['Lote'])
        area = float(row['Área (Ha)'])
        
        fila_res = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
        mapa_semanas = {s: [] for s in range(1, 53)}
        
        # Evaluar celdas con vegetal asignado
        for s in range(1, 53):
            val = str(row[f"S{s}"]).strip()
            if val in st.session_state['vegetales_db']:
                cfg = st.session_state['vegetales_db'][val]
                dur_total = cfg['duracion_total'] + cfg['descanso_post']
                
                for sem_rel, sem_abs in enumerate(range(s, min(s + dur_total, 53)), start=1):
                    if sem_rel == 1:
                        mapa_semanas[sem_abs].append(f"🌱 {val}")
                    elif sem_rel in cfg['cosecha_pct']:
                        pct = cfg['cosecha_pct'][sem_rel]
                        kg = area * RENDIMIENTO_BASE_KG_HA * pct
                        mapa_semanas[sem_abs].append(f"🟢 {int(kg):,} Kg")
                        
                        registros_cosecha.append({
                            'Semana': sem_abs,
                            'Lote': f"{finca}-{lote}",
                            'Cultivo': val,
                            'Producción_Kg': kg
                        })
                    elif sem_rel <= cfg['duracion_total']:
                        mapa_semanas[sem_abs].append("▫️ Dev")
                    else:
                        mapa_semanas[sem_abs].append("🧹 Descanso")

        # Construir fila consolidada
        for s in range(1, 53):
            eventos = mapa_semanas[s]
            if len(eventos) > 1:
                conflictos.append(f"⚠️ Solapamiento en **{finca}-{lote}**, Semana {s}.")
                fila_res[f"S{s}"] = "🔴 CHOQUE"
            elif len(eventos) == 1:
                fila_res[f"S{s}"] = eventos[0]
            else:
                fila_res[f"S{s}"] = ""
                
        matriz_proyectada.append(fila_res)

    df_matriz_calculada = pd.DataFrame(matriz_proyectada)
    df_cosecha = pd.DataFrame(registros_cosecha)

    st.divider()

    if conflictos:
        st.error("🚨 **CONFLICTOS DETECTADOS EN LA PROGRAMACIÓN:**")
        for c in set(conflictos):
            st.warning(c)

    st.subheader("🖼️ Vista Calculada: Ciclos y Cosechas Proyectadas")
    st.dataframe(df_matriz_calculada, use_container_width=True, height=250)

    # ---------------------------------------------------------
    # GRÁFICA DE LA CURVA CONSOLIDADA
    # ---------------------------------------------------------
    st.divider()
    st.subheader("📈 Curva Total Consolidada de Cosecha (Semanas 1 a 52)")

    if not df_cosecha.empty:
        df_totales = df_cosecha.groupby('Semana')['Producción_Kg'].sum().reset_index()
        df_full = pd.DataFrame({'Semana': range(1, 53)})
        df_totales = pd.merge(df_full, df_totales, on='Semana', how='left').fillna(0)
        
        fig = px.area(
            df_totales, x='Semana', y='Producción_Kg',
            title="Volumen Semanal Cosechado Consolidado (Kg Totales)",
            labels={'Producción_Kg': 'Kg Cosechados', 'Semana': 'Semana del Año'},
            markers=True
        )
        fig.update_traces(line_color='#059669', fillcolor='rgba(5, 150, 105, 0.25)')
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# PESTAÑA 2: GESTIONAR VEGETALES Y CURVAS
# =========================================================
with tab_config_veg:
    st.subheader("🌱 Configuración de Vegetales y Curvas de Cosecha")
    
    col_v1, col_v2 = st.columns([1, 1])
    
    with col_v1:
        st.markdown("### Agregar / Modificar Vegetal")
        nuevo_nombre = st.text_input("Nombre del Vegetal (ej. Arveja, China, etc.):")
        dur_t = st.number_input("Duración total del ciclo (Semanas):", min_value=1, value=11)
        dur_d = st.number_input("Semanas de descanso post-cosecha:", min_value=0, value=2)
        
        st.markdown("**Porcentajes de Cosecha por Semana del Ciclo:**")
        s1 = st.number_input("Semana Cosecha 1:", value=9)
        p1 = st.number_input("% Cosecha 1 (ej. 0.30):", value=0.30)
        
        s2 = st.number_input("Semana Cosecha 2:", value=10)
        p2 = st.number_input("% Cosecha 2 (ej. 0.45):", value=0.45)
        
        s3 = st.number_input("Semana Cosecha 3:", value=11)
        p3 = st.number_input("% Cosecha 3 (ej. 0.25):", value=0.25)
        
        if st.button("💾 Guardar Vegetal", type="primary"):
            if nuevo_nombre:
                st.session_state['vegetales_db'][nuevo_nombre] = {
                    'duracion_total': int(dur_t),
                    'descanso_post': int(dur_d),
                    'cosecha_pct': {int(s1): p1, int(s2): p2, int(s3): p3}
                }
                st.success(f"Vegetal '{nuevo_nombre}' agregado a la lista.")
                st.rerun()

    with col_v2:
        st.markdown("### Vegetales Habilitados Activos")
        st.json(st.session_state['vegetales_db'])

# =========================================================
# PESTAÑA 3: GESTIONAR FINCAS Y LOTES
# =========================================================
with tab_config_lotes:
    st.subheader("🚜 Gestión de Lotes y Fincas")
    st.caption("Puedes agregar más filas o modificar las hectáreas directamente en la tabla:")
    
    df_lotes_actual = st.session_state['matriz_entrada'][['Finca', 'Lote', 'Área (Ha)']]
    
    df_lotes_editado = st.data_editor(
        df_lotes_actual,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_fincas_lotes"
    )
