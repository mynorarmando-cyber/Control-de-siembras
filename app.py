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

# A. Catálogo Maestro de Fincas y Lotes (Generación automática NP, SM, PV, TM, CH + opción nueva finca)
if "df_lotes" not in st.session_state:
    lotes_iniciales = []
    
    # Definir estructuras estándar solicitadas
    config_fincas = [
        {"finca": "NP", "rango": 40, "area_default": 2.0},
        {"finca": "SM", "rango": 30, "area_default": 2.5},
        {"finca": "PV", "rango": 30, "area_default": 1.8},
        {"finca": "TM", "rango": 30, "area_default": 3.0},
        {"finca": "CH", "rango": 30, "area_default": 2.2},
    ]
    
    contador = 1
    for f in config_fincas:
        for i in range(1, f["rango"] + 1):
            lotes_iniciales.append({
                "ID_Lote": f"L-{contador:03d}",
                "Finca": f["finca"],
                "Nombre_Lote": f"Lote {i}",
                "Area_Manzanas": f["area_default"],
                "Estado": "Activo"
            })
            contador += 1
            
    st.session_state.df_lotes = pd.DataFrame(lotes_iniciales)

# B. Catálogo Maestro de Cultivos / Vegetales (Baja lógica para proteger históricos)
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

# C. Matriz de Rendimientos Semanales
if "df_rendimientos" not in st.session_state:
    try:
        df_temp = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimientos")
        if "Semana" not in df_temp.columns and len(df_temp.columns) >= 6:
            df_temp.columns = ["Semana", "Ejote", "Brocoli", "China", "Dulce", "Grano"]
        st.session_state.df_rendimientos = df_temp
    except Exception:
        semanas = list(range(1, 54))
        st.session_state.df_rendimientos = pd.DataFrame({
            "Semana": semanas,
            "Ejote": [10900]*27 + [11600]*10 + [10900]*16,
            "Brocoli": [8000]*27 + [6500]*10 + [8000]*16,
            "China": [7500]*53,
            "Dulce": [12000]*5 + [10000]*10 + [7000]*13 + [10500]*25,
            "Grano": [8250]*53
        })

# D. Rendimiento por vegetal (Segunda hoja o estructura relacionada)
if "df_rendimiento_vegetal" not in st.session_state:
    try:
        st.session_state.df_rendimiento_vegetal = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimiento por vegetal")
    except Exception:
        st.session_state.df_rendimiento_vegetal = pd.DataFrame(columns=["Semana", "Ejote", "Brocoli", "China", "Dulce", "Grano"])


# ==========================================
# 2. PANEL LATERAL (PARÁMETROS Y NAVEGACIÓN)
# ==========================================
st.sidebar.header("⚙️ Configuración General")

st.sidebar.subheader("❄️ Época Fría (Ajuste Ejote)")
frio_activo = st.sidebar.checkbox("Activar Lógica de Época Fría", value=True)
semana_inicio_frio = st.sidebar.number_input("Semana Inicio Frío", min_value=1, max_value=53, value=48)
semana_fin_frio = st.sidebar.number_input("Semana Fin Frío", min_value=1, max_value=53, value=6)

st.sidebar.markdown("---")
menu_principal = st.sidebar.radio(
    "Navegación", 
    [
        "🚀 Simulador / Planificador de Siembra", 
        "🏢 Gestión de Fincas y Lotes", 
        "🥦 Catálogo de Vegetales", 
        "📊 Matriz de Rendimientos",
        "📈 Rendimiento por Vegetal"
    ]
)


# ==========================================
# 3. VISTAS DE LA APLICACIÓN
# ==========================================

