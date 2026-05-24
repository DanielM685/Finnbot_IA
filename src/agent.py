import os
import sys
import json
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
    temperature=0.7,
    max_tokens=1024,  # suficiente para respuestas completas
)

_fmt = lambda v: "$" + f"{float(v):,.0f}".replace(",", ".")


# ── Contexto extendido de transacciones ──────────────────────────
def _get_txn_context_completo() -> str:
    """
    Construye un bloque de texto con TODAS las transacciones del usuario,
    ordenadas de más reciente a más antigua. Incluye ID, fecha, comercio,
    categoría, monto y estado. Así el LLM puede buscar por ID o comercio.
    """
    txns = sorted(
        load_transactions(),
        key=lambda t: (t["fecha"], t.get("hora", "")),
        reverse=True,
    )

    if not txns:
        return "Sin transacciones registradas."

    lines = ["HISTORIAL COMPLETO DE TRANSACCIONES (ordenado de más reciente a más antiguo):"]
    for t in txns:
        estado_tag = "✓" if t["estado"] == "aprobada" else ("✗" if t["estado"] == "rechazada" else "⏳")
        cuotas_txt = f" ({t['cuotas']} cuota{'s' if t['cuotas'] > 1 else ''})" if t.get("cuotas", 1) > 1 else ""
        lines.append(
            f"[{t['id']}] {estado_tag} {t['fecha']} {t.get('hora','')} | "
            f"{t['tipo'].upper()} | {t['comercio']} | "
            f"{t.get('categoria', '')} | {_fmt(t['monto'])}{cuotas_txt} | "
            f"{t['canal']} | {t.get('descripcion', '')}"
        )

    return "\n".join(lines)


# ── Alertas ───────────────────────────────────────────────────────
def _get_alertas() -> str:
    try:
        alertas = load_context().get("alertas", [])
        if not alertas:
            return ""
        lines = ["ALERTAS ACTIVAS DEL CLIENTE:"]
        for a in alertas:
            icono = "⚠️" if a["tipo"] == "advertencia" else "ℹ️"
            lines.append(f"{icono} {a['mensaje']}")
        return "\n".join(lines)
    except Exception:
        return ""


# ── Nombre ────────────────────────────────────────────────────────
def _get_nombre() -> str:
    try:
        nombre = load_context()["usuario"].get("nombre", "").strip()
        return nombre.split()[0] if nombre else "cliente"
    except Exception:
        return "cliente"

def _set_rutas(ctx_path: str = None, txn_path: str = None):
    _txn_mod._TXN_PATH = Path(txn_path) if txn_path else DATA_DIR / "transactions.json"
    _ctx_mod._CTX_PATH = Path(ctx_path) if ctx_path else DATA_DIR / "user_context.json"
    
# ── Función principal ─────────────────────────────────────────────
def ask_agent(user_message: str, history: list, ctx_path: str = None, txn_path: str = None) -> str:
    _set_rutas(ctx_path, txn_path)
    user_info    = get_user_context()
    txn_resumen  = get_txn_context()           # resumen últimos 30 días
    txn_completo = _get_txn_context_completo() # historial completo para búsquedas
    alertas      = _get_alertas()
    product_info = get_product_context(query=user_message)
    nombre       = _get_nombre()

    system_prompt = f"""Eres FinnBot, el asesor virtual de Banco Serfinanza. Atiendes a {nombre}.

{user_info}

{alertas}

{txn_resumen}

{txn_completo}

CATÁLOGO DE PRODUCTOS SERFINANZA (referencia interna):
{product_info}

INSTRUCCIONES GENERALES:
- Usa el nombre del cliente de forma natural pero sin exagerar.
- Responde SIEMPRE con la información EXACTA disponible en los datos. Nunca digas que no tienes un dato si aparece en los datos.
- Para buscar transacciones: usa el HISTORIAL COMPLETO por ID, comercio, categoría o período.
- Si hay alertas activas relacionadas con la pregunta, menciónalas primero.
- Si genuinamente no tienes el dato, sugiere llamar al 01 8000 123 456.

ESTILO DE RESPUESTA — MUY IMPORTANTE:
- Sé BREVE por defecto. Da lo mínimo necesario y ofrece profundizar.
- Si listas varios items (tarjetas, productos, transacciones), menciona SOLO los nombres o un resumen de una línea por item. Luego pregunta: "¿Quieres saber más sobre alguno?"
- Solo da detalles completos cuando el usuario los pida explícitamente.
- Nunca des tablas ni bloques largos a menos que el usuario lo solicite.

PREGUNTAS INICIALES:
- Si es el PRIMER mensaje del usuario (el historial está vacío), antes de responder al fondo hazle DOS preguntas para entender mejor cómo ayudarle:
  1. ¿En qué área le gustaría enfocarse hoy? (ej: consultar saldos, revisar movimientos, conocer productos, resolver un problema)
  2. ¿Hay algo urgente que necesite atender primero?
- Después de esas dos preguntas, responde brevemente al mensaje inicial si aplica."""

    messages = [("system", system_prompt)]
    for interaction in history:
        messages.append(interaction)
    messages.append(("human", user_message))

    response = llm.invoke(messages)
    return response.content

