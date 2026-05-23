from agent import ask_agent

history = []

print("=" * 40)
print("   FinnBot IA — Banco Serfinanza")
print("=" * 40)
print("Escribe 'salir' para terminar.\n")

while True:
    user_input = input("Tú: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "salir":
        print("FinnBot: ¡Hasta luego!")
        break

    response = ask_agent(user_input, history)
    print(f"\nFinnBot: {response}\n")

    history.append(("human", user_input))
    history.append(("ai", response))