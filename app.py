import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Planificación Agrícola (Siesa Plan)",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Sistema de Control de Producción Agrícola (Siesa Plan V2)")
st.markdown("---")

# ==========================================
# 1. INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================

# Catálogo Maestro de Fincas y Lotes (Con estatus Activo/Inactivo)
if "df_lotes" not in st.session_state:
    st.session_state.df_lotes = pd.DataFrame(
        [
            {"ID_Lote": "L-01", "Finca": "Finca El Paraíso", "Nombre_Lote": "Lote Norte 1", "Area_Manzanas": 3.50, "Estado": "Activo"},
            {"ID_Lote": "L-02", "Finca": "Finca El Paraíso", "Nombre_Lote": "Lote El Jocote", "Area_Manzanas": 2.00, "Estado": "Activo"},
            {"ID_Lote": "L-03", "Finca": "Finca San José", "Nombre_Lote": "Lote La Vega", "Area_Manzanas": 4.25, "Estado": "Activo"},
            {"ID_Lote": "L-04", "Finca": "Finca San José", "Nombre_Lote": "Lote Experimental", "Area_Manzanas": 1.50, "Estado": "Inactivo"},
        ]
    )

# Catálogo Maestro de Cultivos / Vegetales (Baja lógica para proteger históricos)
if "df_cultivos" not in st.session_state:
    st.session_state.df_cultivos = pd.DataFrame(
        [
            {"ID_Cultivo": "C-01", "Vegetal": "Ejote", "Ciclo_Base_Semanas": 10, "Aplica_Frio": True, "Estado": "Activo"},
            {"ID_Cultivo": "C-02", "Vegetal": "Brocoli", "Ciclo_Base_Semanas": 12, "Aplica_Frio": False, "Estado": "Activo"},
            {"ID_Cultivo": "C-03", "Vegetal": "China", "Ciclo_Base_Semanas": 11, "Aplica_Frio": False, "Estado": "Activo"},
            {"ID_Cultivo": "C-04", "Vegetal": "Dulce", "Ciclo_Base_Semanas": 9, "Aplica_Frio": False, "Estado": "Activo"},
            {"ID_Cultivo": "C-05", "Vegetal": "Grano", "Ciclo_Base_Semanas": 14, "Aplica_Frio": False, "Estado": "Activo"},
        ]
    )

# Matriz de Rendimientos Semanales (Intenta leer tu Excel, si no, usa respaldo estándar)
try:
    df_rendimientos = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimientos")
    if "Semana" not in df_rendimientos.columns:
        df_rendimientos.columns = ["Semana", "Ejote", "Brocoli", "China", "Dulce", "Grano"]
except Exception:
    semanas = list(range(1, 54))
    df_rendimientos = pd.DataFrame({
        "Semana": semanas,
        "Ejote": [10900]*27 + [11600]*10 + [10900]*16,
        "Brocoli": [8000]*27 + [6500]*10 + [8000]*16,
        "China": [7500]*53,
        "Dulce": [12000]*5 + [10000]*10 + [7000]*13 + [10500]*25,
        "Grano": [8250]*53
    })


# ==========================================
# 2. PANEL LATERAL (PARÁMETROS Y CONFIGURACIÓN)
# ==========================================
st.sidebar.header("⚙️ Configuración General")

st.sidebar.subheader("❄️ Época Fría (Ajuste Ejote)")
frio_activo = st.sidebar.checkbox("Activar Lógica de Época Fría", value=True)
semana_inicio_frio = st.sidebar.number_input("Semana Inicio Frío", min_value=1, max_value=53, value=48)
semana_fin_frio = st.sidebar.number_input("Semana Fin Frío", min_value=1, max_value=53, value=6)

st.sidebar.markdown("---")
# Navegación principal por pestañas en la barra lateral o superior
menu_principal = st.sidebar.radio(
    "Navegación", 
    ["🚀 Simulador de Producción", "🏢 Gestión de Fincas y Lotes", "🥦 Catálogo de Vegetales", "📊 Matriz de Rendimientos"]
)


