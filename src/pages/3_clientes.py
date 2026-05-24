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
    st.error("Acceso denegado. Esta sección es exclusiva para clientes.")
    if st.button("Ir a la Página de Inicio", use_container_width=True):
        st.switch_page("src/pages/inicio.py")
    st.stop()

# ── CSS personalizado (Patrón de diseño unificado, accesible y limpio) ──
st.markdown("""
<style>
/* Tipografía y accesibilidad general */
html, body, [data-testid="stMarkdownContainer"] p {
    font-size: 15px !important;
    line-height: 1.6 !important;
}

/* Tarjetas de Alerta limpias, sin emojis y con alto contraste */
.alerta-warn {
    background: #fffbeb;
    border-left: 5px solid #d97706;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    color: #92400e;
    font-size: 14px;
}
.alerta-info {
    background: #f0fdf4;
    border-left: 5px solid #16a34a;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    color: #166534;
    font-size: 14px;
}

/* Tarjetas de Producto consistentes */
.prod-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.prod-titulo { 
    font-weight: 700; 
    font-size: 15px; 
    color: #0f172a; 
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.prod-sub { 
    font-size: 13px; 
    color: #475569; 
    margin-top: 4px; 
    margin-bottom: 8px;
}
.prod-monto { 
    font-size: 20px; 
    font-weight: 800; 
    color: #0f2942; 
}

/* Texto destacado para estados financieros sin depender de círculos de color */
.estado-valor {
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
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

# ── ENCABEZADO (Lenguaje claro y bienvenida humana) ─────────────────
st.title(f"Bienvenido, {nombre}")
st.markdown("Este es el resumen del estado de sus cuentas e ingresos para el día de hoy.")
st.divider()

# ══════════════════════════════════════════════════════════════════
# FILA 1: Métricas rápidas de transacciones (Estructura limpia)
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
    st.metric(label="Gasto Total Registrado", value=f"${total_aprobado:,}")
with col2:
    st.metric(label="Número de Movimientos", value=f"{total_txn:,}")
with col3:
    st.metric(label="Gasto Realizado Este Mes", value=f"${gasto_mes:,}")
with col4:
    st.metric(label="Promedio por Operación", value=f"${int(promedio_txn):,}")

st.write("")

# ══════════════════════════════════════════════════════════════════
# FILA 2: Salud financiera (izquierda) + Alertas (derecha)
# ══════════════════════════════════════════════════════════════════
col_salud, col_alertas = st.columns([1.1, 0.9])

with col_salud:
    # Mapeo de estados sin emojis de colores, usando lenguaje natural y descriptivo
    badge_map = {
        "saludable": "ESTADO BUENO",
        "moderado":  "ESTADO MODERADO",
        "en riesgo": "REQUIERE ATENCIÓN",
    }
    estado_txt = badge_map.get(indicador, indicador.upper())

    # Cálculos matemáticos de porcentajes
    pct_cuota   = min((cuota_total / ingresos) if ingresos else 0.0, 1.0)
    total_neto  = total_deudas + total_ahorros
    pct_deuda   = min((total_deudas / total_neto) if total_neto else 0.0, 1.0)

    # Contenedor principal integrado al diseño nativo
    with st.container(border=True):
        st.subheader("Resumen de Salud Financiera")
        st.markdown(f"Su situación actual se califica como: **{estado_txt}**")
        st.caption("Este análisis se genera automáticamente a partir de sus ingresos y sus deudas vigentes.")
        
        st.divider()

        # Métricas principales en 3 columnas internas
        sub_col1, sub_col2, sub_col3 = st.columns(3)
        with sub_col1:
            st.metric("Deudas Totales", f"${total_deudas:,}")
        with sub_col2:
            st.metric("Ahorros e Inversiones", f"${total_ahorros:,}")
        with sub_col3:
            st.metric("Capacidad de Endeudamiento", f"${capacidad:,}")

        st.write("")

        # Barra 1: Cuota mensual vs Ingresos
        st.markdown(f"**Uso de sus ingresos para el pago de cuotas mensuales** ({pct_cuota*100:.1f}% del total disponible)")
        st.progress(pct_cuota)
        
        # Barra 2: Distribución Deuda vs Ahorro
        st.markdown(f"**Distribución de su patrimonio actual** ({pct_deuda*100:.0f}% Deudas / {(1-pct_deuda)*100:.0f}% Ahorros)")
        st.progress(pct_deuda)

        st.divider()
        
        # Detalles informativos complementarios en texto claro
        st.markdown(f"**Detalle de montos:** Ingresos mensuales: `${ingresos:,}` | Pago total de cuotas: `${cuota_total:,}` al mes.")

with col_alertas:
    st.subheader("Notificaciones Importantes")
    if alertas:
        for a in alertas:
            css_cls = "alerta-warn" if a["tipo"] == "advertencia" else "alerta-info"
            # Se eliminaron los prefijos de emojis para mantener una interfaz sobria y legible
            st.markdown(
                f'<div class="{css_cls}"><strong>{a["producto_relacionado"]}</strong><br>{a["mensaje"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.success("Usted no presenta notificaciones ni tareas pendientes en este momento.")

st.write("")

# ══════════════════════════════════════════════════════════════════
# FILA 3: Productos activos (izquierda) + Gráfico (derecha)
# ══════════════════════════════════════════════════════════════════
col_prod, col_chart = st.columns([0.9, 1.1])

with col_prod:
    st.subheader("Sus Productos Activos")

    for p in productos:
        saldo = p["saldo_actual"]
        cupo  = p.get("cupo_total", 0)

        # Configuración de textos informativos según tipo de producto (Sin emojis)
        if p["tipo"] == "tarjeta" and cupo:
            disponible = cupo - saldo
            extra = f"Cupo libre para usar: <strong>${disponible:,}</strong> de un total de ${cupo:,}"
        elif p["tipo"] == "credito" and p.get("cuotas_totales"):
            pagadas = p["cuotas_pagadas"]
            total_c = p["cuotas_totales"]
            pct     = int(pagadas / total_c * 100)
            extra   = f"Progreso de pago: {pagadas} de {total_c} cuotas canceladas ({pct}%)"
        elif p["tipo"] == "cdt":
            extra = f"Fecha de vencimiento: {p.get('fecha_vencimiento', '—')} · Rendimiento: {p.get('tasa_ea', 0)}% E.A."
        else:
            extra = f"Rendimiento del producto: {p.get('tasa_ea', 0)}% E.A."

        cuota_txt = f" · Pago mensual: ${p['cuota_mensual']:,}" if p.get("cuota_mensual") else ""

        st.markdown(f"""
        <div class="prod-card">
            <div class="prod-titulo">{p['nombre']}</div>
            <div class="prod-sub">{extra}{cuota_txt}</div>
            <div class="prod-monto">${saldo:,} <span style="font-size:13px;font-weight:400;color:#64748b;">Pesos (COP)</span></div>
        </div>
        """, unsafe_allow_html=True)

with col_chart:
    with st.container(border=True):
        st.subheader("¿En qué se va el dinero?")
        st.caption("Seleccione una opción en la lista de abajo para cambiar cómo se agrupan sus gastos en el gráfico:")

        opciones_visuales = {
            "Por Categoría de Gasto":    "categoria",
            "Por Canal o Medio de Pago": "canal",
            "Por Tipo de Operación":     "tipo",
            "Por Estado de la Cuenta":   "estado",
            "Por Ciudad":                "ciudad",
        }

        parametro = st.selectbox(
            "Seleccionar criterio de agrupación:",
            options=list(opciones_visuales.keys()),
            index=0
        )

        columna_activa = opciones_visuales[parametro]
        df_chart = df_datos.groupby(columna_activa, as_index=False)["monto"].sum()

        # Gráfico adaptado con colores corporativos y limpios de Altair
        grafico = (
            alt.Chart(df_chart)
            .mark_arc(innerRadius=65, stroke="#fff", strokeWidth=2)
            .encode(
                theta=alt.Theta(field="monto", type="quantitative"),
                color=alt.Color(
                    field=columna_activa,
                    type="nominal",
                    legend=alt.Legend(title="Referencias"),
                    scale=alt.Scale(scheme="tableau10")
                ),
                tooltip=[
                    alt.Tooltip(field=columna_activa, title="Clasificación"),
                    alt.Tooltip(field="monto", title="Dinero total ($)", format=",d"),
                ]
            )
            .properties(height=320)
        )
        st.altair_chart(grafico, use_container_width=True)

st.write("")

# ══════════════════════════════════════════════════════════════════
# FILA 4: Botones de navegación (Con instrucciones explícitas)
# ══════════════════════════════════════════════════════════════════
col_b1, col_b2 = st.columns(2)

with col_b1:
    with st.container(border=True):
        st.subheader("Atención al Cliente y Soporte")
        st.markdown("Si tiene dudas sobre sus saldos, productos o movimientos, presione el botón de abajo para hablar con un asesor virtual.")
        st.write("")
        if st.button("Ir al Chat de Soporte", use_container_width=True, type="primary"):
            st.switch_page("pages/1_chatbot.py")

with col_b2:
    with st.container(border=True):
        st.subheader("Herramientas de Plan de Ahorro")
        st.markdown("Consulte el análisis detallado de sus consumos mensuales y organice sus metas de ahorro futuras, presione el botón de abajo.")
        st.write("")
        if st.button("Ver mi Plan de Ahorros", use_container_width=True, type="primary"):
            st.switch_page("pages/2_reportes.py")

st.divider()