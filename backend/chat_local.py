import ollama

def generar_respuesta(mensaje, historial):
    historial.append({
        "role": "user",
        "content": mensaje
    })

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": """
                Eres Brujula, un asistente conversacional
                amigable para estudiantes universitarios.

                Por ahora conversa de forma natural.
                No resuelvas dudas académicas ni hagas tareas.

                Responde en español, de forma clara y breve.
                """
            },
            *historial
        ]
    )

    respuesta = response["message"]["content"]

    historial.append({
        "role": "assistant",
        "content": respuesta
    })

    return respuesta


def iniciar_chat():
    historial = []

    print("================================")
    print("       Brujula")
    print(" Conversación local con Ollama")
    print(" Escribe 'salir' para terminar")
    print("================================\n")

    while True:
        mensaje = input("Tú: ")

        if mensaje.lower() == "salir":
            print("Brujula: ¡Hasta luego!")
            break

        if not mensaje.strip():
            continue

        try:
            respuesta = generar_respuesta(mensaje, historial)
            print(f"\Brujula: {respuesta}\n")

        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    iniciar_chat()
