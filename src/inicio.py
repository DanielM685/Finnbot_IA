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
.big-title {
    font-size: 45px !important;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}
.subtitle {
    font-size: 20px !important;
    text-align: center;
    color: #888888;
    margin-bottom: 40px;
}
.user-card {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: border-color 0.2s;
    cursor: pointer;
    margin-bottom: 8px;
}
.user-card:hover { border-color: #3b82f6; }
.user-emoji  { font-size: 40px; margin-bottom: 6px; }
.user-name   { font-weight: 700; font-size: 15px; color: #0f172a; }
.user-desc   { font-size: 13px; color: #64748b; margin-top: 2px; }
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