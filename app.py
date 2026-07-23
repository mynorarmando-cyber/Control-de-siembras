import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Planificación Agrícola y Curvas de Cosecha",
    page_icon="🌾",
    layout="wide"
)

# Estilos CSS
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .alert-box { background-color: #FEE2E2; border-left: 5px solid #EF4444; padding: 10px; margin-bottom: 10px; border-radius: 4px; color: #991B1B; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🌾 Sistema de Planificación Agrícola y Curvas de Cosecha</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. PARÁMETROS Y CATALOGOS (CONFIGURACIÓN)
# ---------------------------------------------------------

# Curvas de Distribución de Cosecha (% de cosecha por semana del ciclo)
if 'vegetales_config' not in st.session_state:
    st.session_state['vegetales_config'] = {
        'Ejote Fino': {
            'duracion_total': 11,
            'descanso_post': 3,
            # Cosecha en semanas 10, 11 y 12 del ciclo (35%, 42%, 23%)
            'cosechas': {10: 0.35, 11: 0.42, 12: 0.23}
        },
        'Broccoli': {
            'duracion_total': 16,
            'descanso_post': 3,
            'cosechas': {10: 0.105, 11: 0.21, 12: 0.1785, 13: 0.105, 14: 0.2415, 15: 0.21}
        },
        'Grano': {
            'duracion_total': 13,
            'descanso_post': 3,
            'cosechas': {11: 0.2446, 12: 0.2935, 13: 0.1957, 14: 0.0815}
        },
        'China': {
            'duracion_total': 13,
            'descanso_post': 3,
            'cosechas': {10: 0.0946, 11: 0.3870, 12: 0.3182, 13: 0.0602}
        },
        'Dulce': {
            'duracion_total': 14,
            'descanso_post': 3,
            'cosechas': {11: 0.0882, 12: 0.1764, 13: 0.3616, 14: 0.2558}
        }
    }

# Catálogo de Lotes
if 'lotes_db' not in st.session_state:
    st.session_state['lotes_db'] = pd.DataFrame([
        {'Finca': 'TM', 'Lote': '1', 'Area_Ha': 1.05},
        {'Finca': 'TM', 'Lote': '2', 'Area_Ha': 0.49},
        {'Finca': 'TM', 'Lote': '3', 'Area_Ha': 1.10},
        {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 0.93},
        {'Finca': 'NP', 'Lote': 'NP-2', 'Area_Ha': 1.12},
        {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90},
        {'Finca': 'PV', 'Lote': 'PV-13', 'Area_Ha': 1.34},
        {'Finca': 'SM', 'Lote': 'SM-17', 'Area_Ha': 1.16}
    ])

# Registro de Siembras Planificadas
if 'planificaciones' not in st.session_state:
    st.session_state['planificaciones'] = [
        {'Finca': 'TM', 'Lote': '1', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 1},
        {'Finca': 'NP', 'Lote': 'NP-1', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 3},
        {'Finca': 'TM', 'Lote': '2', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 5},
        {'Finca': 'CH', 'Lote': 'CH-8', 'Vegetal': 'Broccoli', 'Semana_Siembra': 2},
    ]

# Rendimiento Base Esperado (Kg / Ha) según la semana del año
@st.cache_data
def get_rendimiento_base():
    rend_data = []
    for sem in range(1, 53):
        if sem <= 9: rend = {'Ejote Fino': 10900, 'Broccoli': 8000, 'Grano': 8500, 'China': 7500, 'Dulce': 12000}
        elif sem <= 26: rend = {'Ejote Fino': 11900, 'Broccoli': 10000, 'Grano': 8500, 'China': 7500, 'Dulce': 10000}
        elif sem <= 44: rend = {'Ejote Fino': 11600, 'Broccoli': 9500, 'Grano': 8500, 'China': 7500, 'Dulce': 11000}
        else: rend = {'Ejote Fino': 10900, 'Broccoli': 8000, 'Grano': 8500, 'China': 7500, 'Dulce': 12000}
        rend['Semana'] = sem
        rend_data.append(rend)
    return pd.DataFrame(rend_data)

df_rend_base = get_rendimiento_base()

# ---------------------------------------------------------
# 2. MOTOR DE CÁLCULO DE PRODUCCIÓN Y OCUPACIÓN
# ---------------------------------------------------------
def calcular_matrices():
    lotes_df = st.session_state['lotes_db']
    veg_config = st.session_state['vegetales_config']
    plans = st.session_state['planificaciones']
    
    prod_registros = []
    matriz_ocupacion = []
    conflictos = []
    
    for idx, row in lotes_df.iterrows():
        finca, lote, area = row['Finca'], row['Lote'], row['Area_Ha']
        
        # Estructura para la tabla estilo Excel
        fila_matriz = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
        semanas_texto = {s: "" for s in range(1, 53)}
        semanas_conteo = {s: 0 for s in range(1, 53)}
        
        plans_lote = [p for p in plans if p['Finca'] == finca and p['Lote'] == lote]
        
        for p in plans_lote:
            veg = p['Vegetal']
            sem_i = p['Semana_Siembra']
            cfg = veg_config.get(veg, {'duracion_total': 12, 'descanso_post': 3, 'cosechas': {}})
            
            duracion_total_ocupada = cfg['duracion_total'] + cfg['descanso_post']
            
            # 1. Mapear ocupación en la matriz
            for s in range(sem_i, min(sem_i + duracion_total_ocupada, 53)):
                semanas_conteo[s] += 1
                if semanas_texto[s] == "":
                    semanas_texto[s] = f"{veg}"
                else:
                    semanas_texto[s] += f" / {veg}"
            
            # 2. Calcular producción según la curva del cultivo
            for sem_relativa, pct in cfg['cosechas'].items():
                sem_cosecha_real = sem_i + (sem_relativa - 1)
                if sem_cosecha_real <= 52:
                    # Obtener rendimiento base para esa semana del año
                    r_row = df_rend_base[df_rend_base['Semana'] == sem_cosecha_real]
                    rend_base_ha = r_row[veg].values[0] if (not r_row.empty and veg in r_row) else 10000
                    
                    kg_estimados = area * rend_base_ha * pct
                    
                    prod_registros.append({
                        'Semana': sem_cosecha_real,
                        'Finca': finca,
                        'Lote': lote,
                        'Vegetal': veg,
                        'Produccion_Kg': kg_estimados
                    })
        
        # Validar si hay más de 1 cultivo en la misma semana para este lote
        for s, count in semanas_conteo.items():
            if count > 1:
                conflictos.append(f"⚠️ **Solapamiento:** Finca **{finca}** - Lote **{lote}** en Semana **{s}** ({semanas_texto[s]})")
        
        for s in range(1, 53):
            fila_matriz[f"S{s}"] = semanas_texto[s]
            
        matriz_ocupacion.append(fila_matriz)
        
    return pd.DataFrame(matriz_ocupacion), pd.DataFrame(prod_registros), conflictos

df_matriz, df_produccion, lista_conflictos = calcular_matrices()

# ---------------------------------------------------------
# 3. INTERFAZ Y NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", [
    "📈 Curva de Cosecha Consolidada",
    "📋 Planificación (Matriz Semanal)",
    "➕ Programar Siembra",
    "⚙️ Configurar Cultivos y Lotes"
])

