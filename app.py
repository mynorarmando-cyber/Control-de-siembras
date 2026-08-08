import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Siesa Plan - Planificador Agrícola",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Siesa Plan: Planificador y Simulador de Siembra")
st.markdown("---")

# ==========================================
# 1. CARGA DE DATOS DESDE EL EXCEL ORIGINAL
# ==========================================
@st.cache_data
def cargar_datos_excel():
    try:
        # Cargar matriz de rendimientos del archivo Siesa Plan.xlsx
        df_rend = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimientos")
        if "Semana" not in df_rend.columns and len(df_rend.columns) >= 6:
            df_rend.columns = ["Semana", "Ejote", "Brocoli", "China", "Dulce", "Grano"]
        return df_rend
    except Exception as e:
        # Fallback si no encuentra el archivo exacto
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
# 2. DEFINICIÓN DE FINCAS Y LOTES OFICIALES
# ==========================================
# NP (1-40), SM (1-30), PV (1-30), TM (1-30), CH (1-30)
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
                "Vegetal": "Ejote",          # Vegetal por defecto
                "Semana Cosecha": 48         # Semana por defecto
            })
            
    st.session_state.df_lotes_maestros = pd.DataFrame(lotes_data)

# ==========================================
# 3. PANEL LATERAL (PARÁMETROS CLAVE)
# ==========================================
st.sidebar.header("⚙️ Parámetros de Ciclo y Clima")

# Ciclos base por vegetal
ciclos_base = {
    "Ejote": 10,
    "Brocoli": 12,
    "China": 11,
    "Dulce": 9,
    "Grano": 14
}

st.sidebar.subheader("❄️ Época Fría (Ajuste Ejote)")
frio_activo = st.sidebar.checkbox("Activar ajuste de Época Fría (+1 sem. Ejote)", value=True)
semana_inicio_frio = st.sidebar.number_input("Semana Inicio Frío", 1, 53, 48)
semana_fin_frio = st.sidebar.number_input("Semana Fin Frío", 1, 53, 6)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Instrucciones:** Modifica directamente en la tabla principal el **Vegetal** y la **Semana de Cosecha** para cada lote de tus fincas (NP, SM, PV, TM, CH). Todo se calculará automáticamente en tiempo real.")

# ==========================================
# 4. VISTA PRINCIPAL: PLANIFICADOR MAESTRO
# ==========================================
st.subheader("📋 Matriz General de Fincas, Lotes y Planificación")

# Filtro rápido por Finca
fincas_disponibles = ["Todas las Fincas", "NP", "SM", "PV", "TM", "CH"]
finca_seleccionada = st.selectbox("🔍 Filtrar vista por Finca:", options=fincas_disponibles)

df_actual = st.session_state.df_lotes_maestros
if finca_seleccionada != "Todas las Fincas":
    df_filtrado = df_actual[df_actual["Finca"] == finca_seleccionada]
else:
    df_filtrado = df_actual

# Tabla editable donde el usuario ve sus fincas y lotes juntos
st.markdown("### Asignación de Cultivos y Cosechas por Lote")
vegetales_disponibles = list(ciclos_base.keys())

# Renderizamos un editor de tabla limpio y directo
df_editado = st.data_editor(
    df_filtrado,
    num_rows="fixed",
    use_container_width=True,
    key="editor_planificador_principal",
    column_config={
        "Finca": st.column_config.TextColumn("Finca", disabled=True),
        "Lote": st.column_config.TextColumn("Lote", disabled=True),
        "Área (mz)": st.column_config.NumberColumn("Área (mz)", format="%.2f"),
        "Vegetal": st.column_config.SelectboxColumn("Vegetal", options=vegetales_disponibles, required=True),
        "Semana Cosecha": st.column_config.NumberColumn("Semana Cosecha", min_value=1, max_value=53, step=1)
    }
)

# Sincronizar cambios de vuelta al estado general si se filtró
if finca_seleccionada != "Todas las Fincas":
    st.session_state.df_lotes_maestros.update(df_editado)
else:
    st.session_state.df_lotes_maestros = df_editado

# ==========================================
# 5. CÁLCULOS AUTOMÁTICOS Y RESULTADOS
# ==========================================
st.markdown("---")
st.subheader("📊 Resultados y Proyección de Siembra y Cosecha")

resultados = []
for _, row in st.session_state.df_lotes_maestros.iterrows():
    finca = row["Finca"]
    lote = row["Lote"]
    area = row["Área (mz)"]
    vegetal = row["Vegetal"]
    sem_cosecha = int(row["Semana Cosecha"])
    
    # Obtener ciclo base
    ciclo_base = ciclos_base.get(vegetal, 10)
    
    # Lógica de época fría (aplica solo si el vegetal es Ejote y está activado)
    es_frio = False
    if frio_activo and vegetal == "Ejote":
        if semana_inicio_frio > semana_fin_frio:
            es_frio = (sem_cosecha >= semana_inicio_frio) or (sem_cosecha <= semana_fin_frio)
        else:
            es_frio = (semana_inicio_frio <= sem_cosecha <= semana_fin_frio)
            
    ciclo_efectivo = ciclo_base + 1 if es_frio else ciclo_base
    
    # Calcular semana de siembra
    sem_siembra = sem_cosecha - ciclo_efectivo
    if sem_siembra <= 0:
        sem_siembra += 53
        
    # Buscar rendimiento en la matriz del Excel
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

df_resultados = st.session_state.df_resultados_finales = pd.DataFrame(resultados)

# Mostrar tabla de resultados con formato limpio
st.dataframe(
    df_resultados.style.format({
        "Área (mz)": "{:.2f}",
        "Rend. (lbs/mz)": "{:,.2f}",
        "Producción Total (lbs)": "{:,.2f}"
    }),
    use_container_width=True
)

# Resumen general consolidado
total_mz = df_resultados["Área (mz)"].sum()
total_libras = df_resultados["Producción Total (lbs)"].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="🌾 Área Total Planificada", value=f"{total_mz:,.2f} Manzanas")
with col2:
    st.metric(label="📦 Producción Total Estimada", value=f"{total_libras:,.2f} Libras")
    
