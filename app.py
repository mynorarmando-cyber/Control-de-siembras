import streamlit as st
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Planificación Agrícola", layout="wide")

st.title("🌾 Planificador Agrícola Multi-Año")

# 1. BASE DE DATOS SIMULADA (DATOS MAESTROS)
@st.cache_data
def cargar_datos_maestros():
    fincas_lotes = {
        "Finca El Roble": [
            {"id": "NP01A", "ha": 2.5},
            {"id": "NP01B", "ha": 2.5},
            {"id": "NP02", "ha": 6.0},
            {"id": "NP03", "ha": 4.0}
        ],
        "Finca San José": [
            {"id": "SJ01", "ha": 8.0},
            {"id": "SJ02", "ha": 5.5}
        ]
    }
    
    # Matriz de rendimiento por vegetal y semana de siembra
    # (Vegetal, Semana) -> (Semanas Ciclo, Rendimiento Ton/Ha)
    rendimientos = {
        "Brócoli": {"ciclo": 9, "rendimiento_base": 45.0},
        "Ejote": {"ciclo": 7, "rendimiento_base": 12.0},
        "Arveja": {"ciclo": 10, "rendimiento_base": 15.0}
    }
    return fincas_lotes, rendimientos

fincas_lotes, catálogo_rendimientos = cargar_datos_maestros()

# 2. PANEL DE FILTROS SUPERIOR
st.sidebar.header("🔍 Filtros de Control")

finca_sel = st.sidebar.selectbox("Seleccionar Finca", list(fincas_lotes.keys()))
anios_sel = st.sidebar.multiselect("Años a Visualizar", [2026, 2027], default=[2026, 2027])
vegetales_sel = st.sidebar.multiselect("Vegetales Visibles", list(catálogo_rendimientos.keys()), default=list(catálogo_rendimientos.keys()))

lotes_disponibles = [l["id"] for l in fincas_lotes[finca_sel]]
lotes_sel = st.sidebar.multiselect("Lotes Visibles", lotes_disponibles, default=lotes_disponibles)

# 3. GENERACIÓN DE MATRIZ DE SEMANAS CONTINUAS
semanas_lista = []
for anio in sorted(anios_sel):
    for sem in range(1, 53):
        semanas_lista.append(f"{anio}-S{sem:02d}")

# Crear DataFrame base
columnas = lotes_sel + ["TOTAL COSECHA FINCA (Ton)"]
df_matriz = pd.DataFrame("", index=semanas_lista, columns=columnas)

# Inicializar estado de siembras en sesión
if "planificacion" not in st.session_state:
    st.session_state.planificacion = [
        {"lote": "NP01A", "semana_siembra": "2026-S49", "vegetal": "Brócoli"},
        {"lote": "NP02", "semana_siembra": "2026-S10", "vegetal": "Ejote"}
    ]

# 4. CÁLCULO DINÁMICO DE COSECHAS
totales_semanales = {sem: 0.0 for sem in semanas_lista}

for plan in st.session_state.planificacion:
    if plan["lote"] in lotes_sel and plan["vegetal"] in vegetales_sel:
        lote_info = next(l for l in fincas_lotes[finca_sel] if l["id"] == plan["lote"])
        veg_info = catálogo_rendimientos[plan["vegetal"]]
        
        sem_siembra = plan["semana_siembra"]
        if sem_siembra in df_matriz.index:
            df_matriz.loc[sem_siembra, plan["lote"]] = f"🌱 {plan['vegetal']}"
            
            # Cálculo de semana de cosecha
            anio_s, num_s = int(sem_siembra.split("-S")[0]), int(sem_siembra.split("-S")[1])
            num_cosecha = num_s + veg_info["ciclo"]
            anio_cosecha = anio_s
            if num_cosecha > 52:
                num_cosecha -= 52
                anio_cosecha += 1
                
            sem_cosecha = f"{anio_cosecha}-S{num_cosecha:02d}"
            volumen = lote_info["ha"] * veg_info["rendimiento_base"]
            
            if sem_cosecha in df_matriz.index:
                df_matriz.loc[sem_cosecha, plan["lote"]] = f"🌽 {volumen:.1f} t"
                totales_semanales[sem_cosecha] += volumen

# Asignar totales calculados
for sem in semanas_lista:
    df_matriz.loc[sem, "TOTAL COSECHA FINCA (Ton)"] = f"{totales_semanales[sem]:.1f} t"

# 5. VISUALIZACIÓN
st.subheader(f"Vista Panorámica: {finca_sel}")
st.dataframe(df_matriz, use_container_width=True, height=600)

# Formulario rápido para programar/cambiar siembras
st.markdown("---")
st.subheader("⚡ Programación Rápida de Siembra")
col1, col2, col3, col4 = st.columns(4)

with col1:
    nuevo_lote = st.selectbox("Lote", lotes_sel)
with col2:
    nueva_sem = st.selectbox("Semana Siembra", semanas_lista)
with col3:
    nuevo_veg = st.selectbox("Vegetal", list(catálogo_rendimientos.keys()))
with col4:
    if st.button("Guardar Siembra"):
        # Remover siembra previa en ese lote/semana si existe
        st.session_state.planificacion = [p for p in st.session_state.planificacion if not (p["lote"] == nuevo_lote and p["semana_siembra"] == nueva_sem)]
        st.session_state.planificacion.append({"lote": nuevo_lote, "semana_siembra": nueva_sem, "vegetal": nuevo_veg})
        st.experimental_rerun()
