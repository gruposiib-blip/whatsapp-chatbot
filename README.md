# 🤖 Chatbot WhatsApp + Claude — Ortopedia SiibStore

Chatbot para WhatsApp Business usando la API de Meta y Claude de Anthropic.

## Variables de entorno necesarias

Configurar en Railway (o donde lo deploys):

| Variable | Descripción |
|---|---|
| `WHATSAPP_TOKEN` | Token de acceso de Meta (empieza con EAA...) |
| `PHONE_NUMBER_ID` | ID del número de teléfono de WhatsApp |
| `VERIFY_TOKEN` | Token inventado por vos para verificar el webhook (ej: `mi_token_secreto_123`) |
| `ANTHROPIC_API_KEY` | Tu API key de Anthropic (console.anthropic.com) |

## Deploy en Railway

1. Subí esta carpeta a un repositorio de GitHub
2. Entrá a [railway.app](https://railway.app) y creá un nuevo proyecto desde GitHub
3. Configurá las variables de entorno arriba
4. Railway te va a dar una URL pública (ej: `https://mi-chatbot-wa.up.railway.app`)

## Configurar el webhook en Meta

1. En Meta Developers → tu app → WhatsApp → Configuración
2. En "Webhook", pegá tu URL: `https://TU-URL.up.railway.app/webhook`
3. En "Token de verificación", poné el mismo valor que `VERIFY_TOKEN`
4. Suscribite al evento `messages`

## Estructura del proyecto

```
whatsapp-chatbot/
├── app.py           # Servidor principal
├── requirements.txt # Dependencias Python
├── Procfile         # Configuración para Railway/Heroku
└── README.md        # Este archivo
```
