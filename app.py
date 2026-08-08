import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURACIÓN INICIAL (ESTILO V11.0)
# ==========================================
st.set_page_config(
    page_title="Siesa Plan - Sistema de Control Agrícola (V12.0)",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Siesa Plan V12.0 - Planificador de Siembra y Producción")
st.markdown("---")

# ==========================================
# 1. CARGA DE DATOS DESDE EL EXCEL ORIGINAL
# ==========================================
@st.cache_data
def cargar_datos_excel():
    try:
        df_rend = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimientos")
        if "Semana" not in df_rend.columns and len(df_rend.columns) >= 6:
            df_rend.columns = ["Semana", "Ejote", "Brocoli", "China", "Dulce", "Grano"]
        return df_rend
    except Exception:
        semanas = list(range(1, 54))
        return pd.DataFrame({
            "Semana": semanas,
            "Ejote": [10900]*53,
            "Brocoli": [8000]*53,
            "China": [7500]*53,
            "Dulce": [12000]*53,
            "Grano": [8250]*53
        })

df_rendimientos = cargar_datos_excel()

# ==========================================
# 2. INICIALIZACIÓN DE LOTES OFICIALES (V12.0)
# NP: 1-40, SM: 1-30, PV: 1-30, TM: 1-30, CH: 1-30
# ==========================================
if "df_lotes_maestros" not in st.session_state:
    lotes_data = []
    config_fincas = [
        ("NP", 40, 2.0),
        ("SM", 30, 2.5),
        ("PV", 30, 1.8),
        ("TM", 30, 3.0),
        ("CH", 30, 2.2)
    ]
    
    for finca, total_lotes, area_def in config_fincas:
        for i in range(1, total_lotes + 1):
            lotes_data.append({
                "Finca": finca,
                "Lote": f"Lote {i}",
                "Área (mz)": area_def,
                "Vegetal": "Ejote",
                "Semana Cosecha": 48
            })
            
    st.session_state.df_lotes_maestros = pd.DataFrame(lotes_data)

# Ciclos base por vegetal (amarrados al rendimiento y planificación)
ciclos_base = {
    "Ejote": 10,
    "Brocoli": 12,
    "China": 11,
    "Dulce": 9,
    "Grano": 14
}

# ==========================================
# 3. PANEL LATERAL (PARÁMETROS CLÁSICOS V11)
# ==========================================
st.sidebar.header("⚙️ Parámetros de Control")

frio_activo = st.sidebar.checkbox("Activar Época Fría (+1 sem. Ejote)", value=True)
semana_inicio_frio = st.sidebar.number_input("Semana Inicio Frío", 1, 53, 48)
semana_fin_frio = st.sidebar.number_input("Semana Fin Frío", 1, 53, 6)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Instrucciones V12.0:** Modifica directamente en la tabla principal el **Vegetal** y la **Semana de Cosecha** para tus lotes oficiales. El ciclo, la siembra y el rendimiento se calculan automáticamente de forma integrada.")

# ==========================================
# 4. VISTA PRINCIPAL: PLANIFICADOR INTEGRADO
# ==========================================
st.subheader("📋 Matriz de Planificación por Finca y Lote")

# Filtro rápido por Finca
fincas_disponibles = ["Todas las Fincas", "NP", "SM", "PV", "TM", "CH"]
finca_seleccionada = st.selectbox("🔍 Filtrar Finca:", options=fincas_disponibles)

df_actual = st.session_state.df_lotes_maestros
if finca_seleccionada != "Todas las Fincas":
    df_filtrado = df_actual[df_actual["Finca"] == finca_seleccionada]
else:
    df_filtrado = df_actual

# Tabla interactiva heredada de la versión clásica
vegetales_disponibles = list(ciclos_base.keys())

df_editado = st.data_editor(
    df_filtrado,
    num_rows="fixed",
    use_container_width=True,
    key="editor_v12",
    column_config={
        "Finca": st.column_config.TextColumn("Finca", disabled=True),
        "Lote": st.column_config.TextColumn("Lote", disabled=True),
        "Área (mz)": st.column_config.NumberColumn("Área (mz)", format="%.2f"),
        "Vegetal": st.column_config.SelectboxColumn("Vegetal", options=vegetales_disponibles, required=True),
        "Semana Cosecha": st.column_config.NumberColumn("Semana Cosecha", min_value=1, max_value=53, step=1)
    }
)

# Sincronización de cambios en el estado general
if finca_seleccionada != "Todas las Fincas":
    # Actualizar las filas correspondientes en el dataframe maestro
    indices_afectados = df_editado.index
    st.session_state.df_lotes_maestros.loc[indices_afectados] = df_editado
else:
    st.session_state.df_lotes_maestros = df_editado

# ==========================================
# 5. CÁLCULOS Y RESULTADOS CON RENDIMIENTO AMARRADO AL CICLO
# ==========================================
st.markdown("---")
st.subheader("📊 Resultados de Siembra, Ciclo y Producción")

resultados = []
for _, row in st.session_state.df_lotes_maestros.iterrows():
    finca = row["Finca"]
    lote = row["Lote"]
    area = row["Área (mz)"]
    vegetal = row["Vegetal"]
    sem_cosecha = int(row["Semana Cosecha"])
    
    # Ciclo base del vegetal seleccionado
    ciclo_base = ciclos_base.get(vegetal, 10)
    
    # Lógica de época fría (aplica para Ejote)
    es_frio = False
    if frio_activo and vegetal == "Ejote":
        if semana_inicio_frio > semana_fin_frio:
            es_frio = (sem_cosecha >= semana_inicio_frio) or (sem_cosecha <= semana_fin_frio)
        else:
            es_frio = (semana_inicio_frio <= sem_cosecha <= semana_fin_frio)
            
    ciclo_efectivo = ciclo_base + 1 if es_frio else ciclo_base
    
    # Cálculo de la semana de siembra amarrada al ciclo efectivo
    sem_siembra = sem_cosecha - ciclo_efectivo
    if sem_siembra <= 0:
        sem_siembra += 53
        
    # Obtener rendimiento unitario del Excel amarrado a la semana de cosecha
    rendimiento_unitario = 0.0
    if vegetal in df_rendimientos.columns:
        match_r = df_rendimientos.loc[df_rendimientos.iloc[:, 0] == sem_cosecha, vegetal]
        if not match_r.empty:
            rendimiento_unitario = float(match_r.values[0])
            
    produccion_total = area * rendimiento_unitario
    
    resultados.append({
        "Finca": finca,
        "Lote": lote,
        "Área (mz)": area,
        "Vegetal": vegetal,
        "Sem. Siembra": sem_siembra,
        "Sem. Cosecha": sem_cosecha,
        "Ciclo (Sem)": ciclo_efectivo,
        "Rend. (lbs/mz)": rendimiento_unitario,
        "Producción Total (lbs)": produccion_total,
        "Época Fría": "Sí (+1 sem)" if es_frio else "No"
    })

df_resultados = pd.DataFrame(resultados)

# Mostrar tabla de resultados formateada
st.dataframe(
    df_resultados.style.format({
        "Área (mz)": "{:.2f}",
        "Rend. (lbs/mz)": "{:,.2f}",
        "Producción Total (lbs)": "{:,.2f}"
    }),
    use_container_width=True
)

# Métricas consolidadas finales
total_mz = df_resultados["Área (mz)"].sum()
total_libras = df_resultados["Producción Total (lbs)"].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="🌾 Área Total Planificada", value=f"{total_mz:,.2f} Manzanas")
with col2:
    st.metric(label="📦 Producción Total Estimada", value=f"{total_libras:,.2f} Libras")
    
