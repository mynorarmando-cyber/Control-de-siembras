import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Planificador Agrícola por Matriz Directa",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Matriz Directa de Planificación Agrícola")
st.caption("Escribe **'Ejote'** en la semana de inicio. Al presionar **'Procesar y Armar Ciclos'** (o presionar Enter), la matriz completará automáticamente la cosecha y el desarrollo a la derecha.")

# ---------------------------------------------------------
# 1. PARÁMETROS DEL CULTIVO (EJOTE)
# ---------------------------------------------------------
CULTIVOS_CONFIG = {
    'Ejote': {
        'duracion_total': 11,
        'descanso_post': 2,
        # Cosecha en semanas 9, 10 y 11 del ciclo
        'cosecha_pct': {9: 0.30, 10: 0.45, 11: 0.25}
    },
    'Broccoli': {
        'duracion_total': 14,
        'descanso_post': 3,
        'cosecha_pct': {11: 0.20, 12: 0.50, 13: 0.30}
    }
}

RENDIMIENTO_BASE_KG_HA = 11000

# Lotes Base
LOTES = [
    {'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05},
    {'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80},
    {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20},
    {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90},
]

# ---------------------------------------------------------
# 2. INICIALIZAR LA MATRIZ DE TRABAJO (S1 a S52)
# ---------------------------------------------------------
if 'matriz_trabajo' not in st.session_state:
    filas_iniciales = []
    for l in LOTES:
        fila = {'Finca': l['Finca'], 'Lote': l['Lote'], 'Área (Ha)': l['Area_Ha']}
        for s in range(1, 53):
            fila[f"S{s}"] = ""
        filas_iniciales.append(fila)
    
    # Ejemplo inicial: ponemos "Ejote" en S2 del Lote 1
    filas_iniciales[0]['S2'] = 'Ejote'
    st.session_state['matriz_trabajo'] = pd.DataFrame(filas_iniciales)

# ---------------------------------------------------------
# 3. FUNCIÓN PARA EXPANDIR CULTIVOS Y ARMAR CICLOS
# ---------------------------------------------------------
def expandir_ciclos_en_matriz(df_in):
    df_out = df_in.copy()
    registros_cosecha = []
    conflictos = []

    for idx, row in df_in.iterrows():
        finca = row['Finca']
        lote = row['Lote']
        area = row['Área (Ha)']
        
        # Guardar las siembras detectadas en la fila
        siembras_detectadas = []
        for s in range(1, 53):
            val = str(row[f"S{s}"]).strip()
            for crop_name in CULTIVOS_CONFIG.keys():
                if crop_name.lower() in val.lower():
                    siembras_detectadas.append((s, crop_name))
        
        # Si se detectaron siembras, limpiar y proyectar la fila
        if siembras_detectadas:
            # Crear mapa limpio para las 52 semanas
            mapa_semanas = {s: [] for s in range(1, 53)}
            
            for sem_inicio, crop_name in siembras_detectadas:
                cfg = CULTIVOS_CONFIG[crop_name]
                duracion_total = cfg['duracion_total'] + cfg['descanso_post']
                
                for sem_rel, sem_abs in enumerate(range(sem_inicio, min(sem_inicio + duracion_total, 53)), start=1):
                    if sem_rel == 1:
                        mapa_semanas[sem_abs].append(f"🌱 {crop_name}")
                    elif sem_rel in cfg['cosecha_pct']:
                        pct = cfg['cosecha_pct'][sem_rel]
                        kg_cosecha = area * RENDIMIENTO_BASE_KG_HA * pct
                        mapa_semanas[sem_abs].append(f"🟢 {int(kg_cosecha):,} Kg")
                        
                        registros_cosecha.append({
                            'Semana': sem_abs,
                            'Lote': f"{finca}-{lote}",
                            'Cultivo': crop_name,
                            'Producción_Kg': kg_cosecha
                        })
                    elif sem_rel <= cfg['duracion_total']:
                        mapa_semanas[sem_abs].append("▫️ Dev")
                    else:
                        mapa_semanas[sem_abs].append("🧹 Descanso")

            # Asignar a la matriz de salida
            for s in range(1, 53):
                eventos = mapa_semanas[s]
                if len(eventos) > 1:
                    conflictos.append(f"⚠️ Solapamiento en **{finca}-{lote}**, Semana {s}.")
                    df_out.at[idx, f"S{s}"] = "🔴 CHOQUE"
                elif len(eventos) == 1:
                    df_out.at[idx, f"S{s}"] = eventos[0]
                else:
                    df_out.at[idx, f"S{s}"] = ""
                    
    return df_out, pd.DataFrame(registros_cosecha), conflictos

# ---------------------------------------------------------
# 4. INTERFAZ Y EDITOR
# ---------------------------------------------------------
col_title, col_btn = st.columns([3, 1])

with col_btn:
    if st.button("🔄 Generar / Actualizar Ciclos", type="primary", use_container_width=True):
        st.session_state['matriz_trabajo'], df_cosecha, conflictos = expandir_ciclos_en_matriz(st.session_state['matriz_trabajo'])
        st.rerun()

# Matriz Editable Directa
matriz_editada = st.data_editor(
    st.session_state['matriz_trabajo'],
    use_container_width=True,
    height=300,
    key="editor_matriz_unificada"
)

# Guardar cambios del usuario
st.session_state['matriz_trabajo'] = matriz_editada

# Auto-calcular curva para visualización de gráficas
df_matriz_procesada, df_cosecha, conflictos = expandir_ciclos_en_matriz(matriz_editada)

if conflictos:
    st.error("🚨 **CONFLICTOS DETECTADOS:**")
    for c in set(conflictos):
        st.warning(c)

# ---------------------------------------------------------
# 5. GRÁFICA DE LA CURVA CONSOLIDADA
# ---------------------------------------------------------
st.divider()
st.subheader("📈 Curva Total Consolidada de Cosecha (Semanas 1 a 52)")

if not df_cosecha.empty:
    df_totales = df_cosecha.groupby('Semana')['Producción_Kg'].sum().reset_index()
    df_full = pd.DataFrame({'Semana': range(1, 53)})
    df_totales = pd.merge(df_full, df_totales, on='Semana', how='left').fillna(0)
    
    fig = px.area(
        df_totales,
        x='Semana',
        y='Producción_Kg',
        title="Volumen Semanal Cosechado Consolidado (Kg Totales de Todos los Lotes)",
        labels={'Producción_Kg': 'Kg Cosechados', 'Semana': 'Semana del Año'},
        markers=True
    )
    fig.update_traces(line_color='#059669', fillcolor='rgba(5, 150, 105, 0.25)')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
