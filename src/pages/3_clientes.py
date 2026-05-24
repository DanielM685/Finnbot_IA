import streamlit as st
import pandas as pd
import altair as alt
import json
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Panel de Cliente — Serfinanza",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "rol" not in st.session_state or st.session_state.rol != "cliente":
    st.error("⚠️ Acceso denegado. Esta sección es exclusiva para clientes.")
    if st.button("Ir a la Página de Inicio", use_container_width=True):
        st.switch_page("src/pages/inicio.py")
    st.stop()

# ── CSS personalizado ─────────────────────────────────────────────
st.markdown("""
<style>
/* Tarjeta de salud financiera */
.salud-card {
    background: linear-gradient(135deg, #0f2942 0%, #1a3f6f 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    margin-bottom: 8px;
}
.salud-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}
.badge-saludable  { background: #22c55e; color: #052e16; }
.badge-moderado   { background: #f59e0b; color: #1c1003; }
.badge-en-riesgo  { background: #ef4444; color: #1c0202; }

/* Barra de progreso custom */
.barra-wrap { margin: 8px 0 16px 0; }
.barra-label { font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
.barra-bg {
    background: rgba(255,255,255,0.12);
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
}
.barra-fill {
    height: 10px;
    border-radius: 8px;
    transition: width 0.6s ease;
}

/* Tarjeta de alerta */
.alerta-warn {
    background: #fff7ed;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 14px;
    color: #1a1a1a;
}
.alerta-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 14px;
    color: #1a1a1a;
}

/* Tarjeta de producto */
.prod-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.prod-titulo { font-weight: 700; font-size: 14px; color: #0f172a; }
.prod-sub    { font-size: 12px; color: #64748b; margin-top: 2px; }
.prod-monto  { font-size: 18px; font-weight: 800; color: #0f2942; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)


# ── Carga de datos ────────────────────────────────────────────────
PATH_TXN  = "data/transactions.json"
PATH_CTX  = "data/user_context.json"

@st.cache_data
def cargar_transacciones():
    df = pd.read_json(PATH_TXN)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df

@st.cache_data
def cargar_contexto():
    with open(PATH_CTX, encoding="utf-8") as f:
        return json.load(f)

try:
    df_datos    = cargar_transacciones()
    ctx         = cargar_contexto()
    datos_ok    = True
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    datos_ok = False
    st.stop()

# ── Extraer datos del contexto ────────────────────────────────────
usuario   = ctx["usuario"]
resumen   = ctx["resumen_financiero"]
productos = ctx["productos_activos"]
alertas   = ctx.get("alertas", [])

ingresos        = usuario.get("ingresos_mensuales", 0)
total_deudas    = resumen["total_deudas"]
total_ahorros   = resumen["total_ahorros_e_inversiones"]
cuota_total     = resumen["cuota_mensual_total"]
capacidad       = resumen["capacidad_endeudamiento_restante"]
indicador       = resumen["indicador_salud_financiera"]
nombre          = usuario["nombre"].split()[0]

# ── ENCABEZADO ────────────────────────────────────────────────────
st.markdown(f"## 👋 Hola, {nombre}")
st.markdown("Tu resumen financiero personal de hoy.")
st.divider()

# ══════════════════════════════════════════════════════════════════
# FILA 1: Métricas rápidas de transacciones
# ══════════════════════════════════════════════════════════════════
col1, col2, col3, col4 = st.columns(4)

total_aprobado = int(df_datos[df_datos["estado"] == "aprobada"]["monto"].sum())
total_txn      = len(df_datos)
promedio_txn   = round(df_datos["monto"].mean(), 0)
mes_actual     = pd.Timestamp.now().strftime("%Y-%m")
gasto_mes      = int(df_datos[
    (df_datos["estado"] == "aprobada") &
    (df_datos["fecha"].dt.strftime("%Y-%m") == mes_actual)
]["monto"].sum())

with col1:
    st.metric("💳 Gasto Total Registrado",  f"${total_aprobado:,}")
with col2:
    st.metric("🔢 Total Movimientos",        f"{total_txn:,}")
with col3:
    st.metric("📅 Gasto Este Mes",           f"${gasto_mes:,}")
with col4:
    st.metric("📊 Promedio por Transacción", f"${int(promedio_txn):,}")

st.write("")

# ══════════════════════════════════════════════════════════════════
# FILA 2: Salud financiera (izquierda) + Alertas (derecha)
# ══════════════════════════════════════════════════════════════════
col_salud, col_alertas = st.columns([1.1, 0.9])

with col_salud:
    # 1. Mapeo de estados (Usamos texto nativo con emojis en lugar de Badges CSS)
    badge_map = {
        "saludable": "🟢 SALUDABLE",
        "moderado":  "🟡 MODERADO",
        "en riesgo": "🔴 EN RIESGO",
    }
    estado_txt = badge_map.get(indicador, indicador.upper())

    # 2. Cálculos matemáticos de porcentajes
    pct_cuota   = min((cuota_total / ingresos) if ingresos else 0.0, 1.0) # st.progress pide valor entre 0.0 y 1.0
    total_neto  = total_deudas + total_ahorros
    pct_deuda   = min((total_deudas / total_neto) if total_neto else 0.0, 1.0)

    # 3. Contenedor principal que simula la tarjeta
    with st.container(border=True):
        # Encabezado y Estado
        st.subheader("📊 Salud Financiera")
        st.caption(f"Estado actual: **{estado_txt}** — Basado en tus productos activos e ingresos")
        
        st.divider()

        # Métricas principales en 3 columnas internas
        sub_col1, sub_col2, sub_col3 = st.columns(3)
        with sub_col1:
            st.metric("Deudas Totales", f"${total_deudas:,}")
        with sub_col2:
            st.metric("Ahorros e Inversiones", f"${total_ahorros:,}")
        with sub_col3:
            st.metric("Capacidad Disponible", f"${capacidad:,}")

        st.write("") # Espacio

        # Barra 1: Cuota mensual vs Ingresos
        st.write(f"**Cuota mensual vs ingresos** ({pct_cuota*100:.1f}% de ${ingresos:,})")
        st.progress(pct_cuota)
        
        # Barra 2: Distribución Deuda vs Ahorro
        st.write(f"**Distribución de capital** ({pct_deuda*100:.0f}% Deuda / {(1-pct_deuda)*100:.0f}% Ahorros)")
        st.progress(pct_deuda)

        st.divider()
        
        # Pie de tarjeta con datos informativos
        st.caption(f"💰 **Ingresos mensuales:** ${ingresos:,} | 💳 **Cuota total:** ${cuota_total:,}/mes")

with col_alertas:
    st.markdown("#### 🔔 Alertas Activas")
    if alertas:
        for a in alertas:
            css_cls = "alerta-warn" if a["tipo"] == "advertencia" else "alerta-info"
            icono   = "⚠️" if a["tipo"] == "advertencia" else "ℹ️"
            st.markdown(
                f'<div class="{css_cls}">{icono} <strong>{a["producto_relacionado"]}</strong><br>{a["mensaje"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.success("✅ No tienes alertas pendientes.")

st.write("")

# ══════════════════════════════════════════════════════════════════
# FILA 3: Productos activos (izquierda) + Gráfico (derecha)
# ══════════════════════════════════════════════════════════════════
col_prod, col_chart = st.columns([0.9, 1.1])

with col_prod:
    st.markdown("#### 🏦 Tus Productos Activos")

    tipo_iconos = {
        "tarjeta": "💳",
        "credito": "🏦",
        "cdt":     "📈",
        "ahorro":  "🐷",
    }

    for p in productos:
        icono = tipo_iconos.get(p["tipo"], "📄")
        saldo = p["saldo_actual"]
        cupo  = p.get("cupo_total", 0)

        # Línea extra según tipo
        if p["tipo"] == "tarjeta" and cupo:
            disponible = cupo - saldo
            extra = f"Cupo disponible: <strong>${disponible:,}</strong> de ${cupo:,}"
        elif p["tipo"] == "credito" and p.get("cuotas_totales"):
            pagadas = p["cuotas_pagadas"]
            total_c = p["cuotas_totales"]
            pct     = int(pagadas / total_c * 100)
            extra   = f"Progreso: {pagadas}/{total_c} cuotas ({pct}%)"
        elif p["tipo"] == "cdt":
            extra = f"Vence: {p.get('fecha_vencimiento', '—')} · Tasa: {p.get('tasa_ea', 0)}% E.A."
        else:
            extra = f"Tasa: {p.get('tasa_ea', 0)}% E.A."

        cuota_txt = f" · Cuota: ${p['cuota_mensual']:,}/mes" if p.get("cuota_mensual") else ""

        st.markdown(f"""
        <div class="prod-card">
            <div class="prod-titulo">{icono} {p['nombre']}</div>
            <div class="prod-sub">{extra}{cuota_txt}</div>
            <div class="prod-monto">${saldo:,} <span style="font-size:12px;font-weight:400;color:#64748b;">COP</span></div>
        </div>
        """, unsafe_allow_html=True)

with col_chart:
    with st.container(border=True):
        st.subheader("📊 Distribución de Gastos")

        opciones_visuales = {
            "Categoría":            "categoria",
            "Canal de Pago":        "canal",
            "Tipo de Transacción":  "tipo",
            "Estado":               "estado",
            "Ciudad":               "ciudad",
        }

        parametro = st.selectbox(
            "Agrupar por:",
            options=list(opciones_visuales.keys()),
            index=0,
            label_visibility="collapsed"
        )

        columna_activa = opciones_visuales[parametro]
        df_chart = df_datos.groupby(columna_activa, as_index=False)["monto"].sum()

        grafico = (
            alt.Chart(df_chart)
            .mark_arc(innerRadius=65, stroke="#fff", strokeWidth=2)
            .encode(
                theta=alt.Theta(field="monto", type="quantitative"),
                color=alt.Color(
                    field=columna_activa,
                    type="nominal",
                    legend=alt.Legend(title=parametro),
                    scale=alt.Scale(scheme="tableau10")
                ),
                tooltip=[
                    alt.Tooltip(field=columna_activa, title=parametro),
                    alt.Tooltip(field="monto", title="Monto ($)", format=",d"),
                ]
            )
            .properties(height=300)
        )
        st.altair_chart(grafico, use_container_width=True)

st.write("")

# ══════════════════════════════════════════════════════════════════
# FILA 4: Botones de navegación
# ══════════════════════════════════════════════════════════════════
col_b1, col_b2 = st.columns(2)

with col_b1:
    with st.container(border=True):
        st.subheader("💬 Consultas y Soporte")
        st.write("Pregunta sobre tus productos, saldos, movimientos o cualquier duda sobre Serfinanza.")
        st.write("")
        if st.button("💬 Abrir Chat de Soporte", use_container_width=True, type="primary"):
            st.switch_page("pages/1_chatbot.py")

with col_b2:
    with st.container(border=True):
        st.subheader("📊 Plan de Ahorros con Nova")
        st.write("Analiza tus hábitos de gasto y construye un plan de ahorro personalizado.")
        st.write("")
        if st.button("📂 Ir al Plan de Ahorros", use_container_width=True):
            st.switch_page("pages/2_reportes.py")

st.divider()