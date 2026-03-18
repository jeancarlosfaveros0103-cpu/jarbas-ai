# ===============================
# JARBAS — CÉREBRO (IA + MEMÓRIA AVANÇADA)
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
client = OpenAI()

MEMORIA_FILE = "memoria.json"
LIMITE_CONTEXTO = 5  # quantas conversas lembrar

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
# GERAR CONTEXTO
# ===============================
def gerar_contexto():
    contexto = ""
    for item in memoria[-LIMITE_CONTEXTO:]:
        contexto += f"Usuário: {item['pergunta']}\n"
        contexto += f"Jarbas: {item['resposta']}\n"
    return contexto

# ===============================
# IA ONLINE
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
                        "Você é JARBAS, um assistente pessoal brasileiro altamente inteligente, "
                        "amigo do Jean. Responda de forma clara, detalhada e organizada. "
                        "Se for pergunta de estudo, explique passo a passo como um professor. "
                        "Sempre que possível, dê exemplos e finalize com um resumo simples."
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
