import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Planificación Agrícola y Control de Siembras",
    page_icon="🌾",
    layout="wide"
)

# Estilos visuales
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { font-size: 15px; color: #4B5563; margin-bottom: 15px; }
    .alert-box { background-color: #FEE2E2; border-left: 5px solid #EF4444; padding: 10px; margin-bottom: 10px; border-radius: 4px; color: #991B1B; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🌾 Sistema de Planificación y Control de Siembras / Cosechas</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. ESTADO DE SESIÓN (DATOS DINÁMICOS EDITABLES)
# ---------------------------------------------------------

# Catalog de Vegetales y Ciclos
if 'vegetales_config' not in st.session_state:
    st.session_state['vegetales_config'] = {
        'Ejote Fino': {'duracion_total': 11, 'descanso_post': 3, 'cosechas': {10: 0.35, 11: 0.42, 12: 0.23}},
        'Broccoli': {'duracion_total': 16, 'descanso_post': 3, 'cosechas': {10: 0.105, 11: 0.21, 12: 0.1785, 13: 0.105, 14: 0.2415, 15: 0.21}},
        'Grano': {'duracion_total': 13, 'descanso_post': 3, 'cosechas': {11: 0.2446, 12: 0.2935, 13: 0.1957, 14: 0.0815}},
        'China': {'duracion_total': 13, 'descanso_post': 3, 'cosechas': {10: 0.0946, 11: 0.3870, 12: 0.3182, 13: 0.0602}},
        'Dulce': {'duracion_total': 14, 'descanso_post': 3, 'cosechas': {11: 0.0882, 12: 0.1764, 13: 0.3616, 14: 0.2558}}
    }

# Catálogo de Fincas y Lotes
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

# Registros de Planificación
if 'planificaciones' not in st.session_state:
    st.session_state['planificaciones'] = [
        {'Finca': 'TM', 'Lote': '1', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 1},
        {'Finca': 'TM', 'Lote': '1', 'Vegetal': 'Broccoli', 'Semana_Siembra': 15}, # Segunda siembra
        {'Finca': 'NP', 'Lote': 'NP-1', 'Vegetal': 'Ejote Fino', 'Semana_Siembra': 5},
    ]

# Rendimientos Base por Semana
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
# 2. MENÚ NAVEGACIÓN Y PESTAÑAS
# ---------------------------------------------------------
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", [
    "📋 Pestaña Planificación (Matriz Semanal)",
    "➕ Registrar / Editar Siembra",
    "⚙️ Configuración (Vegetales, Lotes y Fincas)"
])

# ---------------------------------------------------------
# OPCIÓN 1: PESTAÑA PLANIFICACIÓN (ESTILO EXCEL) CON DETECCIÓN DE CONFLICTOS
# ---------------------------------------------------------
if opcion == "📋 Pestaña Planificación (Matriz Semanal)":
    st.subheader("📋 Matriz de Planificación de Siembras (Semanas 1 a 52)")
    
    # Evaluar Solapamientos y Ocupación
    lotes_df = st.session_state['lotes_db']
    veg_config = st.session_state['vegetales_config']
    
    # Crear estructura matriz: Finca, Lote, Area_Ha, Sem1 ... Sem52
    matriz_dict = []
    conflictos = []
    
    for idx, row in lotes_df.iterrows():
        finca, lote, area = row['Finca'], row['Lote'], row['Area_Ha']
        fila = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
        
        # Inicializar semanas vacías
        semanas_ocupacion = {s: "" for s in range(1, 53)}
        semanas_duplicadas = {s: 0 for s in range(1, 53)}
        
        # Filtrar planificaciones para este lote
        plans_lote = [p for p in st.session_state['planificaciones'] if p['Finca'] == finca and p['Lote'] == lote]
        
        for p in plans_lote:
            veg = p['Vegetal']
            sem_i = p['Semana_Siembra']
            duracion = veg_config.get(veg, {}).get('duracion_total', 12) + veg_config.get(veg, {}).get('descanso_post', 0)
            
            for s in range(sem_i, min(sem_i + duracion, 53)):
                semanas_duplicadas[s] += 1
                if semanas_ocupacion[s] == "":
                    semanas_ocupacion[s] = f"{veg}"
                else:
                    semanas_ocupacion[s] += f" / {veg}"
                    
        # Detectar si hubo solapamiento (>1 ciclo en la misma semana)
        for s, count in semanas_duplicadas.items():
            if count > 1:
                conflictos.append(f"⚠️ **Conflicto de Solapamiento:** Finca **{finca}** - Lote **{lote}** en la **Semana {s}** ({semanas_ocupacion[s]})")
        
        for s in range(1, 53):
            fila[f"S{s}"] = semanas_ocupacion[s]
            
        matriz_dict.append(fila)
        
    df_matriz = pd.DataFrame(matriz_dict)
    
    # Mostrar alertas de conflicto si existen
    if conflictos:
        st.error("🚨 **¡ALERTA DE SOBREPOSICIÓN DE CICLOS DETECTADA!**")
        for conf in conflictos:
            st.markdown(f"<div class='alert-box'>{conf}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ **Planificación Limpia:** No hay solapamientos de ciclos en ningún lote.")
        
    st.markdown("---")
    st.markdown("### Vista de Calendario por Lote (Pestaña Planificación)")
    st.dataframe(df_matriz, use_container_width=True, height=450)

