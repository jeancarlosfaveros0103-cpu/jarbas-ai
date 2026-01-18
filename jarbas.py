# ===============================
# JARBAS — CÉREBRO (VOZ + IA)
# ===============================

import os
import json
from datetime import datetime
from openai import OpenAI

# ===============================
# CONFIG
# ===============================

API_KEY = os.getenv("OPENAI_API_KEY") or "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"
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
        resposta = client.responses.create(
            model="gpt-4.1-mini",
            input=texto
        )

        return resposta.output_text.strip()

    except Exception as e:
        print("ERRO IA:", e)
        return "Erro ao acessar a IA."

# ===============================
# FUNÇÃO PRINCIPAL
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

    resposta = perguntar_ia(texto)

    memoria[texto] = resposta
    salvar_memoria(memoria)

    return resposta

