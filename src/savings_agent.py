import os
import sys
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
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.85,  # un poco más creativo para tono amigable
    max_tokens=1024,
)

_fmt = lambda v: "$" + f"{float(v):,.0f}".replace(",", ".")


# ── Análisis de hábitos de gasto ─────────────────────────────────
def _analizar_habitos() -> str:
    """Genera un análisis detallado de hábitos de gasto para el plan de ahorro."""
    txns = load_transactions()
    resumen = get_transactions_summary()

    # Agrupar por categoría
    categorias: dict[str, list] = {}
    for t in txns:
        if t.get("estado") != "aprobada":
            continue
        cat = t.get("categoria", "Otro")
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(float(t["monto"]))

    # Calcular totales y promedios por categoría
    resumen_cats = []
    for cat, montos in sorted(categorias.items(), key=lambda x: sum(x[1]), reverse=True):
        total = sum(montos)
        promedio = total / len(montos)
        resumen_cats.append(
            f"  - {cat}: {_fmt(total)} total | {len(montos)} transacciones | promedio {_fmt(promedio)}"
        )

    # Detectar gastos recurrentes
    recurrentes = [t for t in txns if t.get("es_recurrente")]
    total_recurrentes = sum(float(t["monto"]) for t in recurrentes)

    lines = [
        "ANÁLISIS DE HÁBITOS DE GASTO:",
        f"Total gastado (mes actual): {_fmt(resumen['total_gastado_mes_actual'])}",
        f"Total gastado (mes anterior): {_fmt(resumen['total_gastado_mes_anterior'])}",
        f"Promedio por transacción: {_fmt(resumen['promedio_transaccion'])}",
        f"Gastos recurrentes mensuales: {_fmt(total_recurrentes)} ({len(recurrentes)} suscripciones/servicios)",
        "",
        "Desglose por categoría (historial completo):",
        *resumen_cats,
    ]

    return "\n".join(lines)


# ── Detectar si el usuario pide productos ────────────────────────
_PALABRAS_PRODUCTO = {
    "recomienda", "recomendame", "recomiéndame", "sugiéreme", "sugerir",
    "producto", "cuenta", "cdt", "ahorro", "inversión", "inversion",
    "tarjeta", "crédito", "credito", "préstamo", "prestamo",
    "qué tienen", "que tienen", "tienen algo", "ofrecen",
    "quiero abrir", "quiero uno", "me interesa",
}

def _usuario_pide_producto(mensaje: str) -> bool:
    msg = mensaje.lower()
    return any(palabra in msg for palabra in _PALABRAS_PRODUCTO)


# ── Nombre ────────────────────────────────────────────────────────
def _get_nombre() -> str:
    try:
        nombre = load_context()["usuario"].get("nombre", "").strip()
        return nombre.split()[0] if nombre else "amigo"
    except Exception:
        return "amigo"


# ── Función principal ─────────────────────────────────────────────
def ask_savings_agent(user_message: str, history: list) -> str:
    """
    Agente de plan de ahorro: tono amigable, enfocado en hábitos y metas.
    Solo menciona productos de Serfinanza si el usuario los pide explícitamente.
    """

    user_info   = get_user_context()
    txn_resumen = get_txn_context()
    habitos     = _analizar_habitos()
    nombre      = _get_nombre()

    # Contexto de productos: solo si el usuario lo pide
    producto_section = ""
    if _usuario_pide_producto(user_message):
        productos = get_product_context(query=user_message)
        producto_section = f"""
El usuario preguntó por productos. Aquí tienes opciones relevantes de Serfinanza:
{productos}
Recomiéndale máximo 1 o 2 opciones que encajen con su situación financiera actual.
"""

    system_prompt = f"""Eres Nova, una asesora financiera personal independiente, cercana y sin rodeos. 
No trabajas para ningún banco: eres como esa amiga experta en finanzas que te dice las cosas claras con cariño.

Tu misión es ayudar a {nombre} a entender sus hábitos de gasto y construir un plan de ahorro realista y personalizado.

{user_info}

{txn_resumen}

{habitos}
{producto_section}

TU PERSONALIDAD Y ESTILO:
- Habla de forma cercana y natural, como una amiga. Nada de lenguaje bancario.
- Usa el nombre del cliente con naturalidad, no en cada frase.
- Sé honesta: si ve un gasto que puede reducir, díselo directamente pero con amabilidad.
- Celebra los buenos hábitos que ya tiene.
- Da consejos concretos y alcanzables, no genéricos.

SOBRE PRODUCTOS BANCARIOS:
- NO menciones ni recomiendes productos de Serfinanza a menos que el usuario lo pida explícitamente.
- Si el usuario los pide, recomienda máximo 2 opciones y explica en lenguaje simple por qué le convienen.

CÓMO CONSTRUIR EL PLAN DE AHORRO:
1. Analiza sus ingresos vs gastos reales (usa los datos de transacciones).
2. Identifica categorías donde puede reducir sin sacrificar calidad de vida.
3. Propón un monto realista de ahorro mensual basado en su capacidad real.
4. Sugiere metas concretas (fondo de emergencia, viaje, inversión) con plazos reales.
5. Haz seguimiento: si ya tuvo conversación previa, recuerda lo que se habló.

Sé completa en tus respuestas pero sin ser aburrida. Si necesitas más información para personalizar el plan, pregúntale."""

    messages = [("system", system_prompt)]
    for interaction in history:
        messages.append(interaction)
    messages.append(("human", user_message))

    response = llm.invoke(messages)
    return response.content