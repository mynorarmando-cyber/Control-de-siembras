import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Planificador Multiciclo Agrícola",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Planificador Agrícola: Múltiples Siembras y Desplazamiento de Ciclo")

# ---------------------------------------------------------
# 1. PARÁMETROS DEL CULTIVO (EJOTE)
# ---------------------------------------------------------
# Ciclo: 11 semanas totales. Cosecha en semanas 9, 10 y 11 del ciclo.
CURVA_EJOTE = {
    'duracion_total': 11,
    'descanso_post': 2,
    'cosecha_pct': {9: 0.30, 10: 0.45, 11: 0.25}
}
RENDIMIENTO_BASE_KG_HA = 11000

# ---------------------------------------------------------
# 2. PLANIFICADOR INTERACTIVO (Múltiples Siembras por Lote)
# ---------------------------------------------------------
st.subheader("📝 Tabla de Siembras Programadas")
st.caption("Puedes **agregar nuevas filas**, cambiar el cultivo, o **cambiar la Semana de Inicio** para mover todo el ciclo completo hacia adelante o hacia atrás.")

# Datos iniciales con MÚLTIPLES siembras en un mismo lote a lo largo del año
if 'siembras_df' not in st.session_state:
    st.session_state['siembras_df'] = pd.DataFrame([
        {'ID': 1, 'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05, 'Cultivo': 'Ejote', 'Semana_Inicio': 2},
        {'ID': 2, 'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05, 'Cultivo': 'Ejote', 'Semana_Inicio': 18}, # Segunda siembra en Lote 1
        {'ID': 3, 'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80, 'Cultivo': 'Ejote', 'Semana_Inicio': 5},
        {'ID': 4, 'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20, 'Cultivo': 'Ejote', 'Semana_Inicio': 8},
        {'ID': 5, 'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20, 'Cultivo': 'Ejote', 'Semana_Inicio': 24}, # Segunda siembra en NP-1
    ])

# Tabla editable donde el usuario puede modificar la semana de inicio o agregar siembras
df_editado = st.data_editor(
    st.session_state['siembras_df'],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "ID": None, # Ocultar columna ID
        "Semana_Inicio": st.column_config.NumberColumn(
            "Semana de Inicio (1-52)",
            help="Al cambiar este número, todo el ciclo (siembra, desarrollo y cosecha) se mueve en automático.",
            min_value=1,
            max_value=45,
            step=1
        ),
        "Area_Ha": st.column_config.NumberColumn("Área (Ha)", format="%.2f Ha")
    },
    key="editor_siembras"
)

# Guardar los cambios editados
st.session_state['siembras_df'] = df_editado

# ---------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MATRIZ Y CÁLCULO DE CURVAS
# ---------------------------------------------------------
registros_cosecha = []
conflictos = []

# Agrupar lotes únicos para construir las filas de la matriz
df_lotes_unicos = df_editado[['Finca', 'Lote', 'Area_Ha']].drop_duplicates()
matriz_filas = []

for _, lote_row in df_lotes_unicos.iterrows():
    finca = lote_row['Finca']
    lote = lote_row['Lote']
    area = lote_row['Area_Ha']
    
    fila_matriz = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
    
    # Buscar TODAS las siembras programadas para este lote
    siembras_lote = df_editado[(df_editado['Finca'] == finca) & (df_editado['Lote'] == lote)]
    
    # Evaluar la ocupación semana a semana de la 1 a la 52
    for s in range(1, 53):
        estado_semana = []
        
        for _, siembra in siembras_lote.iterrows():
            sem_i = siembra['Semana_Inicio']
            cultivo = siembra['Cultivo']
            sem_ciclo = s - sem_i + 1
            
            duracion_ocupada = CURVA_EJOTE['duracion_total'] + CURVA_EJOTE['descanso_post']
            
            if 1 <= sem_ciclo <= duracion_ocupada:
                if sem_ciclo in CURVA_EJOTE['cosecha_pct']:
                    # Calcular Kg producidos
                    pct = CURVA_EJOTE['cosecha_pct'][sem_ciclo]
                    kg_cosecha = area * RENDIMIENTO_BASE_KG_HA * pct
                    estado_semana.append(f"🟢 {int(kg_cosecha):,} Kg")
                    
                    registros_cosecha.append({
                        'Semana': s,
                        'Lote': f"{finca}-{lote}",
                        'Cultivo': cultivo,
                        'Producción_Kg': kg_cosecha
                    })
                elif sem_ciclo == 1:
                    estado_semana.append("🌱 Siembra")
                elif sem_ciclo <= CURVA_EJOTE['duracion_total']:
                    estado_semana.append("▫️ Dev")
                else:
                    estado_semana.append("🧹 Descanso")
                    
        # Si hay más de un evento activo en la misma semana, hay choque de siembras
        if len(estado_semana) > 1:
            conflictos.append(f"⚠️ **Solapamiento:** Finca **{finca}** - Lote **{lote}** tiene dos ciclos cruzados en la **Semana {s}**.")
            fila_matriz[f"S{s}"] = " 🔴 SOLAPADO "
        elif len(estado_semana) == 1:
            fila_matriz[f"S{s}"] = estado_semana[0]
        else:
            fila_matriz[f"S{s}"] = ""
            
    matriz_filas.append(fila_matriz)

df_matriz = pd.DataFrame(matriz_filas)
df_cosecha = pd.DataFrame(registros_cosecha)

# ---------------------------------------------------------
# 4. VISUALIZACIÓN DE MATRIZ Y CURVAS CONSOLIDADAS
# ---------------------------------------------------------
st.divider()

if conflictos:
    st.error("🚨 **ALERTAS DE SOLAPAMIENTO DE CICLOS EN EL MISMO LOTE:**")
    for conf in set(conflictos):
        st.warning(conf)

st.subheader("📋 Matriz Semanal de Cosecha y Ciclos (S1 a S52)")
st.caption("Visualiza las fases activas. Las celdas verdes muestran la cosecha en Kg reales.")
st.dataframe(df_matriz, use_container_width=True, height=300)

st.divider()

# GRÁFICA DE LA CURVA CONSOLIDADA
st.subheader("📈 Curva Total Consolidada de Cosecha (Semanas 1 a 52)")

if not df_cosecha.empty:
    # Agrupar total cosechado por semana (suma de TODOS los lotes y TODAS las siembras)
    df_totales = df_cosecha.groupby('Semana')['Producción_Kg'].sum().reset_index()
    
    # Rango completo S1-S52
    df_full = pd.DataFrame({'Semana': range(1, 53)})
    df_totales = pd.merge(df_full, df_totales, on='Semana', how='left').fillna(0)
    
    # Gráfica de la curva
    fig = px.area(
        df_totales,
        x='Semana',
        y='Producción_Kg',
        title="Volumen Semanal Acumulado de Ejote (Suma de Todas las Siembras)",
        labels={'Producción_Kg': 'Kg Totales Cosechados', 'Semana': 'Semana del Año'},
        markers=True
    )
    fig.update_traces(line_color='#059669', fillcolor='rgba(5, 150, 105, 0.25)')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
    
    # Desglose gráfico por Lote/Siembra
    fig_lotes = px.bar(
        df_cosecha,
        x='Semana',
        y='Producción_Kg',
        color='Lote',
        title="Aporte por Lote a la Curva Semanal",
        labels={'Producción_Kg': 'Kg Cosechados'}
    )
    fig_lotes.update_xaxes(dtick=1)
    st.plotly_chart(fig_lotes, use_container_width=True)