# ---------------------------------------------------------
# VISTA 1: CURVA DE COSECHA CONSOLIDADA POR CULTIVO
# ---------------------------------------------------------
if opcion == "📈 Curva de Cosecha Consolidada":
    st.subheader("📈 Curva de Cosecha Consolidada (Semanas 1 a 52)")
    
    if df_produccion.empty:
        st.info("No hay siembras programadas actualmente.")
    else:
        # Selector de Vegetal
        veg_seleccionado = st.selectbox("Seleccionar Cultivo para ver la Curva:", list(st.session_state['vegetales_config'].keys()))
        
        df_veg = df_produccion[df_produccion['Vegetal'] == veg_seleccionado]
        
        if df_veg.empty:
            st.warning(f"No hay siembras programadas para {veg_seleccionado}.")
        else:
            # Agrupar por semana para ver la suma total de todos los lotes
            df_curva = df_veg.groupby('Semana')['Produccion_Kg'].sum().reset_index()
            
            # Asegurar que se muestren las 52 semanas en la gráfica
            df_full_semanas = pd.DataFrame({'Semana': range(1, 53)})
            df_curva = pd.merge(df_full_semanas, df_curva, on='Semana', how='left').fillna(0)
            
            # Gráfica de Línea/Área para ver la curva
            fig = px.area(
                df_curva, 
                x='Semana', 
                y='Produccion_Kg',
                title=f"Curva de Cosecha Total Estimada para: {veg_seleccionado} (Kg / Semana)",
                labels={'Produccion_Kg': 'Producción (Kg)', 'Semana': 'Semana del Año'},
                markers=True
            )
            fig.update_traces(line_color='#10B981', fillcolor='rgba(16, 185, 129, 0.2)')
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)
            
            # Desglose por Lote
            st.markdown(f"#### Desglose de Producción por Lote para {veg_seleccionado}")
            fig_lotes = px.bar(
                df_veg, 
                x='Semana', 
                y='Produccion_Kg', 
                color='Lote',
                title="Aporte de cada Lote a la Curva Semanal",
                labels={'Produccion_Kg': 'Kg Cosechados'}
            )
            fig_lotes.update_xaxes(dtick=1)
            st.plotly_chart(fig_lotes, use_container_width=True)

