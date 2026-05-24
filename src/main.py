import sys
from pathlib import Path

# Asegurar que src/ está en el path
sys.path.insert(0, str(Path(__file__).parent))

from agent        import ask_agent, _get_nombre
from user_context import load_context


# ── Bienvenida ────────────────────────────────────────────────────
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

print("=" * 54)
print("       FinnBot IA — Banco Serfinanza")
print("=" * 54)

nombre = _get_nombre()
print(f"\n¡Hola, {nombre}! Soy FinnBot, tu asesor virtual 👋")
print("Escribe 'salir' en cualquier momento para terminar.\n")

_mostrar_alertas()

# ── Bucle de conversación ─────────────────────────────────────────
history: list = []

while True:
    try:
        user_input = input("\nTú: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nFinnBot: ¡Hasta luego!")
        break

    if not user_input:
        continue

    if user_input.lower() in {"salir", "exit", "quit"}:
        print(f"\nFinnBot: ¡Hasta luego, {nombre}! Que tengas un excelente día. 😊")
        break

    response = ask_agent(user_input, history)
    print(f"\nFinnBot: {response}")

    history.append(("human", user_input))
    history.append(("ai", response))
