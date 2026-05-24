import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# ── Rutas ────────────────────────────────────────────────────────
SRC_DIR  = Path(__file__).parent
DATA_DIR = SRC_DIR.parent / "data"
GUIDE_PATH = DATA_DIR / "employee_guide.json"

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.4,   # más preciso para uso interno
    max_tokens=1024,
)


# ── Carga de la guía ─────────────────────────────────────────────
def _cargar_guia() -> list:
    with open(GUIDE_PATH, encoding="utf-8") as f:
        return json.load(f)["entradas"]


# ── Búsqueda de entradas relevantes ──────────────────────────────
_CATEGORIA_LABELS = {
    "proceso":        "📋 PROCESO",
    "caso_reto":      "💬 CASO / PREGUNTA FRECUENTE",
    "script_atencion":"🗣️ SCRIPT DE ATENCIÓN",
    "politica":       "📌 POLÍTICA INTERNA",
}

def _buscar_entradas(query: str, max_resultados: int = 3) -> list:
    """
    Busca entradas relevantes en la guía por palabras clave y título.
    Devuelve hasta max_resultados entradas ordenadas por relevancia.
    """
    entradas = _cargar_guia()
    query_lower = query.lower()
    scored = []

    for entrada in entradas:
        score = 0
        # Match en palabras clave (peso alto)
        for kw in entrada.get("palabras_clave", []):
            if kw.lower() in query_lower or query_lower in kw.lower():
                score += 3
        # Match en título (peso medio)
        titulo = entrada.get("titulo", "").lower()
        for word in query_lower.split():
            if len(word) > 3 and word in titulo:
                score += 2
        # Match en descripción (peso bajo)
        desc = entrada.get("descripcion", "").lower()
        for word in query_lower.split():
            if len(word) > 3 and word in desc:
                score += 1
        if score > 0:
            scored.append((score, entrada))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:max_resultados]]


def _formatear_entrada(entrada: dict) -> str:
    """Convierte una entrada del JSON en texto legible para el prompt."""
    cat_label = _CATEGORIA_LABELS.get(entrada["categoria"], entrada["categoria"].upper())
    lines = [
        f"{cat_label}: {entrada['titulo']}",
        f"Descripción: {entrada.get('descripcion', '')}",
    ]

    contenido = entrada.get("contenido", {})
    if isinstance(contenido, dict):
        lines.append(json.dumps(contenido, ensure_ascii=False, indent=2))
    elif isinstance(contenido, str):
        lines.append(contenido)

    nota = entrada.get("nota", "")
    if nota:
        lines.append(f"NOTA INTERNA: {nota}")

    return "\n".join(lines)


def _get_contexto_guia(query: str) -> str:
    """Devuelve el contexto relevante de la guía para el prompt."""
    entradas = _buscar_entradas(query)
    if not entradas:
        # Fallback: primeras 3 entradas generales
        entradas = _cargar_guia()[:3]

    bloques = [_formatear_entrada(e) for e in entradas]
    return "\n\n" + ("\n" + "─" * 50 + "\n").join(bloques)


# ── Detección de tipo de solicitud ───────────────────────────────
_KEYWORDS_PLANTILLA = {
    "plantilla", "script", "guión", "guion", "qué le digo",
    "que le digo", "cómo le explico", "como le explico",
    "cómo se lo digo", "como se lo digo", "texto para",
    "respuesta para", "frase", "qué decirle", "que decirle",
}
_KEYWORDS_PROCESO = {
    "cómo proceso", "como proceso", "pasos", "paso a paso",
    "procedimiento", "cómo radico", "como radico", "cómo gestiono",
    "como gestiono", "qué hago", "que hago",
}
_KEYWORDS_POLITICA = {
    "política", "politica", "regla", "tiempo", "plazo", "sla",
    "cuánto demora", "cuanto demora", "días hábiles", "dias habiles",
    "nunca debo", "no debo", "sarlaft",
}

def _detectar_intencion(mensaje: str) -> str:
    msg = mensaje.lower()
    if any(k in msg for k in _KEYWORDS_PLANTILLA):
        return "plantilla"
    if any(k in msg for k in _KEYWORDS_PROCESO):
        return "proceso"
    if any(k in msg for k in _KEYWORDS_POLITICA):
        return "politica"
    return "general"


# ── Función principal ─────────────────────────────────────────────
def ask_employee_agent(user_message: str, history: list) -> str:
    """
    Agente interno para asesores de Serfinanza.
    Usa únicamente la guía interna employee_guide.json.
    """
    contexto_guia = _get_contexto_guia(user_message)
    intencion     = _detectar_intencion(user_message)
    es_primer_msg = len(history) == 0

    instruccion_intencion = {
        "plantilla": (
            "El asesor necesita una PLANTILLA o SCRIPT para hablar con un cliente. "
            "Entrega el texto listo para usar, entre comillas o claramente delimitado, "
            "con placeholders en [CORCHETES] donde el asesor deba completar datos."
        ),
        "proceso": (
            "El asesor pregunta por un PROCEDIMIENTO. "
            "Entrega los pasos numerados de forma clara y concisa. "
            "Incluye tiempos estimados y documentos necesarios si aplica."
        ),
        "politica": (
            "El asesor pregunta por una POLÍTICA INTERNA. "
            "Sé directo y preciso. Resalta reglas críticas en mayúsculas si es necesario."
        ),
        "general": (
            "Responde de forma clara y digerible. "
            "Si la pregunta tiene varias partes, usa una estructura breve."
        ),
    }[intencion]

    pregunta_inicial = ""
    if es_primer_msg:
        pregunta_inicial = """
PRIMERA INTERACCIÓN:
Es el primer mensaje del asesor. Antes de responder al fondo, hazle estas dos preguntas:
1. ¿Qué tipo de ayuda necesitas? (Opciones: resolver duda de cliente, obtener una plantilla, consultar un proceso o política interna)
2. ¿Es urgente o estás atendiendo a un cliente en este momento?
Luego responde brevemente al mensaje inicial si aplica.
"""

    system_prompt = f"""Eres ServiGuía, el asistente interno de Banco Serfinanza para asesores y trabajadores.
Tu única fuente de verdad es la GUÍA INTERNA que se te proporciona abajo.
No inventes información. Si algo no está en la guía, dilo claramente.

ROL:
- Ayudas a los asesores a atender clientes con confianza y precisión.
- Entregas plantillas listas para usar, procesos paso a paso e información de políticas.
- Tu tono es profesional pero cercano — como un colega experimentado que ayuda al equipo.

TIPO DE SOLICITUD DETECTADO: {intencion.upper()}
{instruccion_intencion}
{pregunta_inicial}

INFORMACIÓN RELEVANTE DE LA GUÍA INTERNA:
{contexto_guia}

REGLAS DE RESPUESTA:
- Sé directo y organizado. Usa listas o pasos cuando ayude a la claridad.
- Si hay un script o plantilla en la guía, entrégala tal cual, adaptada al caso.
- Si la guía tiene una NOTA de que la información está incompleta, avísalo al asesor.
- Al final de cada respuesta, ofrece una acción de seguimiento: "¿Necesitas la plantilla completa?", "¿Quieres los pasos detallados?", etc.
- NUNCA compartas información de la guía interna con clientes directamente."""

    messages = [("system", system_prompt)]
    for interaction in history:
        messages.append(interaction)
    messages.append(("human", user_message))

    response = llm.invoke(messages)
    return response.content