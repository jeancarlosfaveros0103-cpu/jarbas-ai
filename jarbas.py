# ===============================
# JARBAS — CÉREBRO (VOZ + IA)
# ===============================

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

MEMORIA_FILE = "memoria.json"


# ===============================
# MEMÓRIA
# ===============================
def carregar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def salvar_memoria(memoria):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)


memoria = carregar_memoria()


# ===============================
# IA ONLINE
# ===============================
def perguntar_ia(texto):
    if not API_KEY:
        return "IA online não configurada."

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é JARBAS, um assistente brasileiro, "
                        "amigo do Jean. Responda curto e claro."
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=200
        )
        return resposta.choices[0].message.content.strip()
    except Exception:
        return "Erro ao acessar a IA."


# ===============================
# FUNÇÃO USADA PELA UI 🎤
# ===============================
def responder(texto):
    if not texto:
        return "Não ouvi nada, tenta de novo."

    texto = texto.lower().strip()

    if "seu nome" in texto:
        return "Eu sou o Jarbas."

    if "que horas" in texto:
        agora = datetime.now()
        return f"Agora são {agora.hour}:{agora.minute:02d}."

    if "que dia" in texto or "data" in texto:
        agora = datetime.now()
        return f"Hoje é {agora.day}/{agora.month}/{agora.year}."

    if texto in memoria:
        return memoria[texto]

    # 👉 IA ONLINE
    resposta = perguntar_ia(texto)

    memoria[texto] = resposta
    salvar_memoria(memoria)

    return resposta

