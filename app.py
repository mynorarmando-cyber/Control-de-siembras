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

# A. Catálogo Maestro de Fincas y Lotes (NP 1-40, SM/PV/TM/CH 1-30)
if "df_lotes" not in st.session_state:
    lotes_iniciales = []
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

# B. Catálogo Maestro de Cultivos / Vegetales
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

# D. Rendimiento por Vegetal (amarrado al ciclo y semanas)
if "df_rendimiento_vegetal" not in st.session_state:
    try:
        st.session_state.df_rendimiento_vegetal = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimiento por vegetal")
    except Exception:
        semanas = list(range(1, 54))
        st.session_state.df_rendimiento_vegetal = pd.DataFrame({
            "Semana": semanas,
            "Ejote": [0.35]*53,
            "Brocoli": [0.20]*53,
            "China": [0.45]*53,
            "Dulce": [0.10]*53,
            "Grano": [0.30]*53
        })


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
        "📋 Planificador de Siembra", 
        "🏢 Gestión de Fincas y Lotes", 
        "🥦 Catálogo de Vegetales", 
        "📊 Matriz de Rendimientos",
        "📈 Rendimiento por Vegetal"
    ]
)


# ==========================================
# 3. VISTAS DE LA APLICACIÓN
# ==========================================

if menu_principal == "📋 Planificador de Siembra":
    st.subheader("📋 Planificador General de Fincas y Lotes")
    st.markdown("Visualiza tus lotes, selecciona el vegetal y la semana de cosecha. El sistema calcula automáticamente la **semana de siembra**, el **ciclo efectivo** (con ajuste de frío si aplica) y la **producción total en libras**.")

    # Filtro opcional por Finca
    fincas_disponibles = sorted(st.session_state.df_lotes["Finca"].unique().tolist())
    finca_filtro = st.selectbox("🔍 Filtrar vista por Finca:", options=["Todas las Fincas"] + fincas_disponibles)

    lotes_activos = st.session_state.df_lotes[st.session_state.df_lotes["Estado"] == "Activo"]
    if finca_filtro != "Todas las Fincas":
        lotes_visibles = lotes_activos[lotes_activos["Finca"] == finca_filtro]
    else:
        lotes_visibles = lotes_activos

    st.markdown("### Asignación de Cultivos y Cosechas por Lote")
    
    plan_data = []
    for _, row in lotes_visibles.iterrows():
        plan_data.append({
            "Finca": row["Finca"],
            "Lote": row["Nombre_Lote"],
            "Área (mz)": row["Area_Manzanas"],
            "Vegetal": "Ejote",
            "Sem. Cosecha": 48
        })
    
    df_plan_editable = st.data_editor(
        pd.DataFrame(plan_data),
        num_rows="dynamic",
        use_container_width=True,
        key="tabla_planificador"
    )

    if not df_plan_editable.empty:
        st.markdown("---")
        st.subheader("📊 Resultados Calculados")
        
        resultados = []
        df_rend = st.session_state.df_rendimientos
        
        for _, row in df_plan_editable.iterrows():
            finca = row["Finca"]
            lote = row["Lote"]
            area = row["Área (mz)"]
            vegetal = row["Vegetal"]
            sem_cosecha = int(row["Sem. Cosecha"])
            
            cultivo_info = st.session_state.df_cultivos[st.session_state.df_cultivos["Vegetal"] == vegetal]
            if not cultivo_info.empty:
                ciclo_base = int(cultivo_info.iloc[0]["Ciclo_Base_Semanas"])
                aplica_frio = bool(cultivo_info.iloc[0]["Aplica_Frio"])
            else:
                ciclo_base = 10
                aplica_frio = False
                
            es_frio = False
            if frio_activo and aplica_frio:
                if semana_inicio_frio > semana_fin_frio:
                    es_frio = (sem_cosecha >= semana_inicio_frio) or (sem_cosecha <= semana_fin_frio)
                else:
                    es_frio = (semana_inicio_frio <= sem_cosecha <= semana_fin_frio)
                    
            ciclo_efectivo = ciclo_base + 1 if es_frio else ciclo_base
            
            sem_siembra = sem_cosecha - ciclo_efectivo
            if sem_siembra <= 0:
                sem_siembra += 53
                
            rend_unitario = 0.0
            if vegetal in df_rend.columns:
                match_r = df_rend.loc[df_rend.iloc[:, 0] == sem_cosecha, vegetal]
                if not match_r.empty:
                    rend_unitario = float(match_r.values[0])
                    
            prod_total = area * rend_unitario
            
            resultados.append({
                "Finca": finca,
                "Lote": lote,
                "Área (mz)": area,
                "Vegetal": vegetal,
                "Sem. Siembra": sem_siembra,
                "Sem. Cosecha": sem_cosecha,
                "Ciclo (Sem)": ciclo_efectivo,
                "Rend. (lbs/mz)": rend_unitario,
                "Producción Total (lbs)": prod_total,
                "Época Fría": "Sí (+1 sem)" if es_frio else "No"
            })
            
        df_resultados = pd.DataFrame(resultados)
        st.dataframe(df_resultados, use_container_width=True)
        
        total_libras = df_resultados["Producción Total (lbs)"].sum()
        total_area = df_resultados["Área (mz)"].sum()
        st.success(f"📌 **Resumen General:** Área Total: **{total_area:,.2f} Manzanas** | Producción Estimada: **{total_libras:,.2f} Libras**")


elif menu_principal == "🏢 Gestión de Fincas y Lotes":
    st.subheader("🏢 Catálogo y Gestor de Fincas y Lotes")
    st.markdown("Aquí encuentras cargados todos tus lotes oficiales (**NP 1-40, SM 1-30, PV 1-30, TM 1-30, CH 1-30**). Puedes editarlos o agregar nuevas fincas y lotes.")

    df_lotes_editado = st.data_editor(st.session_state.df_lotes, num_rows="dynamic", use_container_width=True, key="editor_lotes")
    st.session_state.df_lotes = df_lotes_editado

    with st.form("form_nueva_finca_lote"):
        st.subheader("➕ Agregar Nueva Finca o Lote Individual")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fincas_actuales = st.session_state.df_lotes["Finca"].unique().tolist()
            nueva_finca = st.selectbox("Finca (Seleccionar o escribir nueva)", options=fincas_actuales + ["+ Nueva Finca"])
            if nueva_finca == "+ Nueva Finca":
                nueva_finca = st.text_input("Escriba el nombre/código de la Nueva Finca")
            
            nuevo_nombre_lote = st.text_input("Nombre o Código del Lote (Ej. Lote 31)")
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
    st.markdown("Administra los vegetales, sus ciclos base y su estado (baja lógica para proteger históricos).")
    
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
    st.markdown("Modifica directamente los valores de rendimiento por semana para cada vegetal. Puedes agregar nuevos vegetales simplemente añadiendo nuevas columnas en la tabla.")
    
    df_rend_editado = st.data_editor(st.session_state.df_rendimientos, num_rows="dynamic", use_container_width=True, key="editor_rendimientos")
    st.session_state.df_rendimientos = df_rend_editado


elif menu_principal == "📈 Rendimiento por Vegetal":
    st.subheader("📈 Rendimiento por Vegetal (Amarrado al Ciclo)")
    st.markdown("Control específico del rendimiento por vegetal vinculado a las semanas de desarrollo del cultivo.")
    
    df_rv_editado = st.data_editor(st.session_state.df_rendimiento_vegetal, num_rows="dynamic", use_container_width=True, key="editor_rend_vegetal")
    st.session_state.df_rendimiento_vegetal = df_rv_editado
