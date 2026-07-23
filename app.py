import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as io
import io
import openpyxl

st.set_page_config(
    page_title="Gestión Agrícola - Control de Siembras y Cosechas",
    page_icon="🌾",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 16px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🌾 Sistema de Planificación Dinámica de Siembras y Cosechas</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Gestión multífinca, asignación por lote y proyección de rendimientos semanales</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DATOS Y CONFIGURACIÓN INICIAL DE CICLOS Y RENDIMIENTOS
# ---------------------------------------------------------
DEFAULT_VEGETALES = {
    'Ejote Fino': {
        'duracion_total': 11,
        'cosechas': {10: 0.35, 11: 0.42, 12: 0.23}, # Semana de ciclo relative: % del rendimiento base
        'descanso_post': 3
    },
    'Broccoli': {
        'duracion_total': 16,
        'cosechas': {10: 0.105, 11: 0.21, 12: 0.1785, 13: 0.105, 14: 0.2415, 15: 0.21},
        'descanso_post': 3
    },
    'Grano': {
        'duracion_total': 13,
        'cosechas': {11: 0.2446, 12: 0.2935, 13: 0.1957, 14: 0.0815},
        'descanso_post': 3
    },
    'China': {
        'duracion_total': 13,
        'cosechas': {10: 0.0946, 11: 0.3870, 12: 0.3182, 13: 0.0602},
        'descanso_post': 3
    },
    'Dulce': {
        'duracion_total': 14,
        'cosechas': {11: 0.0882, 12: 0.1764, 13: 0.3616, 14: 0.2558},
        'descanso_post': 3
    }
}

# Rendimientos base por hectárea según la semana del año
@st.cache_data
def get_rendimiento_base():
    rend_data = []
    for sem in range(1, 53):
        if sem <= 9:
            rend = {'Ejote Fino': 10900, 'Broccoli': 8000, 'Grano': 8500, 'China': 7500, 'Dulce': 12000}
        elif sem <= 26:
            rend = {'Ejote Fino': 11900, 'Broccoli': 10000, 'Grano': 8500, 'China': 7500, 'Dulce': 10000}
        elif sem <= 44:
            rend = {'Ejote Fino': 11600, 'Broccoli': 9500, 'Grano': 8500, 'China': 7500, 'Dulce': 11000}
        else:
            rend = {'Ejote Fino': 10900, 'Broccoli': 8000, 'Grano': 8500, 'China': 7500, 'Dulce': 12000}
        rend['Semana'] = sem
        rend_data.append(rend)
    return pd.DataFrame(rend_data)

df_rend_base = get_rendimiento_base()

# ---------------------------------------------------------
# CARGA Y ESTRUCTURACIÓN DE FINCAS Y LOTES
# ---------------------------------------------------------
@st.cache_data
def load_fincas_lotes_def():
    # Fincas estándar del sistema: NP, CH, TM, PV, SM
    lotes_data = [
        # Finca TM
        {'Finca': 'TM', 'Lote': '1', 'Area_Ha': 1.05},
        {'Finca': 'TM', 'Lote': '2', 'Area_Ha': 0.49},
        {'Finca': 'TM', 'Lote': '3', 'Area_Ha': 1.10},
        {'Finca': 'TM', 'Lote': '4', 'Area_Ha': 0.71},
        {'Finca': 'TM', 'Lote': '5', 'Area_Ha': 0.70},
        {'Finca': 'TM', 'Lote': '6', 'Area_Ha': 1.05},
        {'Finca': 'TM', 'Lote': '7', 'Area_Ha': 1.05},
        {'Finca': 'TM', 'Lote': '8', 'Area_Ha': 1.04},
        {'Finca': 'TM', 'Lote': '11', 'Area_Ha': 0.63},
        # Finca NP
        {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 0.93},
        {'Finca': 'NP', 'Lote': 'NP-2', 'Area_Ha': 1.12},
        {'Finca': 'NP', 'Lote': 'NP-3', 'Area_Ha': 1.07},
        {'Finca': 'NP', 'Lote': 'NP-4', 'Area_Ha': 0.90},
        {'Finca': 'NP', 'Lote': 'NP-5', 'Area_Ha': 1.00},
        {'Finca': 'NP', 'Lote': 'NP-6', 'Area_Ha': 1.01},
        {'Finca': 'NP', 'Lote': 'NP-7A', 'Area_Ha': 0.73},
        {'Finca': 'NP', 'Lote': 'NP-7B', 'Area_Ha': 0.73},
        # Finca CH
        {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90},
        {'Finca': 'CH', 'Lote': 'CH-9', 'Area_Ha': 0.90},
        {'Finca': 'CH', 'Lote': 'CH-10', 'Area_Ha': 1.08},
        {'Finca': 'CH', 'Lote': 'CH-11', 'Area_Ha': 0.78},
        {'Finca': 'CH', 'Lote': 'CH-12', 'Area_Ha': 1.00},
        # Finca PV
        {'Finca': 'PV', 'Lote': 'PV-13', 'Area_Ha': 1.34},
        {'Finca': 'PV', 'Lote': 'PV-14', 'Area_Ha': 1.05},
        {'Finca': 'PV', 'Lote': 'PV-15', 'Area_Ha': 1.40},
        {'Finca': 'PV', 'Lote': 'PV-16', 'Area_Ha': 0.65},
        # Finca SM
        {'Finca': 'SM', 'Lote': 'SM-17', 'Area_Ha': 1.16},
        {'Finca': 'SM', 'Lote': 'SM-18', 'Area_Ha': 1.12},
        {'Finca': 'SM', 'Lote': 'SM-19', 'Area_Ha': 1.11},
        {'Finca': 'SM', 'Lote': 'SM-20', 'Area_Ha': 1.00}
    ]
    return pd.DataFrame(lotes_data)

df_lotes = load_fincas_lotes_def()

# Inicialización de estado de sesión para planificaciones activas
if 'planificaciones' not in st.session_state:
    st.session_state['planificaciones'] = [
        {'Finca': 'TM', 'Lote': '1', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 1},
        {'Finca': 'TM', 'Lote': '3', 'Vegetal': 'Broccoli', 'Semana_Siembra': 4},
        {'Finca': 'NP', 'Lote': 'NP-2', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 10},
        {'Finca': 'CH', 'Lote': 'CH-8', 'Vegetal': 'Grano', 'Semana_Siembra': 5},
        {'Finca': 'PV', 'Lote': 'PV-13', 'Vegetal': 'China', 'Semana_Siembra': 12},
        {'Finca': 'SM', 'Lote': 'SM-17', 'Vegetal': 'Dulce', 'Semana_Siembra': 8},
    ]

# ---------------------------------------------------------
# SIDEBAR / CONTROLES DE NAVEGACIÓN Y AGREGAR SIEMBRA
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/sprout.png", width=70)
st.sidebar.title("Control e Ingreso")

menu_opcion = st.sidebar.radio("Menú Principal", [
    "📌 Dashboard y Resumen General",
    "📝 Planificación e Ingreso de Siembras",
    "📊 Análisis por Vegetal y Finca",
    "⚙️ Configuración de Vegetales / Ciclos"
])

# ---------------------------------------------------------
# CÁLCULOS DINÁMICOS DE PRODUCCIÓN Y ÁREAS
# ---------------------------------------------------------
def calcular_matriz_semanal(planificaciones, df_lotes_df, veg_config, df_rend_df):
    semanas = list(range(1, 53))
    
    # Dataframes de resultados por semana
    prod_records = []
    area_records = []
    
    for plan in planificaciones:
        finca = plan['Finca']
        lote = plan['Lote']
        vegetal = plan['Vegetal']
        sem_inicio = plan['Semana_Siembra']
        
        # Obtener área del lote
        lote_match = df_lotes_df[(df_lotes_df['Finca'] == finca) & (df_lotes_df['Lote'] == lote)]
        if lote_match.empty:
            continue
        area_ha = lote_match['Area_Ha'].values[0]
        
        config = veg_config.get(vegetal, DEFAULT_VEGETALES.get(vegetal, DEFAULT_VEGETALES['Ejote Fino']))
        duracion = config['duracion_total']
        cosechas = config['cosechas']
        
        # Ocupación de lote
        for s in range(sem_inicio, min(sem_inicio + duracion, 53)):
            area_records.append({
                'Semana': s,
                'Finca': finca,
                'Lote': lote,
                'Area_Ha': area_ha,
                'Vegetal': vegetal,
                'Estado': 'Ocupado'
            })
            
        # Producción
        for rel_sem, pct in cosechas.items():
            sem_cosecha = sem_inicio + (rel_sem - 1)
            if sem_cosecha <= 52:
                # Obtener rendimiento base para esa semana de cosecha
                rend_row = df_rend_df[df_rend_df['Semana'] == sem_cosecha]
                rend_base = rend_row[vegetal].values[0] if (not rend_row.empty and vegetal in rend_row) else 10000
                prod_kg = area_ha * rend_base * pct
                
                prod_records.append({
                    'Semana': sem_cosecha,
                    'Finca': finca,
                    'Lote': lote,
                    'Vegetal': vegetal,
                    'Produccion_Kg': prod_kg
                })
                
    df_prod = pd.DataFrame(prod_records) if prod_records else pd.DataFrame(columns=['Semana', 'Finca', 'Lote', 'Vegetal', 'Produccion_Kg'])
    df_area = pd.DataFrame(area_records) if area_records else pd.DataFrame(columns=['Semana', 'Finca', 'Lote', 'Area_Ha', 'Vegetal', 'Estado'])
    
    return df_prod, df_area

df_prod, df_area = calcular_matriz_semanal(
    st.session_state['planificaciones'], 
    df_lotes, 
    DEFAULT_VEGETALES, 
    df_rend_base
)

# ---------------------------------------------------------
# VISTA 1: DASHBOARD Y RESUMEN GENERAL
# ---------------------------------------------------------
if menu_opcion == "📌 Dashboard y Resumen General":
    st.subheader("📊 Métricas Consolidadas y Panorama Semanal")
    
    # Filtros superiores
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fincas_sel = st.multiselect("Filtrar por Finca(s):", df_lotes['Finca'].unique(), default=list(df_lotes['Finca'].unique()))
    with col_f2:
        vegetales_sel = st.multiselect("Filtrar por Vegetal(es):", list(DEFAULT_VEGETALES.keys()), default=list(DEFAULT_VEGETALES.keys()))
        
    # Filtrar datos
    df_prod_filt = df_prod[(df_prod['Finca'].isin(fincas_sel)) & (df_prod['Vegetal'].isin(vegetales_sel))]
    df_area_filt = df_area[(df_area['Finca'].isin(fincas_sel)) & (df_area['Vegetal'].isin(vegetales_sel))]
    
    # KPIs Rápidos
    total_prod = df_prod_filt['Produccion_Kg'].sum() if not df_prod_filt.empty else 0
    total_area_fincas = df_lotes[df_lotes['Finca'].isin(fincas_sel)]['Area_Ha'].sum()
    siembras_cont = len([p for p in st.session_state['planificaciones'] if p['Finca'] in fincas_sel and p['Vegetal'] in vegetales_sel])
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Producción Total Estimada", f"{total_prod:,.0f} Kg")
    kpi2.metric("Área Total Disponible", f"{total_area_fincas:.2f} Ha")
    kpi3.metric("Siembras Programadas", f"{siembras_cont} Lotes")
    kpi4.metric("Fincas Seleccionadas", f"{len(fincas_sel)} de {len(df_lotes['Finca'].unique())}")
    
    st.markdown("---")
    
    # Gráfica de Producción por Semana
    st.markdown("#### 📈 Producción Esperada por Semana (Kg)")
    if not df_prod_filt.empty:
        df_chart_prod = df_prod_filt.groupby(['Semana', 'Vegetal'])['Produccion_Kg'].sum().reset_index()
        fig_prod = px.bar(
            df_chart_prod, 
            x='Semana', 
            y='Produccion_Kg', 
            color='Vegetal',
            title="Producción Semanal por Vegetal",
            labels={'Produccion_Kg': 'Producción (Kg)', 'Semana': 'Semana del Año'},
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_prod.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.info("No hay producción registrada con los filtros seleccionados.")
        
    # Análisis de Ocupación de Suelo / Área Sembrada
    st.markdown("#### 🌱 Resumen de Área Sembrada, Libre y Ocupada por Semana")
    
    area_semanal = []
    for s in range(1, 53):
        area_ocupada = df_area_filt[df_area_filt['Semana'] == s]['Area_Ha'].sum()
        area_libre = max(0.0, total_area_fincas - area_ocupada)
        area_semanal.append({
            'Semana': s,
            'Área Ocupada (Ha)': area_ocupada,
            'Área Libre (Ha)': area_libre
        })
    df_area_semanal = pd.DataFrame(area_semanal)
    
    fig_area = px.area(
        df_area_semanal, 
        x='Semana', 
        y=['Área Ocupada (Ha)', 'Área Libre (Ha)'],
        title="Uso de Suelo Semanal (Hectáreas)",
        color_discrete_map={'Área Ocupada (Ha)': '#10B981', 'Área Libre (Ha)': '#E5E7EB'}
    )
    fig_area.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=2))
    st.plotly_chart(fig_area, use_container_width=True)

    # ---------------------------------------------------------
    # ALERTAS DE LOTES PARADOS (>4 SEMANAS LIBRES) Y POR SEMBRAR
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("#### 🚨 Alertas de Gestión de Lotes")
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown("##### ⏳ Lotes con más de 4 Semanas Libres / Inactivos")
        # Identificar lotes sin siembra en las últimas 4 semanas
        lotes_libres_info = []
        for index, row in df_lotes[df_lotes['Finca'].isin(fincas_sel)].iterrows():
            finca_l = row['Finca']
            lote_l = row['Lote']
            
            # Buscar ocupación del lote
            semanas_ocupadas = df_area[(df_area['Finca'] == finca_l) & (df_area['Lote'] == lote_l)]['Semana'].tolist()
            semanas_libres_consec = 0
            max_descanso = 0
            for s in range(1, 53):
                if s not in semanas_ocupadas:
                    semanas_libres_consec += 1
                    if semanas_libres_consec > max_descanso:
                        max_descanso = semanas_libres_consec
                else:
                    semanas_libres_consec = 0
            
            if max_descanso >= 4:
                lotes_libres_info.append({
                    'Finca': finca_l,
                    'Lote': lote_l,
                    'Área (Ha)': row['Area_Ha'],
                    'Máx. Semanas Libres Consecutivas': max_descanso
                })
        
        if lotes_libres_info:
            st.dataframe(pd.DataFrame(lotes_libres_info), use_container_width=True)
        else:
            st.success("No hay lotes con períodos de inactividad mayores a 4 semanas.")
            
    with col_a2:
        st.markdown("##### 🚀 Próximas Siembras Programadas")
        semana_actual_sim = st.slider("Seleccionar Semana Actual de Referencia:", 1, 52, 10)
        proximas = [
            p for p in st.session_state['planificaciones'] 
            if p['Finca'] in fincas_sel and semana_actual_sim <= p['Semana_Siembra'] <= semana_actual_sim + 3
        ]
        if proximas:
            st.dataframe(pd.DataFrame(proximas), use_container_width=True)
        else:
            st.info(f"No hay siembras programadas para las semanas {semana_actual_sim} a {semana_actual_sim+3}.")

