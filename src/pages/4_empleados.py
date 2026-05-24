import streamlit as st
import sys
from pathlib import Path

# Asegurar que src/ está en el path
sys.path.insert(0, str(Path(__file__).parent))

from employee_agent import ask_employee_agent
from user_context import load_context

st.set_page_config(page_title="FinnBot - Banco Serfinanza", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Fondo general */
[data-testid="stAppViewContainer"] { background: #0B1120 !important; }
[data-testid="stHeader"] { background: #111827 !important; border-bottom: 1px solid #2a3a52; }
[data-testid="block-container"] { background: #0B1120; padding: 1.5rem 2rem; }

/* Tipografía */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; color: #E8EDF5 !important; }
h1 { font-family: 'Syne', sans-serif !important; font-size: 1.7rem !important; font-weight: 700 !important; color: #E8EDF5 !important; }

/* Botón volver */
.stButton > button {
    background: transparent !important;
    border: 1px solid #2a3a52 !important;
    color: #7A90AA !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
}
.stButton > button:hover {
    border-color: #818CF8 !important;
    color: #818CF8 !important;
}

/* Burbuja del asistente */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #13112a !important;
    border: 1px solid rgba(129,140,248,0.2) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    color: #E8EDF5 !important;
}

/* Burbuja del usuario */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(96,165,250,0.08) !important;
    border: 1px solid rgba(96,165,250,0.2) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    color: #E8EDF5 !important;
}

/* Todo el texto dentro del chat en blanco */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] code {
    color: #E8EDF5 !important;
}

/* Avatar de ServiGuía */
[data-testid="stChatMessageAvatarAssistant"] {
    background: rgba(129,140,248,0.12) !important;
    border: 1px solid #818CF8 !important;
    color: #818CF8 !important;
}

/* Avatar del usuario */
[data-testid="stChatMessageAvatarUser"] {
    background: rgba(96,165,250,0.15) !important;
    border: 1px solid #60A5FA !important;
    color: #60A5FA !important;
}

/* Input del chat */
[data-testid="stChatInput"] textarea {
    background: #1e2d42 !important;
    border: 1px solid #2a3a52 !important;
    color: #E8EDF5 !important;
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 6px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #818CF8 !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #4A5F78 !important; }

/* Botón enviar del chat */
[data-testid="stChatInput"] button {
    background: #0B1120 !important;
    color: #818CF8 !important;
    border-color: #818CF8 !important;
}
            
[data-testid="stBottomBlockContainer"] {
    background: #0B1120 !important;
}
            
[data-testid="stBottomBlockContainer"] {
    background: #0B1120 !important;
}

[data-testid="stChatInput"] {
    background: #0B1120 !important;
}
            
[data-testid="stBottomBlockContainer"] [data-testid="stElementContainer"] {
    background: #0B1120 !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: #818CF8 !important; }

/* Divider */
hr { border-color: #2a3a52 !important; }
</style>
""", unsafe_allow_html=True)


if "rol" not in st.session_state or st.session_state.rol != "empleado":
    st.error("⚠️ Acceso denegado. Esta sección es exclusiva para empleados.")
    if st.button("Ir a la Página de Inicio", use_container_width=True):
        st.switch_page("../src/inicio.py")
    st.stop() # <-- Detiene todo el código de abajo para que no puedan ver nada

# --- BOTÓN VOLVER ---
if st.button("⬅️ Volver al Inicio"):
    st.switch_page("../src/inicio.py")

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