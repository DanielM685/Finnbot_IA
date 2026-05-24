import streamlit as st
import sys
from pathlib import Path

# Asegurar que src/ está en el path
sys.path.insert(0, str(Path(__file__).parent))

from savings_agent import ask_savings_agent, _get_nombre
from user_context import load_context

st.set_page_config(page_title="Nova - Banco Serfinanza", layout="wide")

# --- BOTÓN VOLVER ---
if st.button("⬅️ Volver al Inicio"):
    st.switch_page("pagina.py")

st.title("Nova IA — Banco Serfinanza 🤖")

# --- INICIALIZAR ESTADO ---
nombre = _get_nombre()

if "historial" not in st.session_state:
    st.session_state.historial = [
        {
            "role": "assistant",
            "content": f"¡Hola, {nombre}! Soy Nova, tu asesor virtual de Banco Serfinanza 👋 ¿En qué te puedo ayudar hoy?"
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
        with st.spinner("Nova está pensando..."):
            respuesta = ask_savings_agent(prompt, st.session_state.history)
        st.write(respuesta)

    st.session_state.historial.append({"role": "assistant", "content": respuesta})

    # Actualizar historial LangChain para la próxima llamada
    st.session_state.history.append(("human", prompt))
    st.session_state.history.append(("ai", respuesta))