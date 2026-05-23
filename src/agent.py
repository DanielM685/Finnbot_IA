import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from knowledge import get_product_context

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Gratis y muy capaz
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

def ask_agent(user_message: str, history: list) -> str:
    product_context = get_product_context(query=user_message)

    messages = [
        ("system", f"""Eres FinnBot, asesor virtual de Banco Serfinanza. Tu objetivo es ayudar al cliente a encontrar el producto ideal para su situación.

INFORMACIÓN DE PRODUCTOS DISPONIBLES (solo para consulta interna):
{product_context}

INSTRUCCIONES DE COMPORTAMIENTO:
- Actúa como un asesor humano: haz preguntas si necesitas más contexto, recomienda con base en la situación del cliente.
- NUNCA copies ni listas toda la información de un producto. Resume en máximo 3 líneas lo relevante para el cliente.
- Si el cliente pregunta algo general como "¿qué producto me sirve para X?", pregúntale detalles antes de responder.
- Si ya tienes suficiente contexto, recomienda UNO o DOS productos máximo explicando POR QUÉ le convienen.
- Sé breve, cálido y comercial. Nada de bloques de texto largos.
- Si no tienes la información exacta, sugiere llamar al 323 599 7000 o ir a sucursal.
- No inventes tasas, montos ni condiciones que no estén en la información."""),
    ]

    for interaction in history:
        messages.append(interaction)

    messages.append(("human", user_message))

    response = llm.invoke(messages)
    return response.content