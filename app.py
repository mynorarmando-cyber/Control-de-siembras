import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

st.set_page_config(
    page_title="Matriz Agrícola Interactiva",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------------------------------------
# ESTILOS CSS INYECTADOS PARA FORZAR TAMAÑO Y LEGIBILIDAD
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Forzar fuentes grandes y legibles en toda la tabla AgGrid */
    .ag-theme-alpine .ag-cell {
        font-size: 14px !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .ag-theme-alpine .ag-header-cell-label {
        font-size: 15px !important;
        font-weight: bold !important;
        justify-content: center !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌾 Matriz Semanal de Planificación Agrícola")
st.caption("Selecciona el vegetal en la semana de inicio. La tabla expandirá dinámicamente todo el ciclo y marcará en rojo si existe solapamiento.")

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
# 2. INICIALIZAR SIEMBRAS BASE Y ESTRUCTURA
# ---------------------------------------------------------
if 'siembras_origen' not in st.session_state:
    st.session_state['siembras_origen'] = {
        ('TM', 'Lote 1', 2): 'Ejote',
        ('TM', 'Lote 2', 5): 'Broccoli'
    }

# Pestañas de la Aplicación
tab_matriz, tab_config_veg, tab_config_lotes = st.tabs([
    "📋 Matriz Dinámica Unificada (S1 a S52)", 
    "🌱 Gestionar Vegetales y Curvas", 
    "🚜 Gestionar Fincas y Lotes"
])

# =========================================================
# PESTAÑA 1: MATRIZ DINÁMICA DE ENTRADA Y PROYECCIÓN
# =========================================================
with tab_matriz:
    
    # ---------------------------------------------------------
    # CONSTRUCCIÓN DE LA MATRIZ CALCULADA EN TIEMPO REAL
    # ---------------------------------------------------------
    registros_cosecha = []
    conflictos = []
    filas_matriz = []

    for l in LOTES_BASE:
        finca = l['Finca']
        lote = l['Lote']
        area = l['Area_Ha']
        
        fila_res = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
        mapa_semanas = {s: [] for s in range(1, 53)}
        
        # 1. Proyectar todos los ciclos desde las siembras registradas
        for (f, lt, sem_inicio), vegetal in st.session_state['siembras_origen'].items():
            if f == finca and lt == lote and vegetal in st.session_state['vegetales_db']:
                cfg = st.session_state['vegetales_db'][vegetal]
                dur_total = cfg['duracion_total'] + cfg['descanso_post']
                
                for sem_rel, sem_abs in enumerate(range(sem_inicio, min(sem_inicio + dur_total, 53)), start=1):
                    if sem_rel == 1:
                        mapa_semanas[sem_abs].append(f"🌱 {vegetal}")
                    elif sem_rel in cfg['cosecha_pct']:
                        pct = cfg['cosecha_pct'][sem_rel]
                        kg = area * RENDIMIENTO_BASE_KG_HA * pct
                        mapa_semanas[sem_abs].append(f"🟢 {int(kg):,} Kg")
                        
                        registros_cosecha.append({
                            'Semana': sem_abs,
                            'Lote': f"{finca}-{lote}",
                            'Cultivo': vegetal,
                            'Producción_Kg': kg
                        })
                    elif sem_rel <= cfg['duracion_total']:
                        mapa_semanas[sem_abs].append("▫️ Dev")
                    else:
                        mapa_semanas[sem_abs].append("🧹 Descanso")

        # 2. Consolidar celdas y detectar choques/solapamientos
        for s in range(1, 53):
            eventos = mapa_semanas[s]
            if len(eventos) > 1:
                conflictos.append(f"⚠️ Solapamiento en **{finca}-{lote}**, Semana {s}.")
                fila_res[f"S{s}"] = "🔴 CHOQUE"
            elif len(eventos) == 1:
                fila_res[f"S{s}"] = eventos[0]
            else:
                fila_res[f"S{s}"] = ""
                
        filas_matriz.append(fila_res)

    df_matriz_unificada = pd.DataFrame(filas_matriz)

    # ---------------------------------------------------------
    # CONFIGURACIÓN VISUAL Y DIMENSIONES DE AGGRID
    # ---------------------------------------------------------
    gb = GridOptionsBuilder.from_dataframe(df_matriz_unificada)
    gb.configure_default_column(editable=True, groupable=True)

    # Aumentar drásticamente la altura de filas y encabezados
    gb.configure_grid_options(
        rowHeight=60,       # <--- Filas muy amplias (60px)
        headerHeight=50     # <--- Encabezado amplio (50px)
    )

    # Columnas fijas de la izquierda con ancho holgado
    gb.configure_column("Finca", editable=False, pinned="left", width=110)
    gb.configure_column("Lote", editable=False, pinned="left", width=120)
    gb.configure_column("Área (Ha)", editable=False, pinned="left", width=120)

    # Estilos dinámicos JS con colores y bordes claros
    cell_style_js = JsCode("""
    function(params) {
        var baseStyle = {'fontSize': '14px', 'fontWeight': 'bold'};
        if (!params.value) return baseStyle;
        var val = params.value.toString();
        
        if (val.includes("🔴") || val.includes("CHOQUE")) {
            return Object.assign(baseStyle, {'backgroundColor': '#fee2e2', 'color': '#991b1b'});
        } else if (val.includes("🌱")) {
            return Object.assign(baseStyle, {'backgroundColor': '#dcfce7', 'color': '#166534'});
        } else if (val.includes("🟢")) {
            return Object.assign(baseStyle, {'backgroundColor': '#bbf7d0', 'color': '#14532d'});
        } else if (val.includes("▫️")) {
            return Object.assign(baseStyle, {'backgroundColor': '#f3f4f6', 'color': '#374151'});
        } else if (val.includes("🧹")) {
            return Object.assign(baseStyle, {'backgroundColor': '#fef3c7', 'color': '#92400e'});
        }
        return baseStyle;
    }
    """)

    # Desplegable de selección de vegetales para las 52 semanas
    opciones_vegetales = [""] + list(st.session_state['vegetales_db'].keys())

    for s in range(1, 53):
        gb.configure_column(
            f"S{s}",
            cellEditor='agSelectCellEditor',
            cellEditorParams={'values': opciones_vegetales},
            width=180,  # <--- COLUMNAS MUCHO MÁS ANCHAS (180px)
            cellStyle=cell_style_js
        )

    grid_options = gb.build()

    st.subheader("📋 Matriz Única de Planificación y Proyección (S1 - S52)")
    st.caption("Al seleccionar un vegetal en una celda vacía, la tabla proyectará automáticamente las semanas de Desarrollo (▫️), Cosecha (🟢) y Descanso (🧹).")

    grid_response = AgGrid(
        df_matriz_unificada,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=False,
        height=450  # Contenedor principal mucho más alto
    )

    # ---------------------------------------------------------
    # PROCESAR CAMBIOS DEL USUARIO Y REGENERAR SIEMBRAS
    # ---------------------------------------------------------
    df_modificado = pd.DataFrame(grid_response['data'])
    
    # Detectar nuevas siembras creadas o modificadas por el usuario
    nuevas_siembras = {}
    
    for idx, row in df_modificado.iterrows():
        finca = str(row['Finca'])
        lote = str(row['Lote'])
        for s in range(1, 53):
            val = str(row[f"S{s}"]).strip()
            
            # Si el usuario eligió un vegetal directamente o seleccionó '🌱 Vegetal'
            if val in st.session_state['vegetales_db']:
                nuevas_siembras[(finca, lote, s)] = val
            elif val.startswith("🌱 "):
                veg_extraido = val.replace("🌱 ", "").strip()
                if veg_extraido in st.session_state['vegetales_db']:
                    nuevas_siembras[(finca, lote, s)] = veg_extraido

    # Si hubo cambios en la programación de siembras, actualizar estado y recargar
    if nuevas_siembras != st.session_state['siembras_origen']:
        st.session_state['siembras_origen'] = nuevas_siembras
        st.rerun()

    # Alertar conflictos en pantalla
    if conflictos:
        st.error("🚨 **CONFLICTOS DETECTADOS EN LA PROGRAMACIÓN:**")
        for c in set(conflictos):
            st.warning(c)

    # ---------------------------------------------------------
    # GRÁFICA DE LA CURVA CONSOLIDADA
    # ---------------------------------------------------------
    st.divider()
    st.subheader("📈 Curva Total Consolidada de Cosecha (Semanas 1 a 52)")

    df_cosecha = pd.DataFrame(registros_cosecha)

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
    else:
        st.info("No hay cosechas programadas para graficar.")

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
    st.caption("Puedes modificar los lotes o hectáreas de trabajo:")
    
    df_lotes_actual = pd.DataFrame(LOTES_BASE)
    
    df_lotes_editado = st.data_editor(
        df_lotes_actual,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_fincas_lotes"
    )
