import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Planificador Agrícola Interactivo",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------------------------------------
# 1. ESTADO GLOBAL (SESSION STATE)
# ---------------------------------------------------------

# Catalogos de Vegetales y sus Curvas de Cosecha (% de rendimiento por semana relativa)
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
        }
    }

# Catalogos de Fincas y Lotes
if 'lotes_db' not in st.session_state:
    st.session_state['lotes_db'] = pd.DataFrame([
        {'Finca': 'TM', 'Lote': 'Lote 1', 'Area_Ha': 1.05},
        {'Finca': 'TM', 'Lote': 'Lote 2', 'Area_Ha': 0.80},
        {'Finca': 'NP', 'Lote': 'NP-1', 'Area_Ha': 1.20},
        {'Finca': 'CH', 'Lote': 'CH-8', 'Area_Ha': 0.90},
    ])

# Registro de Siembras (Finca, Lote, Cultivo, Semana_Inicio)
if 'siembras_registradas' not in st.session_state:
    st.session_state['siembras_registradas'] = [
        {'Finca': 'TM', 'Lote': 'Lote 1', 'Cultivo': 'Ejote', 'Semana_Inicio': 2},
        {'Finca': 'TM', 'Lote': 'Lote 2', 'Cultivo': 'Ejote', 'Semana_Inicio': 5}
    ]

RENDIMIENTO_BASE_KG_HA = 11000

# ---------------------------------------------------------
# 2. ESTRUCTURA PRINCIPAL DE LA APP (PESTAÑAS)
# ---------------------------------------------------------
st.title("🌾 Sistema de Planificación Agrícola y Cosechas")

tab_matriz, tab_programar, tab_vegetales, tab_lotes = st.tabs([
    "📋 Matriz de Cosecha y Curva", 
    "➕ Asignar / Desplazar Siembras (Automático)", 
    "🌱 Gestionar Vegetales y Ciclos", 
    "🚜 Gestionar Fincas y Lotes"
])

# ---------------------------------------------------------
# PESTAÑA 1: MATRIZ Y CURVAS (CÁLCULO Y VISUALIZACIÓN EN TIEMPO REAL)
# ---------------------------------------------------------
with tab_matriz:
    st.subheader("📋 Matriz Semanal de Proyección Automática (S1 a S52)")
    
    lotes_df = st.session_state['lotes_db']
    veg_db = st.session_state['vegetales_db']
    siembras = st.session_state['siembras_registradas']
    
    matriz_filas = []
    registros_cosecha = []
    conflictos = []
    
    for idx, l_row in lotes_df.iterrows():
        finca, lote, area = l_row['Finca'], l_row['Lote'], l_row['Area_Ha']
        fila_matriz = {'Finca': finca, 'Lote': lote, 'Área (Ha)': area}
        
        # Buscar siembras de este lote
        siembras_lote = [s for s in siembras if s['Finca'] == finca and s['Lote'] == lote]
        
        mapa_semanas = {s: [] for s in range(1, 53)}
        
        for s_data in siembras_lote:
            crop = s_data['Cultivo']
            sem_i = s_data['Semana_Inicio']
            
            if crop in veg_db:
                cfg = veg_db[crop]
                dur_total = cfg['duracion_total'] + cfg['descanso_post']
                
                for sem_rel, sem_abs in enumerate(range(sem_i, min(sem_i + dur_total, 53)), start=1):
                    if sem_rel == 1:
                        mapa_semanas[sem_abs].append(f"🌱 {crop}")
                    elif sem_rel in cfg['cosecha_pct']:
                        pct = cfg['cosecha_pct'][sem_rel]
                        kg = area * RENDIMIENTO_BASE_KG_HA * pct
                        mapa_semanas[sem_abs].append(f"🟢 {int(kg):,} Kg")
                        
                        registros_cosecha.append({
                            'Semana': sem_abs,
                            'Lote': f"{finca}-{lote}",
                            'Cultivo': crop,
                            'Producción_Kg': kg
                        })
                    elif sem_rel <= cfg['duracion_total']:
                        mapa_semanas[sem_abs].append("▫️ Dev")
                    else:
                        mapa_semanas[sem_abs].append("🧹 Descanso")

        for s in range(1, 53):
            eventos = mapa_semanas[s]
            if len(eventos) > 1:
                conflictos.append(f"⚠️ Solapamiento en **{finca}-{lote}**, Semana {s}.")
                fila_matriz[f"S{s}"] = "🔴 CHOQUE"
            elif len(eventos) == 1:
                fila_matriz[f"S{s}"] = eventos[0]
            else:
                fila_matriz[f"S{s}"] = ""
                
        matriz_filas.append(fila_matriz)
        
    df_matriz_visual = pd.DataFrame(matriz_filas)
    df_cosecha = pd.DataFrame(registros_cosecha)

    if conflictos:
        st.error("🚨 **CONFLICTOS DETECTADOS EN LA PLANIFICACIÓN:**")
        for c in set(conflictos): st.warning(c)

    st.dataframe(df_matriz_visual, use_container_width=True, height=280)

    st.divider()
    st.subheader("📈 Curva Total Consolidada de Cosecha (S1 a S52)")

    if not df_cosecha.empty:
        df_totales = df_cosecha.groupby('Semana')['Producción_Kg'].sum().reset_index()
        df_full = pd.DataFrame({'Semana': range(1, 53)})
        df_totales = pd.merge(df_full, df_totales, on='Semana', how='left').fillna(0)
        
        fig = px.area(
            df_totales, x='Semana', y='Producción_Kg',
            title="Volumen Semanal Cosechado Consolidado (Kg Totales de Todos los Lotes)",
            labels={'Producción_Kg': 'Kg Cosechados', 'Semana': 'Semana del Año'},
            markers=True
        )
        fig.update_traces(line_color='#059669', fillcolor='rgba(5, 150, 105, 0.25)')
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 2: PROGRAMAR / ASIGNAR CULTIVOS EN TIEMPO REAL
# ---------------------------------------------------------
with tab_programar:
    st.subheader("⚡ Asignar o Desplazar Siembras en Tiempo Real")
    st.caption("Selecciona el vegetal de la lista desplegable (evita errores de digitación) y la semana de inicio. **Todo se actualiza automáticamente**.")

    # Formulario rápido intercativo
    col_f, col_l, col_v, col_s = st.columns(4)
    with col_f:
        fincas_opt = st.session_state['lotes_db']['Finca'].unique()
        finca_sel = st.selectbox("Seleccionar Finca:", fincas_opt)
    with col_l:
        lotes_opt = st.session_state['lotes_db'][st.session_state['lotes_db']['Finca'] == finca_sel]['Lote'].unique()
        lote_sel = st.selectbox("Seleccionar Lote:", lotes_opt)
    with col_v:
        veg_opt = list(st.session_state['vegetales_db'].keys())
        veg_sel = st.selectbox("Seleccionar Vegetal:", veg_opt)
    with col_s:
        sem_sel = st.number_input("Semana de Inicio (1-52):", min_value=1, max_value=45, value=1)

    if st.button("➕ Agregar / Mover Siembra", type="primary", use_container_width=True):
        st.session_state['siembras_registradas'].append({
            'Finca': finca_sel, 'Lote': lote_sel, 'Cultivo': veg_sel, 'Semana_Inicio': sem_sel
        })
        st.success(f"¡Siembra de {veg_sel} asignada a {finca_sel}-{lote_sel} en la Semana {sem_sel}!")
        st.rerun()

    st.divider()
    st.markdown("### 📝 Siembras Programadas Activas (Edita directamente la semana o borra filas)")
    
    df_siembras_edit = pd.DataFrame(st.session_state['siembras_registradas'])
    
    if not df_siembras_edit.empty:
        # Editor interactivo directo que reacciona instantáneamente sin presionar actualizar
        df_siembras_modificado = st.data_editor(
            df_siembras_edit,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Cultivo": st.column_config.SelectboxColumn("Vegetal", options=veg_opt, required=True),
                "Semana_Inicio": st.column_config.NumberColumn("Semana de Inicio", min_value=1, max_value=52, step=1)
            },
            key="editor_siembras_instantaneo"
        )
        st.session_state['siembras_registradas'] = df_siembras_modificado.to_dict('records')

