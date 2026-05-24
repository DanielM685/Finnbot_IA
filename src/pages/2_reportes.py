import streamlit as st

st.set_page_config(
    page_title="Centro de Reportes - Finn",
    layout="wide"
)

# Botón limpio para regresar al home de la aplicación principal
if st.button("⬅️ Volver al Panel Principal"):
    st.switch_page("pagina.py")

st.title("📂 Centro de Reportes y Descargas")
st.write("Bienvenido al módulo avanzado de análisis. Aquí podrás filtrar tus datos y descargar tus reportes.")

st.divider()

# Simulador de un área de descargas profesional
st.subheader("⚡ Acciones Rápidas")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.write("### 📄 Exportar Historial en PDF")
        st.write("Genera un documento estético con gráficos y tablas listo para imprimir.")
        if st.button("Descargar PDF", use_container_width=True, type="primary"):
            st.info("Generando reporte PDF... (Función de prueba)")

with col2:
    with st.container(border=True):
        st.write("### 📊 Descargar Datos limpios (CSV)")
        st.write("Obtén un archivo plano compatible con Microsoft Excel o Google Sheets.")
        if st.button("Descargar CSV", use_container_width=True):
            st.info("Preparando archivo CSV... (Función de prueba)")