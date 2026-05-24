import streamlit as st

# 1. Configuración de página centrada y limpia
st.set_page_config(
    page_title="Bienvenido a Finn",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo personalizado para hacer los textos aún más llamativos
st.markdown(
    """
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
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Encabezado principal
st.markdown('<div class="big-title">¿Cómo deseas ingresar hoy? 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Por favor, selecciona tu perfil para personalizar tu experiencia en Finn</div>', unsafe_allow_html=True)

# 3. Distribución de botones grandes en dos columnas principales
col_cliente, col_empleado = st.columns(2)

with col_cliente:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>👤 Perfil Cliente</h3>", unsafe_allow_html=True)
        st.write(
            "Accede a nuestro asistente virtual inteligente para resolver dudas, "
            "consultar tus movimientos de dinero y recibir recomendaciones automáticas."
        )
        st.write("") # Espaciado vertical
        
        # Botón para Cliente (Guarda el rol de Cliente antes de cambiar)
        if st.button("Ingresar como Cliente", use_container_width=True, type="primary"):
            st.session_state.rol = "cliente" # <-- GUARDAMOS EL ROL
            st.switch_page("pages/1_chatbot.py")

with col_empleado:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>💼 Perfil Empleado</h3>", unsafe_allow_html=True)
        st.write(
            "Visualiza estadísticas de negocio, distribuciones de transacciones "
            "financieras en tiempo real y gestiona reportes analíticos consolidados."
        )
        st.write("") # Espaciado vertical
        
        # Botón para Empleado (Guarda el rol de Empleado antes de cambiar)
        if st.button("Ingresar como Empleado", use_container_width=True):
            st.session_state.rol = "empleado" # <-- GUARDAMOS EL ROL
            st.switch_page("pages/4_empleados.py")

# 4. Pie de página decorativo
st.divider()
st.caption("🔒 Conexión segura de datos cifrados de Finnbot IA")