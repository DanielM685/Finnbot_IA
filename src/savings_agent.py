import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# ── Rutas ────────────────────────────────────────────────────────
SRC_DIR  = Path(__file__).parent
DATA_DIR = SRC_DIR.parent / "data"

sys.path.insert(0, str(SRC_DIR))

import transactions as _txn_mod
import user_context as _ctx_mod
_txn_mod._TXN_PATH = DATA_DIR / "transactions.json"
_ctx_mod._CTX_PATH = DATA_DIR / "user_context.json"

from transactions import (
    load_transactions,
    get_transactions_summary,
    get_context_for_prompt as get_txn_context,
)
from user_context import (
    get_context_for_prompt as get_user_context,
    load_context,
)
from knowledge import get_product_context

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=600,   # forzar concisión desde el modelo
)

_fmt = lambda v: "$" + f"{float(v):,.0f}".replace(",", ".")


# ── Viabilidad financiera ─────────────────────────────────────────
def _calcular_viabilidad() -> str:
    """
    Calcula cuánto dinero real le sobra al usuario cada mes
    y si podría asumir una cuota adicional.
    """
    ctx     = load_context()
    usuario = ctx["usuario"]
    resumen = ctx["resumen_financiero"]

    ingresos      = float(usuario.get("ingresos_mensuales", 0))
    cuota_actual  = float(resumen.get("cuota_mensual_total", 0))
    capacidad     = float(resumen.get("capacidad_endeudamiento_restante", 0))

    # Gasto promedio mensual en transacciones (no deudas)
    summary       = get_transactions_summary()
    gasto_txn_mes = float(summary.get("total_gastado_mes_actual", 0))

    # Ingreso disponible real después de deudas y gastos del mes
    disponible_real = ingresos - cuota_actual - gasto_txn_mes

    return (
        f"VIABILIDAD FINANCIERA ACTUAL:\n"
        f"Ingresos mensuales       : {_fmt(ingresos)}\n"
        f"Cuotas de deuda/mes      : {_fmt(cuota_actual)}\n"
        f"Gasto variable este mes  : {_fmt(gasto_txn_mes)}\n"
        f"Sobrante real estimado   : {_fmt(max(disponible_real, 0))}\n"
        f"Capacidad endeudamiento  : {_fmt(capacidad)}\n"
        f"Indicador salud          : {resumen.get('indicador_salud_financiera', '—')}\n"
        f"\nUSA ESTOS NÚMEROS para decirle directamente si puede o no puede "
        f"asumir una cuota nueva, comprar algo o ahorrar un monto específico."
    )


# ── Análisis de hábitos ───────────────────────────────────────────
def _analizar_habitos() -> str:
    txns    = load_transactions()
    resumen = get_transactions_summary()

    categorias: dict[str, list] = {}
    for t in txns:
        if t.get("estado") != "aprobada":
            continue
        cat = t.get("categoria", "Otro")
        categorias.setdefault(cat, []).append(float(t["monto"]))

    resumen_cats = [
        f"  - {cat}: {_fmt(sum(m))} total | {len(m)} transacciones"
        for cat, m in sorted(categorias.items(), key=lambda x: sum(x[1]), reverse=True)
    ]

    recurrentes       = [t for t in txns if t.get("es_recurrente")]
    total_recurrentes = sum(float(t["monto"]) for t in recurrentes)
    detalle_recurrentes = [
        f"  - {t['comercio']}: {_fmt(t['monto'])}"
        for t in recurrentes
    ]

    return "\n".join([
        "HÁBITOS DE GASTO:",
        f"Mes actual   : {_fmt(resumen['total_gastado_mes_actual'])}",
        f"Mes anterior : {_fmt(resumen['total_gastado_mes_anterior'])}",
        f"Promedio/txn : {_fmt(resumen['promedio_transaccion'])}",
        f"Recurrentes  : {_fmt(total_recurrentes)} ({len(recurrentes)} suscripciones)",
        *detalle_recurrentes,
        "",
        "Por categoría:",
        *resumen_cats,
    ])