# ---------------------------------------------------------
# OPCIÓN 2: REGISTRAR / EDITAR SIEMBRAS CON VALIDACIÓN
# ---------------------------------------------------------
elif opcion == "➕ Registrar / Editar Siembra":
    st.subheader("➕ Programar Nueva Siembra")
    
    lotes_df = st.session_state['lotes_db']
    veg_config = st.session_state['vegetales_config']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fincas_disponibles = lotes_df['Finca'].unique()
        finca_sel = st.selectbox("Seleccionar Finca:", fincas_disponibles)
        
        lotes_finca = lotes_df[lotes_df['Finca'] == finca_sel]['Lote'].unique()
        lote_sel = st.selectbox("Seleccionar Lote:", lotes_finca)
        
        veg_sel = st.selectbox("Seleccionar Vegetal:", list(veg_config.keys()))
        sem_inicio = st.number_input("Semana de Siembra (1-52):", min_value=1, max_value=52, value=1)
        
        # Validar en tiempo real antes de guardar
        duracion_nueva = veg_config[veg_sel]['duracion_total'] + veg_config[veg_sel]['descanso_post']
        sem_fin_nueva = sem_inicio + duracion_nueva - 1
        
        # Verificar si choca con alguna siembra existente
        choque = False
        mismo_lote_plans = [p for p in st.session_state['planificaciones'] if p['Finca'] == finca_sel and p['Lote'] == lote_sel]
        
        for p in mismo_lote_plans:
            d = veg_config.get(p['Vegetal'], {}).get('duracion_total', 12) + veg_config.get(p['Vegetal'], {}).get('descanso_post', 0)
            p_inicio = p['Semana_Siembra']
            p_fin = p_inicio + d - 1
            
            # Condición de solapamiento
            if not (sem_fin_nueva < p_inicio or sem_inicio > p_fin):
                choque = True
                st.warning(f"⚠️ **Atención:** En el lote {lote_sel} ya existe una siembra de **{p['Vegetal']}** (Semanas {p_inicio} a {p_fin}).")

        if st.button("Guardar Planificación de Siembra"):
            st.session_state['planificaciones'].append({
                'Finca': finca_sel,
                'Lote': lote_sel,
                'Vegetal': veg_sel,
                'Semana_Siembra': sem_inicio
            })
            st.success(f"Siembra de {veg_sel} registrada correctamente para Finca {finca_sel} - Lote {lote_sel}.")
            st.rerun()

    with col2:
        st.markdown("### Planificaciones Guardadas")
        if st.session_state['planificaciones']:
            df_plan_view = pd.DataFrame(st.session_state['planificaciones'])
            st.dataframe(df_plan_view, use_container_width=True)
            if st.button("Limpiar Todas las Planificaciones"):
                st.session_state['planificaciones'] = []
                st.rerun()

# ---------------------------------------------------------
# OPCIÓN 3: CONFIGURACIÓN DINÁMICA (NUEVOS VEGETALES, CICLOS, FINCAS Y LOTES)
# ---------------------------------------------------------
elif opcion == "⚙️ Configuración (Vegetales, Lotes y Fincas)":
    st.subheader("⚙️ Configuración de Parámetros del Sistema")
    
    tab1, tab2 = st.tabs(["🌱 Configurar Vegetales y Ciclos", "🚜 Configurar Fincas y Lotes"])
    
    # TAB 1: VEGETALES Y CICLOS
    with tab1:
        st.markdown("#### Añadir o Modificar Vegetal / Tamaño de Ciclo")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            nombre_veg = st.text_input("Nombre del Vegetal (ej. Arveja, Ejote Fino):")
            duracion_tot = st.number_input("Duración Total del Ciclo (semanas):", min_value=1, max_value=30, value=12)
            descanso_post = st.number_input("Semanas de Descanso Post-Cosecha:", min_value=0, max_value=10, value=3)
            
            if st.button("Guardar / Actualizar Vegetal"):
                if nombre_veg:
                    if nombre_veg not in st.session_state['vegetales_config']:
                        st.session_state['vegetales_config'][nombre_veg] = {
                            'duracion_total': duracion_tot,
                            'descanso_post': descanso_post,
                            'cosechas': {duracion_tot - 1: 0.5, duracion_tot: 0.5}
                        }
                    else:
                        st.session_state['vegetales_config'][nombre_veg]['duracion_total'] = duracion_tot
                        st.session_state['vegetales_config'][nombre_veg]['descanso_post'] = descanso_post
                    st.success(f"Vegetal '{nombre_veg}' guardado exitosamente.")
                    st.rerun()
        
        with col_v2:
            st.markdown("#### Vegetales Activos:")
            st.json(st.session_state['vegetales_config'])

    # TAB 2: FINCAS Y LOTES
    with tab2:
        st.markdown("#### Agregar Nuevas Fincas y Lotes")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            nueva_finca = st.text_input("Código/Nombre Finca (ej. TM, NP, Finca La Cuchilla):")
            nuevo_lote = st.text_input("Identificador del Lote (ej. Lote 1, Lote 12B):")
            nueva_area = st.number_input("Área en Hectáreas (Ha):", min_value=0.1, max_value=100.0, value=1.0)
            
            if st.button("Agregar Lote"):
                if nueva_finca and nuevo_lote:
                    nuevo_df = pd.DataFrame([{'Finca': nueva_finca, 'Lote': nuevo_lote, 'Area_Ha': nueva_area}])
                    st.session_state['lotes_db'] = pd.concat([st.session_state['lotes_db'], nuevo_df], ignore_index=True)
                    st.success(f"Lote {nuevo_lote} agregado a Finca {nueva_finca}.")
                    st.rerun()
                    
        with col_l2:
            st.markdown("#### Tabla de Lotes Registrados:")
            st.dataframe(st.session_state['lotes_db'], use_container_width=True)