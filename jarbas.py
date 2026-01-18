# ===============================
# JARBAS — CÉREBRO (VOZ + IA)
# ===============================

import os
import json
import base64
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key="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")

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
# IA ONLINE (TEXTO)
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
                        "amigo do Jean. Responda curto, claro e inteligente."
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=800
        )
        return resposta.choices[0].message.content.strip()
    except Exception:
        return "Erro ao acessar a IA."

# ===============================
# FUNÇÃO USADA PELA UI 🎤🖼️
# ===============================
def responder(texto, imagem=None):
    if not texto and not imagem:
        return "Não recebi nada, tenta de novo."

    texto = (texto or "").lower().strip()

    if "seu nome" in texto:
        return "Eu sou o Jarbas."

    if "que horas" in texto:
        agora = datetime.now()
        return f"Agora são {agora.hour}:{agora.minute:02d}."

    if "que dia" in texto or "data" in texto:
        agora = datetime.now()
        return f"Hoje é {agora.day}/{agora.month}/{agora.year}."

    if texto in memoria and not imagem:
        return memoria[texto]

    try:
        # ===== COM IMAGEM =====
        if imagem:
            img_bytes = imagem.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é JARBAS, um assistente brasileiro, "
                            "amigo do Jean. Analise imagens e responda curto e claro."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": texto or "O que tem nessa imagem?"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800
            )

            return resposta.choices[0].message.content.strip()

        # ===== SOMENTE TEXTO =====
        resposta = perguntar_ia(texto)
        memoria[texto] = resposta
        salvar_memoria(memoria)
        return resposta

    except Exception:
        return "Erro ao analisar."

