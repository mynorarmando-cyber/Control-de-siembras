import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Planificador Agrícola Dinámico",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Planificador Agrícola: Control de Ciclos y Curva en Tiempo Real")

# ---------------------------------------------------------
# 1. CATALOGO DE VEGETALES Y CURVAS DE COSECHA
# ---------------------------------------------------------
if 'vegetales_db' not in st.session_state:
    st.session_state['vegetales_db'] = {
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

# ---------------------------------------------------------
# 2. CONFIGURACIÓN DE LOTES Y SIEMBRAS
# ---------------------------------------------------------
if 'plan_lotes' not in st.session_state:
    st.session_state['plan_lotes'] = [
        {'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05, 'Cultivo': 'Ejote', 'Semana_Inicio': 2, 'Activo': True},
        {'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80, 'Cultivo': 'Ejote', 'Semana_Inicio': 5, 'Activo': True},
        {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20, 'Cultivo': 'Broccoli', 'Semana_Inicio': 8, 'Activo': True},
        {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90, 'Cultivo': 'Ejote', 'Semana_Inicio': 12, 'Activo': True},
    ]

# ---------------------------------------------------------
# 3. PESTAÑAS DE TRABAJO
# ---------------------------------------------------------
tab_principal, tab_gestion_veg = st.tabs([
    "📋 Planificación y Matriz (S1 a S52)", 
    "🌱 Configurar Vegetales y Curvas"
])

# ---------------------------------------------------------
# PESTAÑA 1: PLANIFICACIÓN Y CONTROL DE CICLO
# ---------------------------------------------------------
with tab_principal:
    st.subheader("🎛️ Panel de Control: Desplazar Ciclo y Seleccionar Vegetal")
    st.caption("Selecciona el vegetal de la lista y **desplaza la Semana de Inicio** para mover todo el ciclo completo a lo largo del año en tiempo real.")

    veg_lista = list(st.session_state['vegetales_db'].keys())

    # Generar controles interactivos fila por fila
    for idx, item in enumerate(st.session_state['plan_lotes']):
        c_lote, c_veg, c_sem, c_act = st.columns([2, 2, 4, 1])
        
        with c_lote:
            st.markdown(f"**{item['Finca']} - {item['Lote']}** ({item['Area_Ha']} Ha)")
        
        with c_veg:
            # Lista desplegable para evitar errores de digitación
            nuevo_veg = st.selectbox(
                "Vegetal:",
                options=veg_lista,
                index=veg_lista.index(item['Cultivo']) if item['Cultivo'] in veg_lista else 0,
                key=f"veg_{idx}"
            )
            st.session_state['plan_lotes'][idx]['Cultivo'] = nuevo_veg

        with c_sem:
            # Control interactivo para mover la semana de inicio y desplazar todo el ciclo
            nueva_sem = st.slider(
                "Mover Semana de Inicio:",
                min_value=1,
                max_value=45,
                value=int(item['Semana_Inicio']),
                key=f"sem_{idx}"
            )
            st.session_state['plan_lotes'][idx]['Semana_Inicio'] = nueva_sem
            
        with c_act:
            activo = st.checkbox("Incluir", value=item['Activo'], key=f"act_{idx}")
            st.session_state['plan_lotes'][idx]['Activo'] = activo

    st.divider()

    # ---------------------------------------------------------
    # CONSTRUCCIÓN AUTOMÁTICA DE LA MATRIZ (S1 A S52)
    # ---------------------------------------------------------
    st.subheader("📋 Matriz Semanal de Proyección (S1 a S52)")
    
    matriz_filas = []
    registros_cosecha = []
    
    for item in st.session_state['plan_lotes']:
        if not item['Activo']:
            continue
            
        finca = item['Finca']
        lote = item['Lote']
        area = item['Area_Ha']
        crop = item['Cultivo']
        sem_i = item['Semana_Inicio']
        
        fila_matriz = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area, 'Vegetal': crop}
        
        if crop in st.session_state['vegetales_db']:
            cfg = st.session_state['vegetales_db'][crop]
            dur_total = cfg['duracion_total'] + cfg['descanso_post']
            
            for s in range(1, 53):
                sem_ciclo = s - sem_i + 1
                
                if 1 <= sem_ciclo <= dur_total:
                    if sem_ciclo in cfg['cosecha_pct']:
                        pct = cfg['cosecha_pct'][sem_ciclo]
                        kg = area * RENDIMIENTO_BASE_KG_HA * pct
                        fila_matriz[f"S{s}"] = f"🟢 {int(kg):,} Kg"
                        
                        registros_cosecha.append({
                            'Semana': s,
                            'Lote': f"{finca}-{lote}",
                            'Cultivo': crop,
                            'Producción_Kg': kg
                        })
                    elif sem_ciclo == 1:
                        fila_matriz[f"S{s}"] = f"🌱 {crop}"
                    elif sem_ciclo <= cfg['duracion_total']:
                        fila_matriz[f"S{s}"] = "▫️ Dev"
                    else:
                        fila_matriz[f"S{s}"] = "🧹 Descanso"
                else:
                    fila_matriz[f"S{s}"] = ""
                    
        matriz_filas.append(fila_matriz)
        
    df_matriz_visual = pd.DataFrame(matriz_filas)
    df_cosecha = pd.DataFrame(registros_cosecha)

    st.dataframe(df_matriz_visual, use_container_width=True, height=260)

    # ---------------------------------------------------------
    # GRÁFICA DE LA CURVA CONSOLIDADA
    # ---------------------------------------------------------
    st.divider()
    st.subheader("📈 Curva Total Consolidada de Cosecha")

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

# ---------------------------------------------------------
# PESTAÑA 2: GESTIÓN DE VEGETALES Y CURVAS
# ---------------------------------------------------------
with tab_gestion_veg:
    st.subheader("🌱 Agregar / Modificar Vegetales")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        nombre_v = st.text_input("Nombre del Vegetal:")
        dur_t = st.number_input("Duración total del ciclo (Semanas):", min_value=1, value=11)
        dur_d = st.number_input("Semanas de descanso:", min_value=0, value=2)
        
        st.markdown("**Distribución de Cosecha:**")
        s1 = st.number_input("Semana Cosecha 1:", value=9)
        p1 = st.number_input("% Cosecha 1 (ej. 0.30):", value=0.30)
        
        s2 = st.number_input("Semana Cosecha 2:", value=10)
        p2 = st.number_input("% Cosecha 2 (ej. 0.45):", value=0.45)
        
        s3 = st.number_input("Semana Cosecha 3:", value=11)
        p3 = st.number_input("% Cosecha 3 (ej. 0.25):", value=0.25)
        
        if st.button("💾 Guardar Vegetal", type="primary"):
            if nombre_v:
                st.session_state['vegetales_db'][nombre_v] = {
                    'duracion_total': dur_t,
                    'descanso_post': dur_d,
                    'cosecha_pct': {int(s1): p1, int(s2): p2, int(s3): p3}
                }
                st.success(f"¡Vegetal '{nombre_v}' guardado!")
                st.rerun()

    with col_b:
        st.markdown("### Vegetales Disponibles Actuales")
        st.json(st.session_state['vegetales_db'])
