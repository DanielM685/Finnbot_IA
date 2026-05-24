import streamlit as st
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from savings_agent import ask_savings_agent

st.set_page_config(page_title="Plan de Ahorros - FinnBot", layout="wide")

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
    border-color: #2DD4BF !important;
    color: #2DD4BF !important;
}

/* Chat messages — burbuja del asistente */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #0f2320 !important;
    border: 1px solid rgba(45,212,191,0.2) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
}

/* Chat messages — burbuja del usuario */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(96,165,250,0.08) !important;
    border: 1px solid rgba(96,165,250,0.2) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
}

/* Avatar de la asistente */
[data-testid="stChatMessageAvatarAssistant"] {
    background: rgba(45,212,191,0.12) !important;
    border: 1px solid #2DD4BF !important;
    color: #2DD4BF !important;
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
    border-color: #2DD4BF !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #4A5F78 !important; }

/* Botón enviar del chat */
[data-testid="stChatInput"] button {
    background: transparent !important;
    color: #2DD4BF !important;
    border-color: #2DD4BF !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: #2DD4BF !important; }

/* Divider */
hr { border-color: #2a3a52 !important; }
</style>
""", unsafe_allow_html=True)

if "rol" not in st.session_state or st.session_state.rol != "cliente":
    st.error("⚠️ Acceso denegado. Esta sección es exclusiva para clientes.")
    if st.button("Ir a la Página de Inicio", use_container_width=True):
        st.switch_page("src/pages/inicio.py")
    st.stop()

# ── Rutas dinámicas ───────────────────────────────────────────────
ctx_path = st.session_state.get("demo_user_contexto", "data/user_context.json")
txn_path = st.session_state.get("demo_user_transacc", "data/transactions.json")
nombre   = st.session_state.get("demo_user_nombre", "Cliente").split()[0]

if st.button("⬅️ Volver al Inicio"):
    st.switch_page("pages/3_clientes.py")

st.title("Asesor de Ahorros de FinnBot 💚")

# ── Historial (key única por usuario) ────────────────────────────
hist_key    = f"historial_FinnBot_{ctx_path}"
lc_hist_key = f"lc_history_FinnBot_{ctx_path}"

if hist_key not in st.session_state:
    st.session_state[hist_key] = [
        {"role": "assistant", "content": f"¡Hola, {nombre}! Soy FinnBot, tu asesor de finanzas 💚 Estoy aquí para ayudarte a entender tus gastos y construir un plan de ahorro real. ¿Por dónde empezamos?"}
    ]
if lc_hist_key not in st.session_state:
    st.session_state[lc_hist_key] = []

# ── Mostrar historial ─────────────────────────────────────────────
for mensaje in st.session_state[hist_key]:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])

# ── Entrada del usuario ───────────────────────────────────────────
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state[hist_key].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("FinnBot está analizando..."):
            respuesta = ask_savings_agent(
                prompt,
                st.session_state[lc_hist_key],
                ctx_path=ctx_path,   
                txn_path=txn_path,   
            )
        st.write(respuesta)

    st.session_state[hist_key].append({"role": "assistant", "content": respuesta})
    st.session_state[lc_hist_key].append(("human", prompt))
    st.session_state[lc_hist_key].append(("ai", respuesta))
