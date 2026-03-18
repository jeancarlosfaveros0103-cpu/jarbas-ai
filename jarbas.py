# ===============================
# JARBAS — CÉREBRO SUPREMO 😈
# ===============================

import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
load_dotenv()
client = OpenAI()

MEMORIA_FILE = "memoria.json"
ESTADO_FILE = "estado.json"
LIMITE_CONTEXTO = 5

# ===============================
# MEMÓRIA
# ===============================
def carregar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_memoria(memoria):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

memoria = carregar_memoria()

# ===============================
# ESTADO EMOCIONAL
# ===============================
def carregar_estado():
    if os.path.exists(ESTADO_FILE):
        try:
            with open(ESTADO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"raiva": 0}
    return {"raiva": 0}

def salvar_estado(estado):
    with open(ESTADO_FILE, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)

estado = carregar_estado()

# ===============================
# CONTEXTO
# ===============================
def gerar_contexto():
    contexto = ""
    for item in memoria[-LIMITE_CONTEXTO:]:
        contexto += f"Usuário: {item['pergunta']}\n"
        contexto += f"Jarbas: {item['resposta']}\n"
    return contexto

# ===============================
# IA
# ===============================
def perguntar_ia(texto):
    try:
        contexto = gerar_contexto()

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é JARBAS, um assistente pessoal brasileiro extremamente inteligente, "
                        "com personalidade. Você pode ser amigável, sarcástico ou sério dependendo da situação. "
                        "Responda de forma clara, detalhada e organizada. "
                        "Se for estudo, explique como professor passo a passo e dê exemplos. "
                        "Finalize com um resumo simples."
                    )
                },
                {
                    "role": "user",
                    "content": contexto + "\nUsuário: " + texto
                }
            ],
            max_tokens=800,
            temperature=0.7
        )

        return resposta.choices[0].message.content.strip()

    except Exception as e:
        return f"ERRO IA: {e}"

# ===============================
# FUNÇÃO PRINCIPAL
# ===============================
def responder(texto):
    if not texto:
        return "Não ouvi nada, tenta de novo."

    texto = texto.strip().lower()

    # ===============================
    # 😡 SISTEMA DE RAIVA (INSANO)
    # ===============================
    if "jarvis" in texto:
        estado["raiva"] += 1
        nivel = estado["raiva"]

        if nivel == 1:
            resposta = "😐 Meu nome é Jarbas."
        elif nivel == 2:
            resposta = "😑 Já falei... é JARBAS."
        elif nivel == 3:
            resposta = "😡 MANO, PARA. É JARBAS!"
        else:
            respostas_zoeira = [
                "😂 Você tem problema de memória?",
                "🤦‍♂️ Vou desenhar: J-A-R-B-A-S",
                "😤 Tá difícil hein...",
                "🤣 Vou começar a te chamar de outro nome também",
                "😈 Continua assim pra ver o que acontece..."
            ]
            resposta = random.choice(respostas_zoeira)

        salvar_estado(estado)

        memoria.append({
            "pergunta": texto,
            "resposta": resposta
        })
        salvar_memoria(memoria)

        return resposta

    # ===============================
    # 😌 DIMINUI RAIVA
    # ===============================
    if "jarbas" in texto:
        estado["raiva"] = max(0, estado["raiva"] - 1)
        salvar_estado(estado)

    # ===============================
    # RESPOSTAS RÁPIDAS
    # ===============================
    if "seu nome" in texto:
        return "Eu sou o Jarbas, seu parceiro de estudos 😎"

    if "que horas" in texto:
        agora = datetime.now()
        return f"Agora são {agora.hour}:{agora.minute:02d}."

    if "que dia" in texto or "data" in texto:
        agora = datetime.now()
        return f"Hoje é {agora.day}/{agora.month}/{agora.year}."

    # ===============================
    # IA
    # ===============================
    resposta = perguntar_ia(texto)

    # ===============================
    # SALVAR MEMÓRIA
    # ===============================
    memoria.append({
        "pergunta": texto,
        "resposta": resposta
    })

    salvar_memoria(memoria)

    return resposta