if menu_principal == "🚀 Simulador / Planificador de Siembra":
    st.subheader("🚀 Simulador y Planificador General de Siembra")
    st.markdown("Selecciona el lote (filtrado por finca) y el vegetal para calcular la siembra, el ciclo efectivo y la producción total basada en el área real.")

    lotes_activos = st.session_state.df_lotes[st.session_state.df_lotes["Estado"] == "Activo"]
    cultivos_activos = st.session_state.df_cultivos[st.session_state.df_cultivos["Estado"] == "Activo"]

    if lotes_activos.empty:
        st.warning("⚠️ No hay lotes activos disponibles. Por favor actívalos en el gestor de lotes.")
    elif cultivos_activos.empty:
        st.warning("⚠️ No hay vegetales activos disponibles.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fincas_disponibles = sorted(lotes_activos["Finca"].unique().tolist())
            finca_elegida = st.selectbox("Filtrar por Finca", options=fincas_disponibles)
        
        lotes_filtrados = lotes_activos[lotes_activos["Finca"] == finca_elegida]
        
        col1, col2, col3 = st.columns(3)

        with col1:
            lote_opciones = lotes_filtrados.apply(lambda r: f"{r['Nombre_Lote']} ({r['Area_Manzanas']} mz)", axis=1).tolist()
            lote_seleccionado = st.selectbox("Seleccionar Lote", options=lote_opciones)

        with col2:
            vegetal_seleccionado = st.selectbox("Seleccionar Vegetal", options=cultivos_activos["Vegetal"].tolist())

        with col3:
            semana_cosecha = st.number_input("Semana Programada de Cosecha", min_value=1, max_value=53, value=48)

        # Extraer datos del lote seleccionado
        lote_row = lotes_filtrados.iloc[lote_opciones.index(lote_seleccionado)]
        area_real = lote_row["Area_Manzanas"]
        lote_nombre = lote_row["Nombre_Lote"]

        # Extraer datos del cultivo seleccionado
        cultivo_row = cultivos_activos[cultivos_activos["Vegetal"] == vegetal_seleccionado].iloc[0]
        ciclo_base = cultivo_row["Ciclo_Base_Semanas"]
        aplica_frio_cultivo = cultivo_row["Aplica_Frio"]

        # Lógica de Época Fría (Ejote)
        es_epoca_fria = False
        if frio_activo and aplica_frio_cultivo:
            if semana_inicio_frio > semana_fin_frio:
                es_epoca_fria = (semana_cosecha >= semana_inicio_frio) or (semana_cosecha <= semana_fin_frio)
            else:
                es_epoca_fria = (semana_inicio_frio <= semana_cosecha <= semana_fin_frio)

        ciclo_efectivo = ciclo_base + 1 if es_epoca_fria else ciclo_base

        semana_siembra = semana_cosecha - ciclo_efectivo
        if semana_siembra <= 0:
            semana_siembra += 53

        # Obtener rendimiento unitario
        df_rend = st.session_state.df_rendimientos
        rendimiento_unitario = 0.0
        if vegetal_seleccionado in df_rend.columns:
            match_rend = df_rend.loc[df_rend.iloc[:, 0] == semana_cosecha, vegetal_seleccionado]
            if not match_rend.empty:
                rendimiento_unitario = float(match_rend.values[0])

        produccion_total = area_real * rendimiento_unitario

        st.markdown("---")
        st.subheader("📊 Resultados del Plan de Siembra")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Finca / Lote", f"{finca_elegida} - {lote_nombre}")
        m2.metric("Área Real", f"{area_real:,.2f} Manzanas")
        m3.metric("Ciclo Efectivo", f"{ciclo_efectivo} Semanas", f"{'+1 sem (Frío)' if es_epoca_fria else 'Estándar'}")
        m4.metric("Siembra ➔ Cosecha", f"Sem. {semana_siembra} ➔ Sem. {semana_cosecha}")

        r1, r2 = st.columns(2)
        r1.metric("Rendimiento por Manzana", f"{rendimiento_unitario:,.2f} lbs / mz")
        r2.metric("Producción Total Estimada", f"{produccion_total:,.2f} lbs")

        if es_epoca_fria:
            st.info("❄️ **Aviso Estacional:** La cosecha programada cae en época fría. El ciclo del ejote se ha extendido automáticamente una semana más.")


elif menu_principal == "🏢 Gestión de Fincas y Lotes":
    st.subheader("🏢 Catálogo y Gestor de Fincas y Lotes")
    st.markdown("Aquí puedes **modificar directamente** los datos de los lotes existentes (Finca, Nombre, Área, Estado) o agregar nuevas fincas y lotes personalizados.")

    # Tabla editable interactiva
    df_lotes_editado = st.data_editor(st.session_state.df_lotes, num_rows="dynamic", use_container_width=True, key="editor_lotes")
    st.session_state.df_lotes = df_lotes_editado

    with st.form("form_nueva_finca_lote"):
        st.subheader("➕ Agregar Nueva Finca o Lote Individual")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            # Opción de escribir una nueva finca o seleccionar una existente
            fincas_actuales = st.session_state.df_lotes["Finca"].unique().tolist()
            nueva_finca = st.selectbox("Finca (Seleccionar o escribir nueva)", options=fincas_actuales + ["+ Nueva Finca"])
            if nueva_finca == "+ Nueva Finca":
                nueva_finca = st.text_input("Escriba el nombre/código de la Nueva Finca (Ej. LP, Xela, etc.)")
            
            nuevo_nombre_lote = st.text_input("Nombre o Código del Lote (Ej. Lote 41)")
        with col_f2:
            nuevo_area = st.number_input("Área Real (Manzanas)", min_value=0.1, value=2.0, step=0.25)
            nuevo_estado = st.selectbox("Estado Inicial", options=["Activo", "Inactivo"])
        
        btn_guardar_lote = st.form_submit_button("Guardar Lote")
        if btn_guardar_lote and nueva_finca and nuevo_nombre_lote:
            nuevo_id = f"L-{len(st.session_state.df_lotes) + 1:03d}"
            nueva_fila = {
                "ID_Lote": nuevo_id, 
                "Finca": nueva_finca, 
                "Nombre_Lote": nuevo_nombre_lote, 
                "Area_Manzanas": nuevo_area, 
                "Estado": nuevo_estado
            }
            st.session_state.df_lotes = pd.concat([st.session_state.df_lotes, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success(f"¡Lote '{nuevo_nombre_lote}' agregado a la finca {nueva_finca} con éxito!")
            st.rerun()


elif menu_principal == "🥦 Catálogo de Vegetales":
    st.subheader("🥦 Catálogo Maestro de Vegetales / Cultivos")
    st.markdown("Administra los vegetales, sus ciclos base y su estado.")
    
    df_cultivos_editado = st.data_editor(st.session_state.df_cultivos, num_rows="dynamic", use_container_width=True, key="editor_cultivos")
    st.session_state.df_cultivos = df_cultivos_editado

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
            nuevo_id_v = f"C-{len(st.session_state.df_cultivos) + 1:03d}"
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
    st.subheader("📊 Matriz de Rendimiento Semanal (Editable)")
    st.markdown("Modifica directamente los valores de rendimiento por semana para cada vegetal, o agrega columnas de nuevos vegetales según lo necesites.")
    
    df_rend_editado = st.data_editor(st.session_state.df_rendimientos, num_rows="dynamic", use_container_width=True, key="editor_rendimientos")
    st.session_state.df_rendimientos = df_rend_editado


elif menu_principal == "📈 Rendimiento por Vegetal":
    st.subheader("📈 Rendimiento por Vegetal")
    st.markdown("Visualización y gestión detallada de los rendimientos específicos por vegetal vinculados al plan.")
    
    df_rv_editado = st.data_editor(st.session_state.df_rendimiento_vegetal, num_rows="dynamic", use_container_width=True, key="editor_rend_vegetal")
    st.session_state.df_rendimiento_vegetal = df_rv_editado