# ---------------------------------------------------------
# VISTA 2: PLANIFICACIÓN E INGRESO DE SIEMBRAS
# ---------------------------------------------------------
elif menu_opcion == "📝 Planificación e Ingreso de Siembras":
    st.subheader("📝 Gestor Dinámico de Siembras")
    st.markdown("Agrega, elimina o desplaza siembras en el calendario. Todo el ciclo se ajusta automáticamente.")
    
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        st.markdown("#### ➕ Agregar / Modificar Siembra")
        with st.form("form_siembra"):
            finca_in = st.selectbox("Seleccionar Finca:", df_lotes['Finca'].unique())
            lotes_disponibles = df_lotes[df_lotes['Finca'] == finca_in]['Lote'].unique()
            lote_in = st.selectbox("Seleccionar Lote:", lotes_disponibles)
            veg_in = st.selectbox("Seleccionar Vegetal:", list(DEFAULT_VEGETALES.keys()))
            sem_in = st.number_input("Semana de Siembra (1-52):", min_value=1, max_value=52, value=10)
            
            submit_btn = st.form_submit_button("Guardar / Actualizar Siembra")
            if submit_btn:
                # Eliminar siembra previa en el mismo lote si existe
                st.session_state['planificaciones'] = [
                    p for p in st.session_state['planificaciones'] 
                    if not (p['Finca'] == finca_in and p['Lote'] == lote_in and p['Semana_Siembra'] == sem_in)
                ]
                st.session_state['planificaciones'].append({
                    'Finca': finca_in,
                    'Lote': lote_in,
                    'Vegetal': veg_in,
                    'Semana_Siembra': sem_in
                })
                st.success(f"Siembra de {veg_in} en {finca_in} - Lote {lote_in} programada para la Semana {sem_in}.")
                st.rerun()

    with col_c2:
        st.markdown("#### 📅 Tabla Maestra de Siembras Activas")
        if st.session_state['planificaciones']:
            df_plan_show = pd.DataFrame(st.session_state['planificaciones'])
            st.dataframe(df_plan_show, use_container_width=True)
            
            # Opción para eliminar
            st.markdown("##### 🗑️ Eliminar Siembra Programada")
            idx_del = st.selectbox("Seleccionar Siembra a Eliminar:", range(len(st.session_state['planificaciones'])), format_func=lambda i: f"{st.session_state['planificaciones'][i]['Finca']} - Lote {st.session_state['planificaciones'][i]['Lote']} ({st.session_state['planificaciones'][i]['Vegetal']} Sem {st.session_state['planificaciones'][i]['Semana_Siembra']})")
            if st.button("Eliminar Siembra Seleccionada"):
                st.session_state['planificaciones'].pop(idx_del)
                st.warning("Siembra eliminada con éxito.")
                st.rerun()
        else:
            st.info("No hay siembras registradas en la planificación.")

