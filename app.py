import streamlit as st
import pandas as pd
import random
import time

# ===============================
# Cargar jugadores desde Excel
# ===============================
df = pd.read_excel("jugadores.xlsx")
df.columns = df.columns.str.strip()
df["Nombre"] = df["Nombre"].astype(str).str.strip()
jugadores_disponibles = df["Nombre"].tolist()

# ===============================
# Configuración inicial
# ===============================
NUM_PICKS = 20      # total de jugadores por draft
PICK_TIME = 60      # segundos por pick

if "salas" not in st.session_state:
    st.session_state["salas"] = {}

if "sala_actual" not in st.session_state:
    st.session_state["sala_actual"] = None

if "last_update" not in st.session_state:
    st.session_state["last_update"] = time.time()

# ===============================
# Funciones helper
# ===============================
def pick_player(sala_id, jugador):
    sala = st.session_state["salas"][sala_id]
    if jugador in sala["players"]:
        sala["players"].remove(jugador)
        sala["picks"].append(jugador)
        sala["current_pick"] += 1
        sala["time_left"] = PICK_TIME

def auto_pick(sala_id):
    sala = st.session_state["salas"][sala_id]
    if sala["players"]:
        jugador_random = random.choice(sala["players"])
        pick_player(sala_id, jugador_random)

def cleanup_finished_salas():
    to_delete = []
    for sala_id, sala in st.session_state["salas"].items():
        if sala["current_pick"] >= NUM_PICKS:
            to_delete.append(sala_id)
    for sala_id in to_delete:
        st.session_state["salas"].pop(sala_id)
        if st.session_state.get("sala_actual") == sala_id:
            st.session_state["sala_actual"] = None
        st.success(f"{sala_id} terminado y cerrado.")

# ===============================
# Pantalla principal: Salas
# ===============================
st.title("⚡ Mock Drafts con Salas")

# Crear nueva sala
if st.button("Crear nueva sala"):
    nueva_sala = f"Sala {len(st.session_state['salas']) + 1}"
    st.session_state["salas"][nueva_sala] = {
        "players": jugadores_disponibles.copy(),
        "picks": [],
        "current_pick": 0,
        "time_left": PICK_TIME
    }
    st.session_state["sala_actual"] = nueva_sala
    st.experimental_rerun()

# Si no estamos en ninguna sala, mostramos la lista
if st.session_state["sala_actual"] is None:
    st.subheader("Salas disponibles:")
    for sala_id in st.session_state["salas"]:
        if st.button(f"Entrar a {sala_id}"):
            st.session_state["sala_actual"] = sala_id
            st.experimental_rerun()
else:
    sala_id = st.session_state["sala_actual"]
    sala = st.session_state["salas"][sala_id]

    st.subheader(f"Draft: {sala_id}")
    st.write(f"Picks: {sala['current_pick']}/{NUM_PICKS}")
    st.write(f"Tiempo restante: {sala['time_left']} seg")

    # Lista de picks anteriores
    if sala["picks"]:
        st.write("Picks anteriores: " + ", ".join(sala["picks"]))

    # Selectbox para pick
    jugador_seleccionado = st.selectbox(
        "Selecciona jugador",
        [""] + sala["players"],
        key=f"sel_{sala_id}"
    )
    if st.button("Hacer pick", key=f"btn_{sala_id}") and jugador_seleccionado:
        pick_player(sala_id, jugador_seleccionado)
        st.experimental_rerun()

    if st.button("Salir de la sala"):
        st.session_state["sala_actual"] = None
        st.experimental_rerun()

# ===============================
# Polling automático cada 3 segundos
# ===============================
if time.time() - st.session_state["last_update"] > 3:
    if st.session_state["sala_actual"]:
        sala_id = st.session_state["sala_actual"]
        sala = st.session_state["salas"][sala_id]
        if sala["current_pick"] < NUM_PICKS:
            sala["time_left"] -= 3
            if sala["time_left"] <= 0:
                auto_pick(sala_id)
    st.session_state["last_update"] = time.time()
    st.experimental_rerun()

cleanup_finished_salas()

cleanup_finished_drafts()

