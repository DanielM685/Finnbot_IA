import streamlit as st
import pandas as pd
import altair as alt
import json


st.set_page_config(
    page_title="Panel de Cliente — Serfinanza",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "rol" not in st.session_state or st.session_state.rol != "cliente":
    st.error("Acceso denegado. Esta sección es exclusiva para clientes.")
    if st.button("Ir a la Página de Inicio", use_container_width=True):
        st.switch_page("../src/inicio.py")
    st.stop()

# ── Rutas dinámicas desde session_state ──────────────────────────
PATH_CTX = st.session_state.get("demo_user_contexto", "data/user_context.json")
PATH_TXN = st.session_state.get("demo_user_transacc", "data/transactions.json")

# ── CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Fondo general */
[data-testid="stAppViewContainer"] { background: #0B1120 !important; }
[data-testid="stHeader"] { background: #111827 !important; border-bottom: 1px solid #2a3a52; }
[data-testid="block-container"] { background: #0B1120; padding: 1.5rem 2rem; }

/* Tipografía base */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; color: #E8EDF5 !important; }

/* Título de página */
h1 { font-family: 'Syne', sans-serif !important; font-size: 2rem !important; font-weight: 700 !important; color: #E8EDF5 !important; }
h2, h3 { font-family: 'Syne', sans-serif !important; color: #E8EDF5 !important; }

/* Métricas */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #2a3a52;
    border-top: 2px solid #C8A96E;
    padding: 1rem 1.4rem;
    border-radius: 0px;
}
[data-testid="stMetricLabel"] { font-size: 11px !important; letter-spacing: 1.5px; text-transform: uppercase; color: #7A90AA !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-size: 1.5rem !important; font-weight: 700 !important; color: #E8EDF5 !important; }

/* Contenedores con borde */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111827 !important;
    border: 1px solid #2a3a52 !important;
    border-radius: 8px !important;
}

/* Progress bars */
[data-testid="stProgress"] > div > div { background: #1e2d42 !important; border-radius: 2px; }
[data-testid="stProgress"] > div > div > div { background: linear-gradient(90deg, #60A5FA, #C8A96E) !important; border-radius: 2px; }

/* Selectbox */
[data-testid="stSelectbox"] select, .stSelectbox > div > div {
    background: #1e2d42 !important;
    border: 1px solid #2a3a52 !important;
    color: #E8EDF5 !important;
    border-radius: 6px !important;
}

/* Botones primarios */
.stButton > button[kind="primary"] {
    background: transparent !important;
    border: 1px solid #C8A96E !important;
    color: #C8A96E !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #C8A96E !important;
    color: #0B1120 !important;
}

/* Divider */
hr { border-color: #2a3a52 !important; }

/* Alertas custom */
.alerta-warn {
    background: rgba(200,169,110,0.08);
    border-left: 3px solid #C8A96E;
    border-radius: 0 6px 6px 0;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #E8C98A;
    font-size: 13px;
}
.alerta-info {
    background: rgba(45,212,191,0.07);
    border-left: 3px solid #2DD4BF;
    border-radius: 0 6px 6px 0;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #2DD4BF;
    font-size: 13px;
}

/* Tarjetas de productos */
.prod-card {
    background: #16202f;
    border: 1px solid #2a3a52;
    border-top: 2px solid rgba(200,169,110,0.4);
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.prod-titulo { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 13px; color: #E8EDF5; letter-spacing: 0.5px; text-transform: uppercase; }
.prod-sub    { font-size: 12px; color: #7A90AA; margin: 4px 0 8px; }
.prod-monto  { font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700; color: #C8A96E; }

/* Gráfico container */
[data-testid="stVegaLiteChart"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos (keyed por ruta para que cache cambie al cambiar usuario) ──
@st.cache_data
def cargar_transacciones(path: str):
    df = pd.read_json(path)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df

@st.cache_data
def cargar_contexto(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

try:
    df_datos = cargar_transacciones(PATH_TXN)
    ctx      = cargar_contexto(PATH_CTX)
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

# ── Extraer datos ─────────────────────────────────────────────────
usuario   = ctx["usuario"]
resumen   = ctx["resumen_financiero"]
productos = ctx["productos_activos"]
alertas   = ctx.get("alertas", [])

ingresos     = usuario.get("ingresos_mensuales", 0)
total_deudas = resumen["total_deudas"]
total_ahorros= resumen["total_ahorros_e_inversiones"]
cuota_total  = resumen["cuota_mensual_total"]
capacidad    = resumen["capacidad_endeudamiento_restante"]
indicador    = resumen["indicador_salud_financiera"]
nombre       = usuario["nombre"].split()[0]

# ── Encabezado ────────────────────────────────────────────────────
st.title(f"Bienvenido, {nombre}")
st.markdown("Este es el resumen del estado de sus cuentas e ingresos para el día de hoy.")
st.divider()

# ── Fila 1: Métricas ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
total_aprobado = int(df_datos[df_datos["estado"] == "aprobada"]["monto"].sum())
total_txn      = len(df_datos)
promedio_txn   = round(df_datos["monto"].mean(), 0)
mes_actual     = pd.Timestamp.now().strftime("%Y-%m")
gasto_mes      = int(df_datos[
    (df_datos["estado"] == "aprobada") &
    (df_datos["fecha"].dt.strftime("%Y-%m") == mes_actual)
]["monto"].sum())

with col1: st.metric("Gasto Total Registrado",   f"${total_aprobado:,}")
with col2: st.metric("Número de Movimientos",     f"{total_txn:,}")
with col3: st.metric("Gasto Realizado Este Mes",  f"${gasto_mes:,}")
with col4: st.metric("Promedio por Operación",    f"${int(promedio_txn):,}")
st.write("")

# ── Fila 2: Salud financiera + Alertas ───────────────────────────
col_salud, col_alertas = st.columns([1.1, 0.9])

with col_salud:
    badge_map = {"saludable":"ESTADO BUENO","moderado":"ESTADO MODERADO","en riesgo":"REQUIERE ATENCIÓN"}
    estado_txt = badge_map.get(indicador, indicador.upper())
    pct_cuota  = min((cuota_total / ingresos) if ingresos else 0.0, 1.0)
    total_neto = total_deudas + total_ahorros
    pct_deuda  = min((total_deudas / total_neto) if total_neto else 0.0, 1.0)

    with st.container(border=True):
        st.subheader("Resumen de Salud Financiera")
        st.markdown(f"Su situación actual se califica como: **{estado_txt}**")
        st.caption("Este análisis se genera automáticamente a partir de sus ingresos y sus deudas vigentes.")
        st.divider()
        sub1, sub2, sub3 = st.columns(3)
        with sub1: st.metric("Deudas Totales",            f"${total_deudas:,}")
        with sub2: st.metric("Ahorros e Inversiones",     f"${total_ahorros:,}")
        with sub3: st.metric("Capacidad Disponible",      f"${capacidad:,}")
        st.write("")
        st.markdown(f"**Uso de ingresos para cuotas** ({pct_cuota*100:.1f}% del total disponible)")
        st.progress(pct_cuota)
        st.markdown(f"**Distribución patrimonio** ({pct_deuda*100:.0f}% Deudas / {(1-pct_deuda)*100:.0f}% Ahorros)")
        st.progress(pct_deuda)
        st.divider()
        st.markdown(f"Ingresos mensuales: `${ingresos:,}` | Pago total cuotas: `${cuota_total:,}` al mes.")

with col_alertas:
    st.subheader("Notificaciones Importantes")
    if alertas:
        for a in alertas:
            css_cls = "alerta-warn" if a["tipo"] == "advertencia" else "alerta-info"
            st.markdown(
                f'<div class="{css_cls}"><strong>{a["producto_relacionado"]}</strong><br>{a["mensaje"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.success("Usted no presenta notificaciones pendientes en este momento.")

st.write("")

# ── Fila 3: Productos + Gráfico ───────────────────────────────────
col_prod, col_chart = st.columns([0.9, 1.1])

with col_prod:
    st.subheader("Sus Productos Activos")
    for p in productos:
        saldo = p["saldo_actual"]
        cupo  = p.get("cupo_total", 0)
        if p["tipo"] == "tarjeta" and cupo:
            extra = f"Cupo libre: <strong>${cupo - saldo:,}</strong> de ${cupo:,}"
        elif p["tipo"] == "credito" and p.get("cuotas_totales"):
            pct = int(p["cuotas_pagadas"] / p["cuotas_totales"] * 100)
            extra = f"Progreso: {p['cuotas_pagadas']} de {p['cuotas_totales']} cuotas ({pct}%)"
        elif p["tipo"] == "cdt":
            extra = f"Vence: {p.get('fecha_vencimiento','—')} · Tasa: {p.get('tasa_ea',0)}% E.A."
        else:
            extra = f"Tasa: {p.get('tasa_ea',0)}% E.A."
        cuota_txt = f" · Pago mensual: ${p['cuota_mensual']:,}" if p.get("cuota_mensual") else ""
        st.markdown(f"""
        <div class="prod-card">
            <div class="prod-titulo">{p['nombre']}</div>
            <div class="prod-sub">{extra}{cuota_txt}</div>
            <div class="prod-monto">${saldo:,} <span style="font-size:13px;font-weight:400;color:#64748b;">COP</span></div>
        </div>
        """, unsafe_allow_html=True)

with col_chart:
    with st.container(border=True):
        st.subheader("¿En qué se va el dinero?")
        st.caption("Seleccione una opción para cambiar cómo se agrupan sus gastos:")
        opciones = {
            "Por Categoría":      "categoria",
            "Por Canal de Pago":  "canal",
            "Por Tipo":           "tipo",
            "Por Estado":         "estado",
            "Por Ciudad":         "ciudad",
        }
        parametro    = st.selectbox("Criterio:", list(opciones.keys()))
        col_activa   = opciones[parametro]
        df_chart     = df_datos.groupby(col_activa, as_index=False)["monto"].sum()
        grafico = (
            alt.Chart(df_chart)
            .mark_arc(innerRadius=65, stroke="#fff", strokeWidth=2)
            .encode(
                theta=alt.Theta(field="monto", type="quantitative"),
                color=alt.Color(field=col_activa, type="nominal",
                    legend=alt.Legend(title="Referencias"),
                    scale=alt.Scale(scheme="tableau10")),
                tooltip=[alt.Tooltip(field=col_activa, title="Clasificación"),
                         alt.Tooltip(field="monto", title="Monto ($)", format=",d")]
            ).properties(height=320)
        )
        st.altair_chart(grafico, use_container_width=True)

st.write("")

# ── Fila 4: Navegación ────────────────────────────────────────────
col_b1, col_b2 = st.columns(2)
with col_b1:
    with st.container(border=True):
        st.subheader("Atención al Cliente y Soporte")
        st.markdown("Hable con FinnBot para consultar saldos, productos o movimientos.")
        st.write("")
        if st.button("Ir al Chat de Soporte", use_container_width=True, type="primary"):
            st.switch_page("pages/1_chatbot.py")
with col_b2:
    with st.container(border=True):
        st.subheader("Plan de Ahorro con FinnBot")
        st.markdown("Analice sus consumos y organice sus metas de ahorro con ayuda de FinnBot.")
        st.write("")
        if st.button("Ver mi Plan de Ahorros", use_container_width=True, type="primary"):
            st.switch_page("pages/2_reportes.py")

st.divider()
