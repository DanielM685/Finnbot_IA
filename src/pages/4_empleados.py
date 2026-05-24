import streamlit as st
import sys
from pathlib import Path

# Asegurar que src/ está en el path
sys.path.insert(0, str(Path(__file__).parent))

from employee_agent import ask_employee_agent
from user_context import load_context

st.set_page_config(page_title="FinnBot - Banco Serfinanza", layout="wide")


if "rol" not in st.session_state or st.session_state.rol != "cliente":
    st.error("⚠️ Acceso denegado. Esta sección es exclusiva para clientes.")
    if st.button("Ir a la Página de Inicio", use_container_width=True):
        st.switch_page("src/pages/inicio.py")
    st.stop() # <-- Detiene todo el código de abajo para que no puedan ver nada

# --- BOTÓN VOLVER ---
if st.button("⬅️ Volver al Inicio"):
    st.switch_page("pages/3_clientes.py")

st.title("FinnBot IA — Banco Serfinanza 🤖")

# --- ALERTAS (se muestran una sola vez al cargar) ---
if "alertas_mostradas" not in st.session_state:
    ctx = load_context()
    alertas = ctx.get("alertas", [])
    for a in alertas:
        if a["tipo"] == "advertencia":
            st.warning(f"⚠️ {a['mensaje']}")
        else:
            st.info(f"ℹ️ {a['mensaje']}")
    st.session_state.alertas_mostradas = True

# --- INICIALIZAR ESTADO ---

if "historial" not in st.session_state:
    st.session_state.historial = [
        {
            "role": "assistant",
            "content": f"¡Hola, Soy ServigGuia, tu asesor virtual de Banco Serfinanza 👋 ¿En qué te puedo ayudar hoy?"
        }
    ]

if "history" not in st.session_state:
    st.session_state.history = []  # formato LangChain: [("human", ...), ("ai", ...)]

# --- MOSTRAR HISTORIAL ---
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])


# --- ENTRADA DEL USUARIO ---
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.historial.append({"role": "user", "content": prompt})

    # Llamar al agente con el historial LangChain
    with st.chat_message("assistant"):
        with st.spinner("ServiGuia está pensando..."):
            respuesta = ask_employee_agent(prompt, st.session_state.history)
        st.write(respuesta)

    st.session_state.historial.append({"role": "assistant", "content": respuesta})

    # Actualizar historial LangChain para la próxima llamada
    st.session_state.history.append(("human", prompt))
    st.session_state.history.append(("ai", respuesta))