# ---------------------------------------------------------
# VISTA 3: ANÁLISIS POR VEGETAL Y FINCA
# ---------------------------------------------------------
elif menu_opcion == "📊 Análisis por Vegetal y Finca":
    st.subheader("📊 Análisis Detallado por Vegetal y Finca")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        finca_target = st.selectbox("Seleccionar Finca para Inspección:", df_lotes['Finca'].unique())
    with col_v2:
        veg_target = st.selectbox("Seleccionar Vegetal:", list(DEFAULT_VEGETALES.keys()))
        
    df_prod_target = df_prod[(df_prod['Finca'] == finca_target) & (df_prod['Vegetal'] == veg_target)]
    
    if not df_prod_target.empty:
        st.markdown(f"#### Proyección de Producción de **{veg_target}** en Finca **{finca_target}**")
        
        # Tabla resumen semana por semana
        df_res_sem = df_prod_target.groupby(['Semana', 'Lote'])['Produccion_Kg'].sum().unstack(fill_value=0)
        st.dataframe(df_res_sem, use_container_width=True)
        
        # Gráfica detallada
        fig_det = px.bar(
            df_prod_target, 
            x='Semana', 
            y='Produccion_Kg', 
            color='Lote',
            title=f"Aporte por Lote para {veg_target} en {finca_target}",
            labels={'Produccion_Kg': 'Kg Producidos', 'Semana': 'Semana del Año'}
        )
        st.plotly_chart(fig_det, use_container_width=True)
    else:
        st.warning(f"No hay registros de producción para {veg_target} en la finca {finca_target}.")

# ---------------------------------------------------------
# VISTA 4: CONFIGURACIÓN DE VEGETALES Y CICLOS
# ---------------------------------------------------------
elif menu_opcion == "⚙️ Configuración de Vegetales / Ciclos":
    st.subheader("⚙️ Configuración Paramétrica de Ciclos y Vegetales")
    st.markdown("Aquí puedes agregar nuevos cultivos o editar la duración y rendimiento de los existentes sin alterar el sistema.")
    
    st.json(DEFAULT_VEGETALES)
    
    st.info("💡 La flexibilidad del sistema permite agregar un nuevo vegetal especificando su duración en semanas y los % de cosecha esperados.")
