import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Planificación Agrícola Dinámica",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTADOS INICIALES
# ---------------------------------------------------------

# Parámetros del cultivo (Ejote)
# Duración total = 11 semanas. Cosecha ocurre solo en las semanas 9, 10 y 11 del ciclo.
CURVA_EJOTE = {
    'duracion_total': 11,
    'descanso_post': 2,
    # % de cosecha en la semana relativa del ciclo
    'cosecha_pct': {9: 0.30, 10: 0.45, 11: 0.25}
}

RENDIMIENTO_BASE_KG_HA = 11000  # Rendimiento promedio por hectárea

if 'lotes_plan' not in st.session_state:
    # Estado inicial de los lotes y su semana de inicio
    st.session_state['lotes_plan'] = [
        {'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05, 'Cultivo': 'Ejote', 'Semana_Inicio': 2},
        {'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80, 'Cultivo': 'Ejote', 'Semana_Inicio': 5},
        {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20, 'Cultivo': 'Ejote', 'Semana_Inicio': 8},
        {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90, 'Cultivo': 'Ejote', 'Semana_Inicio': 12},
    ]

st.title("🌾 Planificador Agrícola: Control de Curva Interactivo")

# ---------------------------------------------------------
# 2. CONTROL DIRECTO DE LA CURVA (Ajustar Semanas)
# ---------------------------------------------------------
st.subheader("🎛️ Desplazar Curva por Lote (Ajuste Interactivo)")
st.caption("Cambia la **Semana de Inicio** para desplazar la cosecha hacia adelante o hacia atrás en el calendario.")

# Crear controles directos para mover la semana de inicio de cada lote
cols_lotes = st.columns(len(st.session_state['lotes_plan']))

for idx, lote_data in enumerate(st.session_state['lotes_plan']):
    with cols_lotes[idx]:
        st.markdown(f"**{lote_data['Finca']} - {lote_data['Lote']}** ({lote_data['Area_Ha']} Ha)")
        
        # Selector que desplaza la semana de inicio
        nueva_sem = st.number_input(
            f"Inicio (S1-S52)",
            min_value=1,
            max_value=45,
            value=int(lote_data['Semana_Inicio']),
            key=f"sem_in_{idx}"
        )
        # Actualizar estado
        st.session_state['lotes_plan'][idx]['Semana_Inicio'] = nueva_sem

# ---------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MATRIZ SIN TEXTO REPETIDO
# ---------------------------------------------------------

registros_matriz = []
registros_cosecha = []

for lote in st.session_state['lotes_plan']:
    finca = lote['Finca']
    nombre_lote = lote['Lote']
    area = lote['Area_Ha']
    sem_inicio = lote['Semana_Inicio']
    
    fila = {'Finca': finca, 'Lote': nombre_lote, 'Área (Ha)': area}
    
    # Evaluar las 52 semanas del año
    for s in range(1, 53):
        # Calcular semana relativa dentro del ciclo del cultivo
        sem_ciclo = s - sem_inicio + 1
        
        if 1 <= sem_ciclo <= CURVA_EJOTE['duracion_total']:
            if sem_ciclo in CURVA_EJOTE['cosecha_pct']:
                # Muestra los Kg/Cajas reales cosechados en esa semana exacta
                pct = CURVA_EJOTE['cosecha_pct'][sem_ciclo]
                kg_cosecha = area * RENDIMIENTO_BASE_KG_HA * pct
                
                # Texto limpio en la matriz (Ejemplo: "🍿 1,500 Kg")
                fila[f"S{s}"] = f"🟢 {int(kg_cosecha):,} Kg"
                
                registros_cosecha.append({
                    'Semana': s,
                    'Lote': f"{finca}-{nombre_lote}",
                    'Producción_Kg': kg_cosecha
                })
            elif sem_ciclo == 1:
                fila[f"S{s}"] = "🌱 Siembra"
            else:
                # Mantiene la celda limpia en lugar de repetir "Ejote"
                fila[f"S{s}"] = "▫️ Crecimiento"
        else:
            fila[f"S{s}"] = ""  # Celda vacía sin texto
            
    registros_matriz.append(fila)

df_matriz = pd.DataFrame(registros_matriz)
df_cosecha = pd.DataFrame(registros_cosecha)

# ---------------------------------------------------------
# 4. VISUALIZACIÓN DE MATRIZ Y CURVA CONSOLIDADA
# ---------------------------------------------------------

st.divider()

# TABLA ESTILO EXCEL
st.subheader("📋 Matriz Semanal de Cosecha")
st.caption("Visualiza únicamente las semanas clave (Siembra, Crecimiento y Cosecha con Kg exactos).")
st.dataframe(df_matriz, use_container_width=True, height=250)

# GRÁFICA DE LA CURVA CONSOLIDADA
st.subheader("📈 Curva Total Consolidada de Cosecha (Semanas 1 a 52)")

if not df_cosecha.empty:
    # Agrupar total cosechado por semana (suma de todos los lotes)
    df_totales = df_cosecha.groupby('Semana')['Producción_Kg'].sum().reset_index()
    
    # Asegurar rango completo S1-S52 en el gráfico
    df_full = pd.DataFrame({'Semana': range(1, 53)})
    df_totales = pd.merge(df_full, df_totales, on='Semana', how='left').fillna(0)
    
    # Gráfica de área que muestra el comportamiento de la curva
    fig = px.area(
        df_totales,
        x='Semana',
        y='Producción_Kg',
        title="Volumen Semanal Acumulado de Ejote (Kg)",
        labels={'Producción_Kg': 'Kg Totales Cosechados', 'Semana': 'Semana del Año'},
        markers=True
    )
    fig.update_traces(line_color='#059669', fillcolor='rgba(5, 150, 105, 0.25)')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
    
    # Desglose gráfico por lote
    fig_lotes = px.bar(
        df_cosecha,
        x='Semana',
        y='Producción_Kg',
        color='Lote',
        title="Aporte por Lote a la Cosecha Semanal",
        labels={'Producción_Kg': 'Kg Cosechados'}
    )
    fig_lotes.update_xaxes(dtick=1)
    st.plotly_chart(fig_lotes, use_container_width=True)