# ==========================================
# 3. VISTAS DE LA APLICACIÓN
# ==========================================

if menu_principal == "🚀 Simulador de Producción":
    st.subheader("🚀 Simulador y Cálculo de Siembra por Lote")
    st.markdown("Calcula la producción estimada multiplicando el **Área Real del Lote** por el **Rendimiento Semanal**, aplicando automáticamente el ajuste de clima frío al ejote.")

    # Filtramos únicamente elementos ACTIVOS para la planificación
    lotes_activos = st.session_state.df_lotes[st.session_state.df_lotes["Estado"] == "Activo"]
    cultivos_activos = st.session_state.df_cultivos[st.session_state.df_cultivos["Estado"] == "Activo"]

    if lotes_activos.empty:
        st.warning("⚠️ No hay lotes activos disponibles. Por favor active al menos un lote en la sección de gestión.")
    elif cultivos_activos.empty:
        st.warning("⚠️ No hay vegetales activos disponibles.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            lote_opciones = lotes_activos.apply(lambda r: f"{r['Finca']} ➔ {r['Nombre_Lote']} ({r['Area_Manzanas']} mz)", axis=1).tolist()
            lote_seleccionado = st.selectbox("Seleccionar Lote Activo", options=lote_opciones)

        with col2:
            vegetal_seleccionado = st.selectbox("Seleccionar Vegetal", options=cultivos_activos["Vegetal"].tolist())

        with col3:
            semana_cosecha = st.number_input("Semana Programada de Cosecha", min_value=1, max_value=53, value=48)

        # Extraer datos del lote seleccionado
        idx_lote = lote_opciones.index(lote_seleccionado)
        lote_row = lotes_activos.iloc[idx_lote]
        area_real = lote_row["Area_Manzanas"]
        finca_nombre = lote_row["Finca"]
        lote_nombre = lote_row["Nombre_Lote"]

        # Extraer datos del cultivo seleccionado
        cultivo_row = cultivos_activos[cultivos_activos["Vegetal"] == vegetal_seleccionado].iloc[0]
        ciclo_base = cultivo_row["Ciclo_Base_Semanas"]
        aplica_frio_cultivo = cultivo_row["Aplica_Frio"]

        # Lógica de Época Fría (Ejote)
        es_epoca_fria = False
        if frio_activo and aplica_frio_cultivo:
            if semana_inicio_frio > semana_fin_frio:
                # Cruce de año (ej: semana 48 a semana 6)
                es_epoca_fria = (semana_cosecha >= semana_inicio_frio) or (semana_cosecha <= semana_fin_frio)
            else:
                es_epoca_fria = (semana_inicio_frio <= semana_cosecha <= semana_fin_frio)

        # Ciclo efectivo (+1 semana si aplica frío)
        ciclo_efectivo = ciclo_base + 1 if es_epoca_fria else ciclo_base

        # Cálculo de semana de siembra (con ajuste circular de 53 semanas)
        semana_siembra = semana_cosecha - ciclo_efectivo
        if semana_siembra <= 0:
            semana_siembra += 53

        # Obtener rendimiento unitario de la matriz
        if vegetal_seleccionado in df_rendimientos.columns:
            rendimiento_unitario = df_rendimientos.loc[df_rendimientos["Semana"] == semana_cosecha, vegetal_seleccionado].values[0]
        else:
            rendimiento_unitario = 0.0

        # Cálculo Total
        produccion_total = area_real * rendimiento_unitario

        st.markdown("---")
        st.subheader("📊 Resultados del Cálculo")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Ubicación", f"{lote_nombre}", f"{finca_nombre}")
        m2.metric("Área Real", f"{area_real:,.2f} Manzanas")
        m3.metric("Ciclo Efectivo", f"{ciclo_efectivo} Semanas", f"{'+1 sem (Frío)' if es_epoca_fria else 'Estándar'}")
        m4.metric("Siembra ➔ Cosecha", f"Sem. {semana_siembra} ➔ Sem. {semana_cosecha}")

        r1, r2 = st.columns(2)
        r1.metric("Rendimiento por Manzana", f"{rendimiento_unitario:,.2f} lbs / mz")
        r2.metric("Producción Total Estimada", f"{produccion_total:,.2f} lbs")

        if es_epoca_fria:
            st.info("❄️ **Aviso Estacional:** La cosecha programada cae dentro del período de época fría. El ciclo del ejote se ha extendido automáticamente una semana más para ajustar la fecha de siembra.")


elif menu_principal == "🏢 Gestión de Fincas y Lotes":
    st.subheader("🏢 Catálogo de Fincas y Lotes")
    st.markdown("Administra las fincas, el tamaño real de los lotes y su estado operativo (Activo/Inactivo).")
    
    st.dataframe(st.session_state.df_lotes, use_container_width=True)

    with st.form("form_nuevo_lote"):
        st.subheader("➕ Agregar Nuevo Lote")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nueva_finca = st.text_input("Nombre de la Finca")
            nuevo_nombre_lote = st.text_input("Nombre o Código del Lote")
        with col_f2:
            nuevo_area = st.number_input("Área Real (Manzanas)", min_value=0.1, value=1.0, step=0.25)
            nuevo_estado = st.selectbox("Estado Inicial", options=["Activo", "Inactivo"])
        
        btn_guardar_lote = st.form_submit_button("Guardar Lote")
        if btn_guardar_lote and nueva_finca and nuevo_nombre_lote:
            nuevo_id = f"L-0{len(st.session_state.df_lotes) + 1}"
            nueva_fila = {
                "ID_Lote": nuevo_id, 
                "Finca": nueva_finca, 
                "Nombre_Lote": nuevo_nombre_lote, 
                "Area_Manzanas": nuevo_area, 
                "Estado": nuevo_estado
            }
            st.session_state.df_lotes = pd.concat([st.session_state.df_lotes, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success(f"¡Lote '{nuevo_nombre_lote}' agregado con éxito!")
            st.rerun()


elif menu_principal == "🥦 Catálogo de Vegetales":
    st.subheader("🥦 Catálogo Maestro de Vegetales / Cultivos")
    st.markdown("Los vegetales marcados como **Inactivos** se ocultan de las nuevas proyecciones, pero se conservan intactos para consultar el histórico plurianual de años anteriores.")
    
    st.dataframe(st.session_state.df_cultivos, use_container_width=True)

    with st.form("form_nuevo_vegetal"):
        st.subheader("➕ Agregar Nuevo Vegetal o Variedad")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            nom_vegetal = st.text_input("Nombre del Vegetal / Variedad")
            ciclo_base_v = st.number_input("Ciclo Base (Semanas de Siembra a Cosecha)", min_value=1, value=10)
        with col_v2:
            aplica_frio_v = st.checkbox("¿Aplica ajuste de +1 semana en Época Fría?", value=False)
            estado_v = st.selectbox("Estado del Vegetal", options=["Activo", "Inactivo"])

        btn_guardar_veg = st.form_submit_button("Guardar Vegetal")
        if btn_guardar_veg and nom_vegetal:
            nuevo_id_v = f"C-0{len(st.session_state.df_cultivos) + 1}"
            nueva_fila_veg = {
                "ID_Cultivo": nuevo_id_v,
                "Vegetal": nom_vegetal,
                "Ciclo_Base_Semanas": ciclo_base_v,
                "Aplica_Frio": aplica_frio_v,
                "Estado": estado_v
            }
            st.session_state.df_cultivos = pd.concat([st.session_state.df_cultivos, pd.DataFrame([nueva_fila_veg])], ignore_index=True)
            st.success(f"¡Vegetal '{nom_vegetal}' agregado con éxito!")
            st.rerun()


elif menu_principal == "📊 Matriz de Rendimientos":
    st.subheader("📊 Matriz de Rendimiento Semanal (lbs / Manzana)")
    st.markdown("Valores base por semana del año. Esta matriz se alimenta de tu archivo Excel y permite calcular la producción multiplicándola por el área real del lote.")
    st.dataframe(df_rendimientos, use_container_width=True)
