import streamlit as st
import json

# ── Configuración ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Bienvenido a Finn",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Estilos ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Fondo general */
[data-testid="stAppViewContainer"] { background: #0B1120 !important; }
[data-testid="stHeader"] { background: #0B1120 !important; border-bottom: 1px solid #2a3a52; }
[data-testid="block-container"] { background: #0B1120; padding: 3rem 2rem; }

/* Tipografía base */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; color: #E8EDF5 !important; }

/* Títulos custom */
.big-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    text-align: center;
    color: #E8EDF5 !important;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}
.subtitle {
    font-size: 16px !important;
    text-align: center;
    color: #7A90AA !important;
    margin-bottom: 40px;
    font-family: 'DM Sans', sans-serif !important;
}

/* Tarjetas de rol */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111827 !important;
    border: 1px solid #2a3a52 !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #C8A96E !important;
}

/* Texto dentro de las tarjetas */
[data-testid="stVerticalBlockBorderWrapper"] p {
    color: #7A90AA !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: #E8EDF5 !important;
    font-size: 1.1rem !important;
}

/* Botón primario (Cliente) */
.stButton > button[kind="primary"] {
    background: transparent !important;
    border: 1px solid #C8A96E !important;
    color: #C8A96E !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 10px !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #C8A96E !important;
    color: #0B1120 !important;
}

/* Botón secundario (Empleado / Volver) */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #2a3a52 !important;
    color: #7A90AA !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 10px !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #818CF8 !important;
    color: #818CF8 !important;
}

/* Tarjetas de usuario demo */
.user-card {
    background: #111827;
    border: 1px solid #2a3a52;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.user-card:hover { border-color: #C8A96E; }
.user-emoji { font-size: 38px; margin-bottom: 8px; }
.user-name  { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 15px; color: #E8EDF5; }
.user-desc  { font-size: 12.5px; color: #7A90AA; margin-top: 4px; line-height: 1.4; }

/* Divider */
hr { border-color: #2a3a52 !important; }

/* Caption */
[data-testid="stCaptionContainer"] { color: #4A5F78 !important; text-align: center; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Estado: pantalla actual ───────────────────────────────────────
# "inicio"         → pantalla principal con los dos roles
# "seleccion_demo" → pantalla de selección de usuario demo
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "inicio"


# ══════════════════════════════════════════════════════════════════
# PANTALLA 1: Selección de rol
# ══════════════════════════════════════════════════════════════════
if st.session_state.pantalla == "inicio":

    st.markdown('<div class="big-title">¿Cómo deseas ingresar hoy? 🚀</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Selecciona tu perfil para personalizar tu experiencia en Finn</div>', unsafe_allow_html=True)

    col_cliente, col_empleado = st.columns(2)

    with col_cliente:
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center;'>👤 Perfil Cliente</h3>", unsafe_allow_html=True)
            st.write(
                "Accede a tu asistente virtual para resolver dudas, "
                "consultar movimientos y recibir recomendaciones personalizadas."
            )
            st.write("")
            if st.button("Ingresar como Cliente", use_container_width=True, type="primary"):
                st.session_state.pantalla = "seleccion_demo"
                st.rerun()

    with col_empleado:
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center;'>💼 Perfil Empleado</h3>", unsafe_allow_html=True)
            st.write(
                "Visualiza estadísticas, distribuciones de transacciones "
                "y gestiona reportes analíticos consolidados."
            )
            st.write("")
            if st.button("Ingresar como Empleado", use_container_width=True):
                st.session_state.rol = "empleado"
                st.switch_page("pages/4_empleados.py")

    st.divider()
    st.caption("🔒 Conexión segura de datos cifrados de Finnbot IA")


# ══════════════════════════════════════════════════════════════════
# PANTALLA 2: Selección de usuario demo
# ══════════════════════════════════════════════════════════════════
elif st.session_state.pantalla == "seleccion_demo":

    # Botón de regreso
    if st.button("← Volver", type="secondary"):
        st.session_state.pantalla = "inicio"
        st.rerun()

    st.markdown('<div class="big-title">¿Quién eres hoy? 👥</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Selecciona un perfil demo para explorar la experiencia personalizada</div>', unsafe_allow_html=True)

    # Cargar usuarios demo
    try:
        with open("data/demo_users.json", encoding="utf-8") as f:
            demo_data = json.load(f)
        usuarios = demo_data["usuarios"]
    except Exception as e:
        st.error(f"No se pudo cargar demo_users.json: {e}")
        st.stop()

    # Mostrar tarjetas de usuario en columnas
    cols = st.columns(len(usuarios))

    for i, (col, usuario) in enumerate(zip(cols, usuarios)):
        with col:
            st.markdown(f"""
            <div class="user-card">
                <div class="user-emoji">{usuario['emoji']}</div>
                <div class="user-name">{usuario['nombre']}</div>
                <div class="user-desc">{usuario['descripcion']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"Seleccionar",
                key=f"usr_{i}",
                use_container_width=True,
                type="primary" 
            ):
                # Guardar en session_state el usuario seleccionado
                st.session_state.rol                   = "cliente"
                st.session_state.demo_user_id          = usuario["id"]
                st.session_state.demo_user_nombre      = usuario["nombre"]
                st.session_state.demo_user_contexto    = usuario["archivo_contexto"]
                st.session_state.demo_user_transacc    = usuario["archivo_transacciones"]
                st.session_state.pantalla              = "inicio"  # reset para próxima vez
                st.switch_page("pages/3_clientes.py")

    st.divider()
    st.caption("🔒 Modo demo — los datos mostrados son ficticios con fines ilustrativos")