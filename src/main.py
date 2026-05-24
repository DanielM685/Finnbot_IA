import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent         import ask_agent,         _get_nombre
from savings_agent import ask_savings_agent
from user_context  import load_context

# ── Alertas ───────────────────────────────────────────────────────
def _mostrar_alertas():
    ctx     = load_context()
    alertas = ctx.get("alertas", [])
    if not alertas:
        return
    print("\n─── Alertas pendientes ───────────────────────────────")
    for a in alertas:
        icono = "⚠️ " if a["tipo"] == "advertencia" else "ℹ️ "
        print(f"{icono}{a['mensaje']}")
    print("──────────────────────────────────────────────────────")


# ── Selección de agente ───────────────────────────────────────────
def _seleccionar_agente() -> str:
    print("\n¿Con quién quieres hablar hoy?")
    print("  [1] FinnBot  — Asesor oficial de Banco Serfinanza")
    print("  [2] Nova     — Tu asesora personal de ahorro e independencia financiera")
    while True:
        opcion = input("\nElige 1 o 2: ").strip()
        if opcion in {"1", "2"}:
            return opcion
        print("Por favor escribe 1 o 2.")


# ── Main ──────────────────────────────────────────────────────────
print("=" * 54)
print("       Serfinanza — Asistentes Virtuales")
print("=" * 54)

nombre = _get_nombre()
print(f"\n¡Hola, {nombre}! 👋")
_mostrar_alertas()

opcion = _seleccionar_agente()

if opcion == "1":
    agente_nombre = "FinnBot"
    agente_fn     = ask_agent
    print(f"\n✅ Conectando con FinnBot, el asesor oficial de Banco Serfinanza.")
else:
    agente_nombre = "Nova"
    agente_fn     = ask_savings_agent
    print(f"\n✅ Conectando con Nova, tu asesora personal de finanzas.")

print(f"Escribe 'salir' para terminar | 'cambiar' para cambiar de agente.\n")

history: list = []

while True:
    try:
        user_input = input("\nTú: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{agente_nombre}: ¡Hasta luego!")
        break

    if not user_input:
        continue

    if user_input.lower() in {"salir", "exit", "quit"}:
        print(f"\n{agente_nombre}: ¡Hasta luego, {nombre}! Que tengas un excelente día. 😊")
        break

    # Cambiar de agente en caliente
    if user_input.lower() == "cambiar":
        history = []  # reinicia el historial al cambiar
        opcion = _seleccionar_agente()
        if opcion == "1":
            agente_nombre = "FinnBot"
            agente_fn     = ask_agent
            print("✅ Ahora hablas con FinnBot.\n")
        else:
            agente_nombre = "Nova"
            agente_fn     = ask_savings_agent
            print("✅ Ahora hablas con Nova.\n")
        continue

    response = agente_fn(user_input, history)
    print(f"\n{agente_nombre}: {response}")

    history.append(("human", user_input))
    history.append(("ai", response))
