import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sistema Agrícola - Planificación", layout="wide")

st.title("🌱 Sistema de Control de Producción Agrícola (Siesa Plan V2)")

# ==========================================
# 1. SIMULACIÓN DE CARGA / DATOS MAESTROS
# ==========================================

# A. Catálogo Maestro de Fincas y Lotes (Con estatus Activo/Inactivo)
if "df_lotes" not in st.session_state:
    st.session_state.df_lotes = pd.DataFrame(
        [
            {"ID_Lote": "L-01", "Finca": "Finca El Paraíso", "Nombre_Lote": "Lote Norte 1", "Area_Manzanas": 3.50, "Estado": "Activo"},
            {"ID_Lote": "L-02", "Finca": "Finca El Paraíso", "Nombre_Lote": "Lote El Jocote", "Area_Manzanas": 2.00, "Estado": "Activo"},
            {"ID_Lote": "L-03", "Finca": "Finca San José", "Nombre_Lote": "Lote La Vega", "Area_Manzanas": 4.25, "Estado": "Activo"},
            {"ID_Lote": "L-04", "Finca": "Finca San José", "Nombre_Lote": "Lote Experimental", "Area_Manzanas": 1.50, "Estado": "Inactivo"},
        ]
    )

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

# C. Matriz de Rendimientos por Semana (Leída o inicializada de tu archivo)
try:
    # Intenta leer de tu archivo base si está disponible
    df_rendimientos = pd.read_excel("Siesa Plan.xlsx", sheet_name="Rendimientos")
    # Limpieza básica por si la columna de semana tiene nombres genéricos
    if "Semana" not in df_rendimientos.columns:
        df_rendimientos.columns = ["Semana", "Ejote", "Brocoli", "China", "Dulce", "Grano"]
except Exception:
    # Fallback por seguridad si no encuentra el archivo exacto en ejecución
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
# 2. PANEL LATERAL DE CONFIGURACIÓN Y FILTROS
# ==========================================
st.sidebar.header("⚙️ Parámetros de Planificación")

st.sidebar.subheader("❄️ Configuración Época Fría")
frio_activo = st.sidebar.checkbox("Considerar Época Fría (Ajuste Ejote)", value=True)
semana_inicio_frio = st.sidebar.number_input("Semana Inicio Frío", min_value=1, max_value=53, value=47)
semana_fin_frio = st.sidebar.number_input("Semana Fin Frío", min_value=1, max_value=53, value=6)

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Gestión de Catálogos")
menu_gestion = st.sidebar.selectbox("Ver / Administrar:", ["Simulador de Siembra", "Catálogo de Lotes y Fincas", "Catálogo de Vegetales", "Matriz de Rendimientos"])


# ==========================================
# 3. VISTAS DE LA APLICACIÓN
# ==========================================