# ---------------------------------------------------------
# PESTAÑA 3: GESTIONAR VEGETALES Y CURVAS DE CICLO
# ---------------------------------------------------------
with tab_vegetales:
    st.subheader("🌱 Configuración de Vegetales y Curvas de Cosecha")
    
    col_v1, col_v2 = st.columns([1, 1])
    
    with col_v1:
        st.markdown("### Agregar / Modificar Vegetal")
        nuevo_veg_nombre = st.text_input("Nombre del Vegetal (ej. Ejote Fino, China, etc.):")
        dur_total = st.number_input("Duración total del ciclo (Semanas):", min_value=1, value=11)
        dur_desc = st.number_input("Semanas de descanso post-cosecha:", min_value=0, value=2)
        
        st.caption("Distribución de Cosecha (% por semana del ciclo):")
        sem_cos_1 = st.number_input("Semana Cosecha 1:", value=9)
        pct_cos_1 = st.number_input("% Cosecha 1:", value=0.30)
        
        sem_cos_2 = st.number_input("Semana Cosecha 2:", value=10)
        pct_cos_2 = st.number_input("% Cosecha 2:", value=0.45)
        
        if st.button("💾 Guardar Vegetal / Curva"):
            if nuevo_veg_nombre:
                st.session_state['vegetales_db'][nuevo_veg_nombre] = {
                    'duracion_total': dur_total,
                    'descanso_post': dur_desc,
                    'cosecha_pct': {int(sem_cos_1): pct_cos_1, int(sem_cos_2): pct_cos_2}
                }
                st.success(f"Vegetal '{nuevo_veg_nombre}' guardado correctamente.")
                st.rerun()

    with col_v2:
        st.markdown("### Vegetales Configurados Actualmente")
        st.json(st.session_state['vegetales_db'])

# ---------------------------------------------------------
# PESTAÑA 4: GESTIONAR FINCAS Y LOTES
# ---------------------------------------------------------
with tab_lotes:
    st.subheader("🚜 Gestión de Fincas y Lotes")
    st.caption("Edita, agrega o elimina lotes en esta tabla interactiva:")
    
    df_lotes_editado = st.data_editor(
        st.session_state['lotes_db'],
        num_rows="dynamic",
        use_container_width=True,
        key="editor_lotes_fincas"
    )
    st.session_state['lotes_db'] = df_lotes_editado