# ── Detectar si pide producto ─────────────────────────────────────
_PALABRAS_PRODUCTO = {
    "recomienda", "recomendame", "recomiéndame", "sugiéreme", "sugerir",
    "producto", "cuenta", "cdt", "ahorro", "inversión", "inversion",
    "tarjeta", "crédito", "credito", "préstamo", "prestamo",
    "qué tienen", "que tienen", "tienen algo", "ofrecen",
    "quiero abrir", "quiero uno", "me interesa",
}

def _usuario_pide_producto(mensaje: str) -> bool:
    return any(p in mensaje.lower() for p in _PALABRAS_PRODUCTO)


# ── Nombre ────────────────────────────────────────────────────────
def _get_nombre() -> str:
    try:
        nombre = load_context()["usuario"].get("nombre", "").strip()
        return nombre.split()[0] if nombre else "amigo"
    except Exception:
        return "amigo"


# ── Rutas dinámicas ───────────────────────────────────────────────
def _set_rutas(ctx_path: str = None, txn_path: str = None):
    _txn_mod._TXN_PATH = Path(txn_path) if txn_path else DATA_DIR / "transactions.json"
    _ctx_mod._CTX_PATH = Path(ctx_path) if ctx_path else DATA_DIR / "user_context.json"


# ── Limpiar formato ───────────────────────────────────────────────
def _limpiar_formato(texto: str) -> str:
    texto = re.sub(r'\$\s*', '$', texto)
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)   # quitar bold markdown
    texto = re.sub(r'`([^`]+)`', r'\1', texto)        # quitar backticks
    return texto.strip()


# ── Función principal ─────────────────────────────────────────────
def ask_savings_agent(
    user_message: str,
    history: list,
    ctx_path: str = None,
    txn_path: str = None,
) -> str:
    _set_rutas(ctx_path, txn_path)

    user_info  = get_user_context()
    txn_resumen = get_txn_context()
    habitos    = _analizar_habitos()
    viabilidad = _calcular_viabilidad()
    nombre     = _get_nombre()

    producto_section = ""
    if _usuario_pide_producto(user_message):
        productos = get_product_context(query=user_message)
        producto_section = (
            f"\nEL USUARIO PREGUNTÓ POR PRODUCTOS. Opciones relevantes:\n{productos}\n"
            f"Recomienda máximo 2. Usa los datos de VIABILIDAD para decirle "
            f"directamente si puede o no asumir la cuota de ese producto ahora mismo."
        )

    es_primer_msg = len(history) == 0
    intro = (
        "PRIMER MENSAJE: Saluda brevemente y haz exactamente 2 preguntas: "
        "1) ¿Tiene alguna meta de ahorro en mente? "
        "2) ¿Cuánto cree que podría apartar cómodamente al mes? "
        "No respondas nada más hasta tener esas respuestas.\n\n"
        if es_primer_msg else ""
    )

    
    system_prompt = f"""Eres FinnBot, asesora financiera personal. Directa, honesta y cercana.

{user_info}

{viabilidad}

{txn_resumen}

{habitos}
{producto_section}

REGLAS ESTRICTAS:
{intro}
- MÁXIMO 4 líneas por respuesta. Si necesitas más, usa viñetas cortas.
- Usa los datos reales. NUNCA respondas con generalidades si tienes el número exacto.
- Si alguien pregunta si puede comprar/ahorrar algo: calcula con los datos de VIABILIDAD y di SÍ o NO directamente, con el número que lo justifica.
- Moneda siempre con $. Ejemplo: $3.200.000. Nunca sin el signo.
- Sin markdown, sin asteriscos, sin fórmulas. Solo texto plano.
- Si el usuario pide un producto: dile si puede o no pagarlo con su situación actual antes de recomendarlo."""

    messages = [("system", system_prompt)]
    for interaction in history:
        messages.append(interaction)
    messages.append(("human", user_message))

    response = llm.invoke(messages)
    texto = response.content
    # Reemplazar backticks seguidos de números por $ 
    import re
    texto = texto.replace("$", "").replace("`", "")
    texto = re.sub(r'\b(\d{1,3}(?:\.\d{3})+)\b', r'\1 COP', texto)
    return texto