if menu_gestion == "Catálogo de Lotes y Fincas":
    st.subheader("🏢 Fincas y Lotes Registrados")
    st.markdown("Aquí puedes dar de alta nuevas fincas, nuevos lotes y activar/desactivar lotes según su disponibilidad.")
    st.dataframe(st.session_state.df_lotes, use_container_width=True)
    
    with st.form("nuevo_lote"):
        st.write("Agregar Nuevo Lote")
        n_finca = st.text_input("Nombre de la Finca")
        n_lote = st.text_input("Nombre / Código del Lote")
        n_area = st.number_input("Área Real (Manzanas)", min_value=0.1, value=1.0)
        submitted_lote = st.form_submit_button("Guardar Lote")
        if submitted_lote and n_finca and n_lote:
            nuevo_id = f"L-0{len(st.session_state.df_lotes) + 1}"
            nueva_fila = {"ID_Lote": nuevo_id, "Finca": n_finca, "Nombre_Lote": n_lote, "Area_Manzanas": n_area, "Estado": "Activo"}
            st.session_state.df_lotes = pd.concat([st.session_state.df_lotes, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success(f"¡Lote {n_lote} agregado exitosamente!")
            st.rerun()

elif menu_gestion == "Catálogo de Vegetales":
    st.subheader("🥦 Catálogo Maestro de Vegetales / Variedades")
    st.markdown("Los vegetales inactivos se ocultan de las nuevas siembras pero se conservan para reportes históricos plurianuales.")
    st.dataframe(st.session_state.df_cultivos, use_container_width=True)

elif menu_gestion == "Matriz de Rendimientos":
    st.subheader("📊 Rendimiento Semanal por Vegetal (lbs / Manzana)")
    st.markdown("Matriz abierta para integrar nuevas columnas de vegetales conforme se requiera.")
    st.dataframe(df_rendimientos, use_container_width=True)

else:
    # Simulador Principal
    st.subheader("🚀 Simulador de Producción por Lote y Ciclo")
    
    # Filtramos únicamente los lotes y cultivos que están ACTIVOS
    lotes_activos = st.session_state.df_lotes[st.session_state.df_lotes["Estado"] == "Activo"]
    cultivos_activos = st.session_state.df_cultivos[st.session_state.df_cultivos["Estado"] == "Activo"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lote_seleccionado = st.selectbox(
            "Seleccionar Lote Activo", 
            options=lotes_activos.apply(lambda row: f"{row['Finca']} - {row['Nombre_Lote']} ({row['Area_Manzanas']} mz)", axis=1)
        )
    
    with col2:
        vegetal_seleccionado = st.selectbox("Seleccionar Vegetal", options=cultivos_activos["Vegetal"].tolist())
        
    with col3:
        semana_cosecha = st.number_input("Semana Programada de Cosecha", min_value=1, max_value=53, value=48)

    # Extraer área del lote seleccionado
    if not lotes_activos.empty:
        idx_lote = lotes_activos.apply(lambda row: f"{row['Finca']} - {row['Nombre_Lote']} ({row['Area_Manzanas']} mz)", axis=1).tolist().index(lote_seleccionado)
        area_real = lotes_activos.iloc[idx_lote]["Area_Manzanas"]
        finca_nombre = lotes_activos.iloc[idx_lote]["Finca"]
        lote_nombre = lotes_activos.iloc[idx_lote]["Nombre_Lote"]
    else:
        area_real = 0.0
        finca_nombre = ""
        lote_nombre = ""

    # Lógica de Época Fría para el Ejote
    info_cultivo = cultivos_activos[cultivos_activos["Vegetal"] == vegetal_seleccionado].iloc[0]
    ciclo_base = info_cultivo["Ciclo_Base_Semanas"]
    aplica_frio_cultivo = info_cultivo["Aplica_Frio"]
    
    # Evaluar si la cosecha cae en época fría
    es_epoca_fria = False
    if frio_activo and aplica_frio_cultivo:
        # Manejo de rangos que pueden cruzar de año (ej: sem 47 a sem 6)
        if semana_inicio_frio > semana_fin_frio:
            es_epoca_fria = (semana_cosecha >= semana_inicio_frio) or (semana_cosecha <= semana_fin_frio)
        else:
            es_epoca_fria = (semana_inicio_frio <= semana_cosecha <= semana_fin_frio)

    # Ajuste de ciclo (+1 semana si es ejote en época fría)
    ciclo_efectivo = ciclo_base + 1 if (es_epoca_fria and aplica_frio_cultivo) else ciclo_base
    semana_siembra = semana_cosecha - ciclo_efectivo
    if semana_siembra <= 0:
        semana_siembra += 53  # Ajuste para ciclo anual circular

    # Obtener rendimiento de la matriz para la semana de cosecha
    if vegetal_seleccionado in df_rendimientos.columns:
        rendimiento_unitario = df_rendimientos.loc[df_rendimientos["Semana"] == semana_cosecha, vegetal_seleccionado].values[0]
    else:
        rendimiento_unitario = 0.0

    produccion_total = area_real * rendimiento_unitario

    st.markdown("---")
    st.markdown("### 📋 Resumen del Ciclo Calculado")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Finca / Lote", f"{lote_nombre}", f"{finca_nombre}")
    m2.metric("Área Real", f"{area_real} Manzanas")
    m3.metric("Ciclo Efectivo", f"{ciclo_efectivo} Semanas", f"{'+1 sem (Frío)' if (es_epoca_fria and aplica_frio_cultivo) else 'Estándar'}")
    m4.metric("Semana Siembra Est. -> Cosecha", f"Sem. {semana_siembra} -> Sem. {semana_cosecha}")

    r1, r2 = st.columns(2)
    r1.metric("Rendimiento por Manzana", f"{rendimiento_unitario:,.2f} lbs/mz")
    r2.metric("Producción Total Estimada", f"{produccion_total:,.2f} lbs")
    
    if es_epoca_fria and aplica_frio_cultivo:
        st.info("❄️ **Aviso de Temporada:** La cosecha cae en período de época fría, por lo que el ciclo del ejote se ha extendido automáticamente una semana más para ajustar la siembra.")
