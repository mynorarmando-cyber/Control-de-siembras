import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

st.set_page_config(
    page_title="Matriz Agrícola Interactiva",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Matriz Semanal de Planificación Agrícola")
st.caption("Selecciona el vegetal directamente desde el menú desplegable en la semana donde iniciará la siembra.")

# ---------------------------------------------------------
# 1. PARÁMETROS DE CULTIVOS Y CURVAS DE COSECHA
# ---------------------------------------------------------
CURVAS_CULTIVOS = {
    'Ejote': {
        'duracion_total': 11,
        'descanso_post': 2,
        'cosecha_pct': {9: 0.30, 10: 0.45, 11: 0.25}
    },
    'Broccoli': {
        'duracion_total': 14,
        'descanso_post': 3,
        'cosecha_pct': {11: 0.20, 12: 0.50, 13: 0.30}
    },
    'Zucchini': {
        'duracion_total': 10,
        'descanso_post': 2,
        'cosecha_pct': {7: 0.30, 8: 0.40, 9: 0.30}
    }
}

RENDIMIENTO_BASE_KG_HA = 11000

# Lotes Iniciales
LOTES_BASE = [
    {'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05},
    {'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80},
    {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20},
    {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90},
]

# ---------------------------------------------------------
# 2. INICIALIZAR MATRIZ DE TRABAJO
# ---------------------------------------------------------
if 'matriz_entrada' not in st.session_state:
    filas = []
    for l in LOTES_BASE:
        f = {'Finca': l['Finca'], 'Lote': l['Lote'], 'Área (Ha)': l['Area_Ha']}
        for s in range(1, 53):
            f[f"S{s}"] = ""
        filas.append(f)
    
    # Ejemplo inicial
    filas[0]['S2'] = 'Ejote'
    filas[1]['S5'] = 'Broccoli'
    st.session_state['matriz_entrada'] = pd.DataFrame(filas)

# ---------------------------------------------------------
# 3. CONFIGURAR HOJA INTERACTIVA (AgGrid)
# ---------------------------------------------------------
df_trabajo = st.session_state['matriz_entrada']

gb = GridOptionsBuilder.from_dataframe(df_trabajo)
gb.configure_default_column(editable=True, groupable=True)

# Fijar columnas principales
gb.configure_column("Finca", editable=False, pinned="left", width=90)
gb.configure_column("Lote", editable=False, pinned="left", width=100)
gb.configure_column("Área (Ha)", editable=False, pinned="left", width=100)

# Configurar cada columna de semana (S1-S52) con Lista Desplegable
opciones_vegetales = [""] + list(CURVAS_CULTIVOS.keys())

for s in range(1, 53):
    gb.configure_column(
        f"S{s}",
        cellEditor='agSelectCellEditor',
        cellEditorParams={'values': opciones_vegetales},
        width=85
    )

grid_options = gb.build()

st.subheader("📋 Matriz Semanal (Haz doble clic en una celda para elegir el vegetal)")

# Renderizar la tabla interactiva
grid_response = AgGrid(
    df_trabajo,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    data_return_mode=DataReturnMode.ALWAYS,
    fit_columns_on_grid_load=False,
    height=250,
    theme='balham'
)

# Guardar cambios
df_actualizado = pd.DataFrame(grid_response['data'])
st.session_state['matriz_entrada'] = df_actualizado

# ---------------------------------------------------------
# 4. CALCULAR CICLOS Y CURVAS EN TIEMPO REAL
# ---------------------------------------------------------
registros_cosecha = []
matriz_proyectada = []

for idx, row in df_actualizado.iterrows():
    finca = row['Finca']
    lote = row['Lote']
    area = float(row['Área (Ha)'])
    
    fila_res = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
    mapa_semanas = {s: [] for s in range(1, 53)}
    
    # Detectar siembras
    for s in range(1, 53):
        val = str(row[f"S{s}"]).strip()
        if val in CURVAS_CULTIVOS:
            cfg = CURVAS_CULTIVOS[val]
            dur_total = cfg['duracion_total'] + cfg['descanso_post']
            
            for sem_rel, sem_abs in enumerate(range(s, min(s + dur_total, 53)), start=1):
                if sem_rel == 1:
                    mapa_semanas[sem_abs].append(f"🌱 {val}")
                elif sem_rel in cfg['cosecha_pct']:
                    pct = cfg['cosecha_pct'][sem_rel]
                    kg = area * RENDIMIENTO_BASE_KG_HA * pct
                    mapa_semanas[sem_abs].append(f"🟢 {int(kg):,} Kg")
                    
                    registros_cosecha.append({
                        'Semana': sem_abs,
                        'Lote': f"{finca}-{lote}",
                        'Cultivo': val,
                        'Producción_Kg': kg
                    })
                elif sem_rel <= cfg['duracion_total']:
                    mapa_semanas[sem_abs].append("▫️ Dev")
                else:
                    mapa_semanas[sem_abs].append("🧹 Descanso")

    for s in range(1, 53):
        eventos = mapa_semanas[s]
        if len(eventos) > 1:
            fila_res[f"S{s}"] = "🔴 CHOQUE"
        elif len(eventos) == 1:
            fila_res[f"S{s}"] = eventos[0]
        else:
            fila_res[f"S{s}"] = ""
            
    matriz_proyectada.append(fila_res)

df_matriz_calculada = pd.DataFrame(matriz_proyectada)
df_cosecha = pd.DataFrame(registros_cosecha)

# ---------------------------------------------------------
# 5. RESULTADO VISUAL Y GRÁFICA
# ---------------------------------------------------------
st.divider()
st.subheader("🖼️ Vista Calculada: Ciclos y Cosechas Proyectadas")
st.dataframe(df_matriz_calculada, use_container_width=True, height=250)

st.divider()
st.subheader("📈 Curva Total Consolidada de Cosecha (Kg Totales S1-S52)")

if not df_cosecha.empty:
    df_totales = df_cosecha.groupby('Semana')['Producción_Kg'].sum().reset_index()
    df_full = pd.DataFrame({'Semana': range(1, 53)})
    df_totales = pd.merge(df_full, df_totales, on='Semana', how='left').fillna(0)
    
    fig = px.area(
        df_totales, x='Semana', y='Producción_Kg',
        title="Volumen Semanal Cosechado Consolidado (Kg Totales)",
        labels={'Producción_Kg': 'Kg Cosechados', 'Semana': 'Semana del Año'},
        markers=True
    )
    fig.update_traces(line_color='#059669', fillcolor='rgba(5, 150, 105, 0.25)')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