# ---------------------------------------------------------
# VISTA 2: MATRIZ DE PLANIFICACIÓN (ESTILO EXCEL)
# ---------------------------------------------------------
elif opcion == "📋 Planificación (Matriz Semanal)":
    st.subheader("📋 Matriz Semanal de Ocupación por Lote")
    
    if lista_conflictos:
        st.error("🚨 **¡ALERTAS DE SOLAPAMIENTO DE CICLOS!**")
        for conf in lista_conflictos:
            st.markdown(f"<div class='alert-box'>{conf}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ **Sin conflictos:** No hay sobreposición de cultivos en ningún lote.")
        
    st.dataframe(df_matriz, use_container_width=True, height=450)

# ---------------------------------------------------------
# VISTA 3: PROGRAMAR SIEMBRA
# ---------------------------------------------------------
elif opcion == "➕ Programar Siembra":
    st.subheader("➕ Registrar Nueva Siembra")
    
    lotes_df = st.session_state['lotes_db']
    veg_config = st.session_state['vegetales_config']
    
    col1, col2 = st.columns(2)
    with col1:
        finca_sel = st.selectbox("Finca:", lotes_df['Finca'].unique())
        lote_sel = st.selectbox("Lote:", lotes_df[lotes_df['Finca'] == finca_sel]['Lote'].unique())
        veg_sel = st.selectbox("Cultivo:", list(veg_config.keys()))
        sem_in = st.number_input("Semana de Siembra (1-52):", min_value=1, max_value=52, value=1)
        
        if st.button("Guardar Siembra"):
            st.session_state['planificaciones'].append({
                'Finca': finca_sel,
                'Lote': lote_sel,
                'Vegetal': veg_sel,
                'Semana_Siembra': sem_in
            })
            st.success("Siembra registrada.")
            st.rerun()
            
    with col2:
        st.markdown("### Siembras Registradas")
        st.dataframe(pd.DataFrame(st.session_state['planificaciones']), use_container_width=True)
        if st.button("Borrar Todo"):
            st.session_state['planificaciones'] = []
            st.rerun()

# ---------------------------------------------------------
# VISTA 4: CONFIGURACIÓN
# ---------------------------------------------------------
elif opcion == "⚙️ Configurar Cultivos y Lotes":
    st.subheader("⚙️ Configuración de Parámetros")
    tab1, tab2 = st.tabs(["🌱 Cultivos y Curvas", "🚜 Fincas y Lotes"])
    
    with tab1:
        st.json(st.session_state['vegetales_config'])
    with tab2:
        st.dataframe(st.session_state['lotes_db'], use_container_width=True)