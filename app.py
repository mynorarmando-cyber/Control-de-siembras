import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Matriz Interactiva de Siembra y Cosecha",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Matriz Directa de Planificación Agrícola")
st.caption("Escribe el nombre del vegetal (ej. **Ejote**) en la semana donde iniciará la siembra. El sistema proyectará automáticamente todo el ciclo y la curva de cosecha hacia la derecha.")

# ---------------------------------------------------------
# 1. PARÁMETROS DE CULTIVOS Y CURVAS
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
if 'matriz_entrada' not in st.session_state:
    filas_iniciales = []
    for l in LOTES:
        fila = {'Finca': l['Finca'], 'Lote': l['Lote'], 'Área (Ha)': l['Area_Ha']}
        for s in range(1, 53):
            fila[f"S{s}"] = ""
        filas_iniciales.append(fila)
    
    # Ejemplo inicial: Ejote en S2 para Lote 1, y en S5 para Lote 2
    filas_iniciales[0]['S2'] = 'Ejote'
    filas_iniciales[1]['S5'] = 'Ejote'
    
    st.session_state['matriz_entrada'] = pd.DataFrame(filas_iniciales)

# ---------------------------------------------------------
# 3. EDITOR INTERACTIVO DIRECTO EN LA MATRIZ
# ---------------------------------------------------------
st.subheader("📋 Matriz Semanal de Entrada (Edita directamente las celdas)")
st.info("💡 **Instrucciones:** Escribe **'Ejote'** o **'Broccoli'** en la semana donde quieras sembrar. Deja la celda vacía para borrar una siembra.")

# Matriz donde el usuario edita
matriz_editada = st.data_editor(
    st.session_state['matriz_entrada'],
    use_container_width=True,
    height=250,
    key="editor_matriz_directa"
)

st.session_state['matriz_entrada'] = matriz_editada

# ---------------------------------------------------------
# 4. PROCESAMIENTO Y PROYECCIÓN AUTOMÁTICA DE LA CURVA
# ---------------------------------------------------------
matriz_proyectada = []
registros_cosecha = []
conflictos = []

for idx, row in matriz_editada.iterrows():
    finca = row['Finca']
    lote = row['Lote']
    area = row['Área (Ha)']
    
    # Crear estructura para la matriz calculada visual
    fila_calculada = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
    mapa_semanas = {s: [] for s in range(1, 53)}
    
    # 1. Detectar en qué semanas el usuario escribió un cultivo
    for s in range(1, 53):
        valor_celda = str(row[f"S{s}"]).strip()
        
        # Si la celda contiene el nombre de un cultivo válido o texto de siembra
        for nombre_cultivo, cfg in CULTIVOS_CONFIG.items():
            if nombre_cultivo.lower() in valor_celda.lower():
                # Desplegar todo el ciclo a partir de esta semana 's'
                duracion_ocupada = cfg['duracion_total'] + cfg['descanso_post']
                
                for sem_rel, sem_abs in enumerate(range(s, min(s + duracion_ocupada, 53)), start=1):
                    if sem_rel == 1:
                        mapa_semanas[sem_abs].append(f"🌱 {nombre_cultivo}")
                    elif sem_rel in cfg['cosecha_pct']:
                        pct = cfg['cosecha_pct'][sem_rel]
                        kg_cosecha = area * RENDIMIENTO_BASE_KG_HA * pct
                        mapa_semanas[sem_abs].append(f"🟢 {int(kg_cosecha):,} Kg")
                        
                        registros_cosecha.append({
                            'Semana': sem_abs,
                            'Lote': f"{finca}-{lote}",
                            'Cultivo': nombre_cultivo,
                            'Producción_Kg': kg_cosecha
                        })
                    elif sem_rel <= cfg['duracion_total']:
                        mapa_semanas[sem_abs].append("▫️ Dev")
                    else:
                        mapa_semanas[sem_abs].append("🧹 Descanso")

    # 2. Construir la fila final con textos/iconos o alertas de choque
    for s in range(1, 53):
        eventos = mapa_semanas[s]
        if len(eventos) > 1:
            conflictos.append(f"⚠️ **Solapamiento:** Finca **{finca}** - Lote **{lote}** tiene ciclos cruzados en la **Semana {s}**.")
            fila_calculada[f"S{s}"] = "🔴 CHOQUE"
        elif len(eventos) == 1:
            fila_calculada[f"S{s}"] = eventos[0]
        else:
            fila_calculada[f"S{s}"] = ""
            
    matriz_proyectada.append(fila_calculada)

df_matriz_visual = pd.DataFrame(matriz_proyectada)
df_cosecha = pd.DataFrame(registros_cosecha)

# ---------------------------------------------------------
# 5. VISUALIZACIÓN DE RESULTADOS Y CURVA
# ---------------------------------------------------------
st.divider()

if conflictos:
    st.error("🚨 **CONFLICTOS DE ESPACIO DETECTADOS:**")
    for conf in set(conflictos):
        st.warning(conf)

st.subheader("🖼️ Vista Resultado: Proyección Automática del Ciclo Completo")
st.caption("Esta tabla muestra cómo se armó la curva automáticamente a la derecha de la semana donde pusiste el nombre del cultivo.")
st.dataframe(df_matriz_visual, use_container_width=True, height=250)

st.divider()

# GRÁFICA DE LA CURVA CONSOLIDADA
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
    
    # Desglose por lote
    fig_lotes = px.bar(
        df_cosecha,
        x='Semana',
        y='Producción_Kg',
        color='Lote',
        title="Aporte de cada Lote a la Curva Semanal",
        labels={'Producción_Kg': 'Kg Cosechados'}
    )
    fig_lotes.update_xaxes(dtick=1)
    st.plotly_chart(fig_lotes, use_container_width=True)
