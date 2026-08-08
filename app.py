import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Planificación de Siembras — V11.0",
    page_icon="🌱",
    layout="wide"
)

# Estilos CSS personalizados para replicar la interfaz web original
st.markdown("""
<style>
    :root {
        --ink: #1b2e26;
        --paper: #f6f5f0;
        --panel: #ffffff;
        --line: #dcd8cc;
        --forest: #1f4e3d;
        --muted: #6b7268;
        --alert: #b3261e;
        --gap-bg: #fbeae8;
        --split-head: #d9edf7;
        --split-head-fg: #1d394a;
        --ejote-bg: #ddebf7; --ejote-fg: #1f4e79;
        --broccoli-bg: #e2efda; --broccoli-fg: #375623;
        --grano-bg: #fce4d6; --grano-fg: #833c00;
        --china-bg: #e4dfec; --china-fg: #5f3f7a;
        --dulce-bg: #fff2cc; --dulce-fg: #7f6000;
        --inherited-bg: #fff3cd; --inherited-fg: #856404; --inherited-border: #ffeeba;
    }
    .main {
        background-color: var(--paper);
    }
    .stButton>button {
        background-color: var(--forest);
        color: white;
        border-radius: 5px;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #15382b;
        color: white;
    }
    .stat-card {
        background: #f0efe8;
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 10px;
        text-align: center;
    }
    .stat-card b {
        font-size: 16px;
        color: var(--forest);
        display: block;
    }
    .stat-card span {
        font-size: 11px;
        color: var(--muted);
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- INICIALIZACIÓN DE ESTADOS -----------------
if 'ciclos' not in st.session_state:
    st.session_state.ciclos = {
        "Ejote":    {"duracionBase": 11, "cosechas": [[10,0.35],[11,0.42],[12,0.23]], "color":"ejote", "coldExtend":True},
        "Broccoli": {"duracionBase": 15, "cosechas": [[10,0.10],[11,0.20],[12,0.17],[13,0.10],[14,0.23],[15,0.20]], "color":"broccoli", "coldExtend":False},
        "Grano":    {"duracionBase": 14, "cosechas": [[11,0.30],[12,0.36],[13,0.24],[14,0.10]], "color":"grano", "coldExtend":False},
        "China":    {"duracionBase": 13, "cosechas": [[10,0.11],[11,0.45],[12,0.37],[13,0.07]], "color":"china", "coldExtend":False},
        "Dulce":    {"duracionBase": 14, "cosechas": [[11,0.10],[12,0.20],[13,0.41],[14,0.29]], "color":"dulce", "coldExtend":False}
    }

if 'rendimientos' not in st.session_state:
    st.session_state.rendimientos = {
        "Ejote": {w: 10900 if w < 10 else (11900 if w < 28 else (11600 if w < 45 else 10900)) for w in range(1, 54)},
        "Broccoli": {w: 8000 if w < 10 else (10000 if w < 28 else (6500 if w < 45 else 8000)) for w in range(1, 54)},
        "China": {w: 7500 for w in range(1, 54)},
        "Dulce": {w: 12000 if w < 6 else (10000 if w < 15 else (7000 if w < 38 else 10500)) for w in range(1, 54)},
        "Grano": {w: 8250 for w in range(1, 54)}
    }

if 'fincas' not in st.session_state:
    st.session_state.fincas = ['NP', 'CH', 'TM', 'PV', 'SM']

if 'base_lotes' not in st.session_state:
    st.session_state.base_lotes = []
    area_seed = [1.0, 1.2, 0.8, 1.5, 1.1, 0.9, 1.3, 1.4]
    id_counter = 0
    for f in st.session_state.fincas:
        count = 40 if f == 'NP' else 30
        for i in range(1, count + 1):
            st.session_state.base_lotes.append({
                "id": f"{f}-{i}",
                "finca": f,
                "nombre": f"{f}-{i}",
                "area": area_seed[id_counter % len(area_seed)]
            })
            id_counter += 1

if 'expanded_lots' not in st.session_state:
    st.session_state.expanded_lots = {}

if 'plantings' not in st.session_state:
    st.session_state.plantings = {
        'NP-1': [{'year': 2026, 'weekInYear': 1, 'vegetal': 'Broccoli'}],
        'NP-1A': [{'year': 2026, 'weekInYear': 20, 'vegetal': 'Ejote'}],
        'NP-1B': [{'year': 2026, 'weekInYear': 20, 'vegetal': 'China'}],
        'NP-5': [{'year': 2026, 'weekInYear': 4, 'vegetal': 'Ejote'}],
        'CH-1': [{'year': 2026, 'weekInYear': 1, 'vegetal': 'China'}]
    }

# ----------------- FUNCIONES DE LÓGICA AGRÍCOLA -----------------
def abs_week(year, week_in_year):
    return (year - 2020) * 52 + week_in_year

def is_cold_season(week_in_year):
    return (week_in_year >= 45 or week_in_year <= 8)

def get_cycle_duration(vegetal, start_year, start_week):
    veg = st.session_state.ciclos.get(vegetal)
    if not veg:
        return 12
    base = veg["duracionBase"]
    if veg.get("coldExtend", False):
        end_week_approx = start_week + base - 1
        norm_end_week = ((end_week_approx - 1) % 52) + 1
        if is_cold_season(start_week) or is_cold_season(norm_end_week):
            return base + 1
    return base

def get_active_lotes_for_finca(finca_name):
    result = []
    finca_base = [l for l in st.session_state.base_lotes if l['finca'] == finca_name]
    for l in finca_base:
        if st.session_state.expanded_lots.get(l['id']):
            half_area = round(l['area'] / 2, 2)
            result.append({"id": l['id'] + 'A', "finca": finca_name, "nombre": l['id'] + 'A', "area": half_area, "parentId": l['id'], "isSplit": True})
            result.append({"id": l['id'] + 'B', "finca": finca_name, "nombre": l['id'] + 'B', "area": half_area, "parentId": l['id'], "isSplit": True})
        else:
            result.append({"id": l['id'], "finca": finca_name, "nombre": l['nombre'], "area": l['area'], "parentId": None, "isSplit": False})
    return result

def get_all_active_lotes_flat():
    all_lotes = []
    for f in st.session_state.fincas:
        all_lotes.extend(get_active_lotes_for_finca(f))
    return all_lotes

def find_active(lote_id, year, week_in_year):
    p_list = st.session_state.plantings.get(lote_id, [])
    current_abs = abs_week(year, week_in_year)
    for p in p_list:
        dur = get_cycle_duration(p['vegetal'], p['year'], p['weekInYear'])
        start_abs = abs_week(p['year'], p['weekInYear'])
        if start_abs <= current_abs < start_abs + dur:
            return p
    return None

def get_detailed_occupancy(lote_id, year, week_in_year):
    direct = find_active(lote_id, year, week_in_year)
    if direct:
        return {"planting": direct, "type": "direct", "sourceId": lote_id}
    
    if not lote_id.endswith('A') and not lote_id.endswith('B'):
        sub_a = find_active(lote_id + 'A', year, week_in_year)
        if sub_a:
            return {"planting": sub_a, "type": "inherited", "sourceId": lote_id + 'A'}
        sub_b = find_active(lote_id + 'B', year, week_in_year)
        if sub_b:
            return {"planting": sub_b, "type": "inherited", "sourceId": lote_id + 'B'}
            
    if lote_id.endswith('A') or lote_id.endswith('B'):
        base_id = lote_id[:-1]
        parent_act = find_active(base_id, year, week_in_year)
        if parent_act:
            return {"planting": parent_act, "type": "inherited", "sourceId": base_id}
            
    return None

def harvest_value(planting, year, week_in_year, area):
    c = st.session_state.ciclos.get(planting['vegetal'])
    if not c:
        return 0
    current_abs = abs_week(year, week_in_year)
    start_abs = abs_week(planting['year'], planting['weekInYear'])
    rel = current_abs - start_abs + 1
    
    cosecha = next((item for item in c['cosechas'] if item[0] == rel), None)
    if not cosecha:
        return 0
        
    factor_pct = cosecha[1]
    calendar_week = ((week_in_year - 1) % 52) + 1
    veg_rend_dict = st.session_state.rendimientos.get(planting['vegetal'], {})
    rendimiento_semanal_base = veg_rend_dict.get(calendar_week, 8000)
    
    return area * rendimiento_semanal_base * factor_pct

def get_total_harvest_all_fincas(year, week_in_year, target_veg):
    sum_val = 0
    active_lots = get_all_active_lotes_flat()
    for l in active_lots:
        p_list = st.session_state.plantings.get(l['id'], [])
        for p in p_list:
            if not target_veg or p['vegetal'] == target_veg:
                sum_val += harvest_value(p, year, week_in_year, l['area'])
    return sum_val

# ----------------- INTERFAZ PRINCIPAL -----------------
st.header("Planificación de Siembras — V11.0 (Rendimientos Reales Excel & Época Fría)")

# Barra de herramientas superior
with st.container():
    col_tabs, col_sum_filt, col_lote_filt, col_years = st.columns([1.5, 1.2, 1.2, 1.8])
    
    with col_tabs:
        st.markdown("**Fincas**")
        selected_finca = st.radio("Finca", st.session_state.fincas, horizontal=True, label_visibility="collapsed")
        
    with col_sum_filt:
        st.markdown("**📊 Resumen General**")
        summary_veg_filter = st.selectbox("Resumen Veg", ["Todos"] + list(st.session_state.ciclos.keys()), label_visibility="collapsed")
        target_summary_veg = None if summary_veg_filter == "Todos" else summary_veg_filter
        
    with col_lote_filt:
        st.markdown("**🌱 Matriz Planificación**")
        lote_veg_filter = st.selectbox("Lote Veg", ["Ver Todos"] + list(st.session_state.ciclos.keys()), label_visibility="collapsed")
        target_lote_veg = None if lote_veg_filter == "Ver Todos" else lote_veg_filter
        
    with col_years:
        st.markdown("**📅 Años Activos**")
        selected_years = st.multiselect("Años", [2025, 2026, 2027, 2028], default=[2026, 2027], label_visibility="collapsed")

st.divider()

# Gestión de catálogos mediante Expander desplegable
with st.expander("⚙ Configuración de Catálogos (Vegetales, Fincas y Lotes)", expanded=False):
    cat_tab1, cat_tab2, cat_tab3 = st.tabs(["Vegetales y Rendimientos", "Fincas", "Lotes"])
    
    with cat_tab1:
        st.subheader("Administrar Vegetales")
        for vname, cdata in list(st.session_state.ciclos.items()):
            cols = st.columns([2, 1, 2, 1])
            with cols[0]:
                st.markdown(f"**{vname}** (Base: {cdata['duracionBase']} sem.)")
            with cols[1]:
                cdata['coldExtend'] = st.checkbox(f"+1 sem fría", value=cdata.get('coldExtend', False), key=f"cold_{vname}")
            with cols[2]:
                new_dur = st.number_input(f"Duración {vname}", value=cdata['duracionBase'], min_value=1, max_value=52, key=f"dur_{vname}")
                cdata['duracionBase'] = new_dur
            with cols[3]:
                if st.button(f"Eliminar {vname}", key=f"del_veg_{vname}"):
                    del st.session_state.ciclos[vname]
                    if vname in st.session_state.rendimientos:
                        del st.session_state.rendimientos[vname]
                    st.rerun()
        
        st.divider()
        st.markdown("##### Agregar Nuevo Vegetal")
        new_veg_name = st.text_input("Nombre del Vegetal")
        if st.button("Crear Vegetal"):
            if new_veg_name and new_veg_name not in st.session_state.ciclos:
                st.session_state.ciclos[new_veg_name] = {"duracionBase": 12, "cosechas": [[11, 0.5], [12, 0.5]], "color": "ejote", "coldExtend": False}
                st.session_state.rendimientos[new_veg_name] = {w: 8000 for w in range(1, 54)}
                st.rerun()

    with cat_tab2:
        st.subheader("Administrar Fincas")
        for f in st.session_state.fincas:
            st.text(f"Finca: {f}")
        new_finca = st.text_input("Código de Nueva Finca (ej. AB)")
        if st.button("Agregar Finca"):
            if new_finca and new_finca.upper() not in st.session_state.fincas:
                st.session_state.fincas.append(new_finca.upper())
                st.rerun()

    with cat_tab3:
        st.subheader("Administrar Lotes Base")
        st.info("Para dividir lotes en A/B, puedes gestionarlo directamente desde los controles de la matriz.")
        lote_to_del = st.selectbox("Seleccionar Lote para Eliminar", [l['id'] for l in st.session_state.base_lotes])
        if st.button("Eliminar Lote Seleccionado"):
            st.session_state.base_lotes = [l for l in st.session_state.base_lotes if l['id'] != lote_to_del]
            st.rerun()

# ----------------- CONSTRUCCIÓN DE LA MATRIZ DE PLANIFICACIÓN -----------------
active_lotes = get_active_lotes_for_finca(selected_finca)

# Métricas superiores acumuladas
total_area_uso = 0
total_prod_acum = 0

# Construir tabla de datos para Streamlit dataframe / data_editor o renderizado personalizado
grid_data = []
sum_col_header = f"Total {target_summary_veg}" if target_summary_veg else "Total Fincas"

if not selected_years:
    st.warning("Por favor seleccione al menos un año en las opciones superiores.")
else:
    table_rows = []
    for year in selected_years:
        for w in range(1, 53):
            global_harvest = get_total_harvest_all_fincas(year, w, target_summary_veg)
            row_dict = {
                "Sem.": w,
                "Año": year,
                sum_col_header: round(global_harvest) if global_harvest > 0 else "-"
            }
            
            for l in active_lotes:
                occupancy = get_detailed_occupancy(l['id'], year, w)
                cell_text = ""
                if occupancy:
                    act = occupancy['planting']
                    if target_lote_veg and act['vegetal'] != target_lote_veg:
                        cell_text = ""
                    else:
                        if occupancy['type'] == 'direct':
                            val = harvest_value(act, year, w, l['area'])
                            if val > 0:
                                cell_text = f"{act['vegetal']} ({round(val)})"
                                total_prod_acum += val
                            else:
                                cell_text = f"[{act['vegetal']}]"
                            if w == 1 or (act['year'] == year and act['weekInYear'] == w):
                                total_area_uso += l['area']
                        else:
                            cell_text = f"[{occupancy['sourceId'][-2:]}]"
                            if w == 1 or (act['year'] == year and act['weekInYear'] == w):
                                total_area_uso += l['area']
                row_dict[l['nombre']] = cell_text
            table_rows.append(row_dict)

    df_grid = pd.DataFrame(table_rows)

    # Mostrar métricas de resumen
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.markdown(f'<div class="stat-card"><b>{round(total_area_uso, 1)}</b><span>Área Total en Uso (ha)</span></div>', unsafe_allow_html=True)
    with mcol2:
        st.markdown(f'<div class="stat-card"><b>{round(total_prod_acum):,}</b><span>Producción Total Estimada</span></div>', unsafe_allow_html=True)
    with mcol3:
        st.markdown(f'<div class="stat-card"><b>{selected_finca}</b><span>Finca Activa ({len(active_lotes)} lotes)</span></div>', unsafe_allow_html=True)

    st.divider()

    # Controles rápidos de división/unificación de lotes por lote individual
    st.markdown("##### 🎛 Control de Partición de Lotes (A / B)")
    split_cols = st.columns(min(len(active_lotes), 6))
    for idx, l in enumerate(active_lotes[:12]): # Mostrar primeros lotes para control rápido
        base_id = l['parentId'] if l['isSplit'] else l['id']
        with split_cols[idx % len(split_cols)]:
            is_currently_split = st.session_state.expanded_lots.get(base_id, False)
            btn_label = f"Unificar {base_id}" if is_currently_split else f"Partir {base_id}"
            if st.button(btn_label, key=f"split_btn_{base_id}_{idx}"):
                if is_currently_split:
                    del st.session_state.expanded_lots[base_id]
                else:
                    st.session_state.expanded_lots[base_id] = True
                st.rerun()

    st.divider()

    # Visualización interactiva de siembras y asignación rápida
    st.markdown("##### 📅 Matriz Semanal de Siembras y Cosechas")
    
    # Selector interactivo para agregar o eliminar una siembra de forma sencilla
    with st.expander("➕ Registrar o Modificar Siembra en Lote", expanded=False):
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        with col_s1:
            target_lote_input = st.selectbox("Lote", [l['id'] for l in active_lotes])
        with col_s2:
            target_veg_input = st.selectbox("Vegetal", list(st.session_state.ciclos.keys()))
        with col_s3:
            target_year_input = st.selectbox("Año Siembra", selected_years)
        with col_s4:
            target_week_input = st.number_input("Semana Siembra", min_value=1, max_value=52, value=1)
        with col_s5:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Registrar Siembra"):
                if target_lote_input not in st.session_state.plantings:
                    st.session_state.plantings[target_lote_input] = []
                st.session_state.plantings[target_lote_input].append({
                    "year": target_year_input,
                    "weekInYear": target_week_input,
                    "vegetal": target_veg_input
                })
                st.success(f"Siembra de {target_veg_input} registrada en {target_lote_input} (Semana {target_week_input}/{target_year_input}).")
                st.rerun()

    # Mostrar la tabla completa filtrada por años
    st.dataframe(df_grid, use_container_width=True, height=500)
```[cite: 3]
