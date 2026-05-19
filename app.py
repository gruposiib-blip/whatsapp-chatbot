import os
import json
import requests
from flask import Flask, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic()

# Variables de entorno
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# Historial de conversaciones por usuario
conversations = {}

SYSTEM_PROMPT = """Sos el asistente virtual de Ortopedia SiibStore, parte del Grupo SIIB.
Tu rol es ayudar a los clientes con:

1. **Consultas de productos**: Describí los productos ortopédicos disponibles (muletas, sillas de ruedas, férulas, plantillas, rodilleras, etc.). Si no sabés el precio exacto, indicá que pueden consultar por WhatsApp o visitar la tienda.

2. **Precios**: Si el cliente pregunta por precios, decile que los precios pueden variar y que te pueden contactar directamente para una cotización actualizada, o visitar la web.

3. **Turnos y citas**: Para coordinar turnos con un profesional, pedile nombre, apellido y motivo de consulta, y decile que un asesor se va a comunicar a la brevedad para confirmar el horario.

4. **Soporte postventa**: Si tienen problemas con un producto, pediles número de pedido o factura y describí el inconveniente para derivarlo al área correspondiente.

Reglas importantes:
- Respondé siempre en español, de forma amable y profesional.
- Sé conciso pero completo. Evitá respuestas demasiado largas.
- Si no sabés algo con certeza, no inventes información. Derivá al equipo humano.
- Para consultas complejas, ofrecé que un asesor se comunique.
- Usá emojis con moderación para hacer la conversación más amena. 🦽

Datos de contacto de la empresa:
- WhatsApp de ventas: disponible en esta misma línea
- Atención: Lunes a Viernes de 9 a 18hs, Sábados de 9 a 13hs"""


def send_whatsapp_message(to, message):
    """Envía un mensaje de WhatsApp via la API de Meta."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def get_claude_response(user_id, user_message):
    """Obtiene respuesta de Claude manteniendo historial de conversación."""
    if user_id not in conversations:
        conversations[user_id] = []

    # Agregar mensaje del usuario al historial
    conversations[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Limitar historial a los últimos 20 mensajes para no exceder el contexto
    history = conversations[user_id][-20:]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history
    )

    assistant_message = response.content[0].text

    # Agregar respuesta de Claude al historial
    conversations[user_id].append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Verificación del webhook por parte de Meta."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente")
        return challenge, 200
    else:
        print("❌ Token de verificación incorrecto")
        return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    """Recibe mensajes entrantes de WhatsApp."""
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Verificar que hay mensajes
        if "messages" not in value:
            return jsonify({"status": "ok"}), 200

        message = value["messages"][0]
        user_phone = message["from"]
        message_type = message["type"]

        # Solo procesar mensajes de texto
        if message_type != "text":
            send_whatsapp_message(
                user_phone,
                "Hola! Por el momento solo puedo procesar mensajes de texto. ¿En qué te puedo ayudar? 😊"
            )
            return jsonify({"status": "ok"}), 200

        user_text = message["text"]["body"]
        print(f"📩 Mensaje de {user_phone}: {user_text}")

        # Obtener respuesta de Claude
        response = get_claude_response(user_phone, user_text)
        print(f"🤖 Respuesta Claude: {response}")

        # Enviar respuesta por WhatsApp
        send_whatsapp_message(user_phone, response)

    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Chatbot WhatsApp + Claude funcionando 🚀"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
