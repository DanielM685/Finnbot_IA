import streamlit as st
import pandas as pd
import os
import json
import altair as alt 

# 1. Configurar la página en modo ancho ("wide") para que el diseño sea óptimo
st.set_page_config(
    page_title="Página principal Finn",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PATH_JSON = "datos.json"

# Verificamos si existe el archivo y si contiene la categoría vieja de "Nómina" para forzar su actualización
forzar_actualizacion = False
if os.path.exists(PATH_JSON):
    try:
        with open(PATH_JSON, "r") as f:
            datos_existentes = json.load(f)
            # Si encontramos "Nómina" en los datos guardados, forzamos la regeneración
            if any(txn.get("categoria") == "Nómina" for txn in datos_existentes):
                forzar_actualizacion = True
    except Exception:
        forzar_actualizacion = True

# Generación del JSON de prueba limpio de ingresos (solo gastos/salidas)
if not os.path.exists(PATH_JSON) or forzar_actualizacion:
    datos_prueba = [
        {
            "id": "TXN-001",
            "fecha": "2026-05-18",
            "hora": "10:30",
            "tipo": "compra",
            "canal": "tarjeta_fisica",
            "comercio": "Éxito",
            "categoria": "Alimentación",
            "subcategoria": "Supermercado",
            "monto": 150000,
            "moneda": "COP",
            "producto_origen": "Cuenta de Ahorros",
            "ciudad": "Bogotá",
            "pais": "Colombia",
            "descripcion": "Mercado quincenal",
            "cuotas": 1,
            "estado": "aprobada",
            "es_recurrente": False,
            "latitud": 4.7110,
            "longitud": -74.0721
        },
        {
            "id": "TXN-002",
            "fecha": "2026-05-19",
            "hora": "14:15",
            "tipo": "pago",
            "canal": "pse",
            "comercio": "Claro",
            "categoria": "Servicios",
            "subcategoria": "Telefonía",
            "monto": 85000,
            "moneda": "COP",
            "producto_origen": "Tarjeta de Crédito",
            "ciudad": "Medellín",
            "pais": "Colombia",
            "descripcion": "Pago plan móvil",
            "cuotas": 1,
            "estado": "aprobada",
            "es_recurrente": True,
            "latitud": 6.2442,
            "longitud": -75.5812
        },
        {
            "id": "TXN-003",
            "fecha": "2026-05-20",
            "hora": "08:00",
            "tipo": "compra",
            "canal": "tarjeta_online",
            "comercio": "Netflix",
            "categoria": "Entretenimiento",
            "subcategoria": "Streaming",
            "monto": 44900,
            "moneda": "COP",
            "producto_origen": "Tarjeta de Crédito",
            "ciudad": "Cali",
            "pais": "Colombia",
            "descripcion": "Suscripción mensual",
            "cuotas": 1,
            "estado": "aprobada",
            "es_recurrente": True,
            "latitud": 3.4516,
            "longitud": -76.5320
        },
        {
            "id": "TXN-004",
            "fecha": "2026-05-21",
            "hora": "19:45",
            "tipo": "transferencia",
            "canal": "app",
            "comercio": "Andrés Pérez",
            "categoria": "Transferencias",
            "subcategoria": "Amigos",
            "monto": 120000,
            "moneda": "COP",
            "producto_origen": "Cuenta de Ahorros",
            "ciudad": "Barranquilla",
            "pais": "Colombia",
            "descripcion": "Regalo de cumpleaños",
            "cuotas": 1,
            "estado": "aprobada",
            "es_recurrente": False,
            "latitud": 10.9685,
            "longitud": -74.7813
        },
        {
            "id": "TXN-005",
            "fecha": "2026-05-22",
            "hora": "11:20",
            "tipo": "avance",
            "canal": "cajero",
            "comercio": "Cajero Bancolombia",
            "categoria": "Efectivo",
            "subcategoria": "Retiro",
            "monto": 300000,
            "moneda": "COP",
            "producto_origen": "Tarjeta de Crédito",
            "ciudad": "Bogotá",
            "pais": "Colombia",
            "descripcion": "Retiro efectivo de emergencia",
            "cuotas": 6,
            "estado": "aprobada",
            "es_recurrente": False,
            "latitud": 4.7110,
            "longitud": -74.0721
        },
        {
            "id": "TXN-006",
            "fecha": "2026-05-23",
            "hora": "16:00",
            "tipo": "compra",
            "canal": "tarjeta_fisica",
            "comercio": "Uber",
            "categoria": "Transporte",
            "subcategoria": "Viaje urbano",
            "monto": 25000,
            "moneda": "COP",
            "producto_origen": "Tarjeta de Crédito",
            "ciudad": "Medellín",
            "pais": "Colombia",
            "descripcion": "Viaje oficina",
            "cuotas": 1,
            "estado": "rechazada",
            "es_recurrente": False,
            "latitud": 6.2442,
            "longitud": -75.5812
        },
        {
            "id": "TXN-007",
            "fecha": "2026-05-23",
            "hora": "18:30",
            "tipo": "pago",
            "canal": "debito_automatico",
            "comercio": "EPM",
            "categoria": "Servicios Públicos",
            "subcategoria": "Luz y Agua",
            "monto": 115000,
            "moneda": "COP",
            "producto_origen": "Cuenta de Ahorros",
            "ciudad": "Bogotá",
            "pais": "Colombia",
            "descripcion": "Pago servicios mes actual",
            "cuotas": 1,
            "estado": "aprobada",
            "es_recurrente": True,
            "latitud": 4.7110,
            "longitud": -74.0721
        }
    ]
    with open(PATH_JSON, "w") as f:
        json.dump(datos_prueba, f, indent=4)

@st.cache_data  # Optimización para que cargue instantáneamente
def cargar_datos():
    df = pd.read_json(PATH_JSON)
    # Comprobamos si la columna 'fecha' existe antes de procesarla
    if "fecha" in df.columns:
        # errors='coerce' convierte fechas inválidas en NaT (vacío) en lugar de romper la app
        df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
    else:
        # Si no existe la columna, creamos una temporal con la fecha de hoy para evitar fallos
        df["fecha"] = pd.Timestamp.now()
    return df

try:
    df_datos = cargar_datos()
    datos_cargados = True
except Exception as e:
    st.error(f"Error al leer el archivo JSON: {e}")
    datos_cargados = False

# 3. Diseño de la Interfaz de Usuario (UI)
st.title("📈 Panel de Gastos Personales")
st.write("Análisis detallado de transacciones y salidas de dinero procesadas desde tu archivo JSON.")

st.divider() # Línea divisoria elegante

if datos_cargados:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sumamos solo los montos de transacciones aprobadas para ver el volumen de gastos real
        total_monto = int(df_datos[df_datos["estado"] == "aprobada"]["monto"].sum())
        st.metric(label="Monto Gastado Aprobado", value=f"${total_monto:,} {df_datos['moneda'].iloc[0]}")
        
    with col2:
        total_transacciones = len(df_datos)
        st.metric(label="Total de Movimientos registrados", value=f"{total_transacciones:,} transacciones")
        
    with col3:
        promedio_monto = round(df_datos["monto"].mean(), 1)
        st.metric(label="Monto Promedio por Gasto", value=f"${promedio_monto:,} {df_datos['moneda'].iloc[0]}")

    st.write("") # Espacio en blanco

    col_grafica, col_chat = st.columns([1, 1])

    # Columna Izquierda: Gráfico Circular Variable / Distribución
    with col_grafica:
        with st.container(border=True):
            st.subheader("📊 Distribución de Egresos")
            
            # Selector dinámico de parámetros de visualización
            opciones_visuales = {
                "Categoría": "categoria",
                "Canal de Pago": "canal",
                "Tipo de Transacción": "tipo",
                "Estado de Transacción": "estado",
                "Ciudad": "ciudad"
            }
            
            parametro_seleccionado = st.selectbox(
                "¿Qué parámetro deseas analizar en el gráfico circular?",
                options=list(opciones_visuales.keys()),
                index=0
            )
            
            columna_activa = opciones_visuales[parametro_seleccionado]
            
            # Agrupar datos por la columna elegida y sumar los montos correspondientes
            df_chart = df_datos.groupby(columna_activa, as_index=False)["monto"].sum()
            
            # Construir el gráfico circular (tipo Dona interactivo)
            grafico_circular = (
                alt.Chart(df_chart)
                .mark_arc(innerRadius=65, stroke="#111", strokeWidth=2)
                .encode(
                    theta=alt.Theta(field="monto", type="quantitative"),
                    color=alt.Color(
                        field=columna_activa, 
                        type="nominal", 
                        legend=alt.Legend(title=parametro_seleccionado),
                        scale=alt.Scale(scheme="accent")  # Gama de colores alegre y distinguible
                    ),
                    tooltip=[
                        alt.Tooltip(field=columna_activa, title=parametro_seleccionado),
                        alt.Tooltip(field="monto", title="Monto Total ($)", format=",d")
                    ]
                )
                .properties(height=280) # Altura balanceada con la tarjeta de la derecha
            )
            
            # Renderizar el gráfico interactivo de Altair
            st.altair_chart(grafico_circular, use_container_width=True)

    with col_chat:
        with st.container(border=True):
            st.subheader("💬 Asistente Inteligente")
            st.write(
                "¿Necesitas ayuda para interpretar estas tendencias? Nuestro "
                "chatbot puede analizar el comportamiento de las métricas y ayudarte "
                "a tomar decisiones inteligentes sobre tus datos en tiempo real."
            )
            
            st.info("💡 Consejo: Puedes subir tus propios archivos `.json` o `.csv` en la barra lateral del chatbot para analizarlos.")
            
            # Espaciado para alinear el botón de forma estética
            st.write("")
            st.write("")
            st.write("")
            
            # Botón de redirección directo a la página del chat
            if st.button("💬 Abrir Chat de Soporte", use_container_width=True, type="primary"):
                st.switch_page("pages/1_chatbot.py")

    st.write("") # Pequeño espacio vertical para separar filas
    
    # NUEVA SECCIÓN GRANDE ABAJO
    with st.container(border=True):
        # Usamos columnas internas para organizar el texto a la izquierda y el botón a la derecha
        col_banner_texto, col_banner_boton = st.columns([2, 1])
        
        with col_banner_texto:
            st.subheader("📊 Plan de Ahorros")
            st.write(
                "Explora tus transacciones con filtros avanzados por fecha, "
                "exporta tus balances financieros a formatos de contabilidad como CSV y Excel, "
                "o genera un reporte en PDF de tus consumos del mes."
            )
            
        with col_banner_boton:
            # Añadimos unos espacios para centrar verticalmente el botón con respecto al texto
            st.write("")
            st.write("")
            # Botón de redirección a la nueva pestaña de reportes
            if st.button("📂 Ir al Plan de ahorros", use_container_width=True):
                st.switch_page("pages/2_reportes.py")

else:
    st.warning("No se pudieron cargar los datos. Revisa el formato de tu archivo JSON.")

st.divider()