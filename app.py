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
    for f in st.session_
