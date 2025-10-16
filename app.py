import streamlit as st
import pandas as pd
import random
import time

# ==============================
# Configuración inicial
# ==============================
NUM_DRAFTS = 4
PICKS_PER_DRAFT = 8  # Número de rondas por draft
PICK_TIME = 60  # segundos por pick

# ==============================
# Cargar jugadores desde Excel
# ==============================
df = pd.read_excel("jugadores.xlsx")
df["Nombre"] = df["Nombre"].astype(str).str.strip()
jugadores_disponibles = df["Nombre"].tolist()

# ==============================
# Inicializar drafts
# ==============================
if "drafts" not in st.session_state:
    st.session_state.drafts = {}
    for i in range(1, NUM_DRAFTS + 1):
        st.session_state.drafts[f"Draft {i}"] = {
            "players": jugadores_disponibles.copy(),
            "picks": [],
            "current_pick": 0,
            "time_left": PICK_TIME
        }

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# ==============================
# Funciones auxiliares
# ==============================
def pick_player(draft_id, jugador):
    draft = st.session_state.drafts[draft_id]
    if jugador in draft["players"]:
        draft["players"].remove(jugador)
        draft["picks"].append(jugador)
        draft["current_pick"] += 1
        draft["time_left"] = PICK_TIME

def auto_pick(draft_id):
    draft = st.session_state.drafts[draft_id]
    if draft["players"]:
        jugador_random = random.choice(draft["players"])
        pick_player(draft_id, jugador_random)

def cleanup_finished_drafts():
    to_delete = []
    for draft_id, draft in st.session_state.drafts.items():
        if draft["current_pick"] >= PICKS_PER_DRAFT:
            to_delete.append(draft_id)
    for draft_id in to_delete:
        st.session_state.drafts.pop(draft_id)
        st.success(f"{draft_id} terminado y eliminado.")

# ==============================
# Layout visual
# ==============================
st.title("⚡ Mock Drafts Visuales - Jugadores reales")

cols = st.columns(2)

for idx, (draft_id, draft) in enumerate(st.session_state.drafts.items()):
    with cols[idx % 2]:
        st.subheader(draft_id)
        # Barra de progreso
        st.progress(draft["current_pick"] / PICKS_PER_DRAFT)
        st.write(f"Picks: {draft['current_pick']}/{PICKS_PER_DRAFT}")
        st.write(f"Tiempo restante: {draft['time_left']} seg")

        # Lista de picks ya hechos
        if draft["picks"]:
            st.write("Picks anteriores: " + ", ".join(draft["picks"]))

        # Selectbox de jugadores disponibles
        jugador_seleccionado = st.selectbox(
            f"Selecciona jugador {draft_id}",
            [""] + draft["players"],
            key=f"sel_{draft_id}"
        )

        if st.button(f"Hacer pick {draft_id}", key=f"btn_{draft_id}") and jugador_seleccionado:
            pick_player(draft_id, jugador_seleccionado)
            st.experimental_rerun()

# ==============================
# Timer de simulación de pick automático
# ==============================
if time.time() - st.session_state.last_update > 3:  # polling cada 3 segundos
    for draft_id, draft in st.session_state.drafts.items():
        if draft["current_pick"] < PICKS_PER_DRAFT:
            draft["time_left"] -= 3
            if draft["time_left"] <= 0:
                auto_pick(draft_id)
    st.session_state.last_update = time.time()
    st.experimental_rerun()

cleanup_finished_drafts()

