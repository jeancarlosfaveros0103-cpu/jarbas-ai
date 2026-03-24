# ===============================
# JARBAS — CÉREBRO SUPREMO v2
# ===============================

import os
import json
import random
import base64
import re
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
LOG_FILE = "log.txt"

LIMITE_CONTEXTO = 5
MAX_MEMORIA = 50

# ===============================
# LOGGER
# ===============================

def log(texto):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {texto}\n")

# ===============================
# REMOVER EMOJIS
# ===============================

def remover_emojis(texto):

    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F900-\U0001F9FF"
        "]+",
        flags=re.UNICODE
    )

    return emoji_pattern.sub("", texto)

# ===============================
# MEMÓRIA
# ===============================

def carregar_memoria():
    try:
        if os.path.exists(MEMORIA_FILE):
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        log("Erro ao carregar memória")

    return []

def salvar_memoria(memoria):

    # limitar tamanho
    if len(memoria) > MAX_MEMORIA:
        memoria = memoria[-MAX_MEMORIA:]

    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
    except:
        log("Erro ao salvar memória")

memoria = carregar_memoria()

# ===============================
# ESTADO
# ===============================

def carregar_estado():
    try:
        if os.path.exists(ESTADO_FILE):
            with open(ESTADO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        log("Erro ao carregar estado")

    return {"raiva": 0}

def salvar_estado(estado):

    try:
        with open(ESTADO_FILE, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
    except:
        log("Erro ao salvar estado")

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
# CACHE INTELIGENTE
# ===============================

def buscar_cache(pergunta):

    for item in memoria:

        if item["pergunta"].lower() == pergunta.lower():

            return item["resposta"]

    return None

# ===============================
# GERADOR DE IMAGEM
# ===============================

def criar_imagem(prompt):

    try:

        print("Criando imagem...")

        resultado = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        imagem_base64 = resultado.data[0].b64_json

        nome = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        with open(nome, "wb") as f:
            f.write(base64.b64decode(imagem_base64))

        log(f"Imagem criada: {nome}")

        return f"Imagem criada: {nome}"

    except Exception as erro:

        log(f"Erro imagem: {erro}")

        return "Erro ao gerar imagem."

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
                    "content":
                    "Você é JARBAS, um assistente brasileiro inteligente, "
                    "com personalidade variável e respostas claras."
                },
                {
                    "role": "user",
                    "content": contexto + "\nUsuário: " + texto
                }
            ],
            max_tokens=700,
            temperature=0.7
        )

        texto_resp = resposta.choices[0].message.content.strip()

        return remover_emojis(texto_resp)

    except Exception as e:

        log(f"Erro IA: {e}")

        return "Erro ao falar com a IA."

# ===============================
# FUNÇÃO PRINCIPAL
# ===============================

def responder(texto):

    if not texto:
        return "Digite algo."

    texto_original = texto
    texto = texto.lower().strip()

    log(f"Pergunta: {texto_original}")

    # ===============================
    # CACHE
    # ===============================

    cache = buscar_cache(texto_original)

    if cache:
        return cache

    # ===============================
    # IMAGEM
    # ===============================

    comandos_imagem = [
        "crie uma imagem",
        "gerar imagem",
        "desenhe",
        "faça uma imagem",
        "imagem de",
        "ilustre"
    ]

    if any(cmd in texto for cmd in comandos_imagem):

        prompt = texto_original

        resposta = criar_imagem(prompt)

        memoria.append({
            "pergunta": texto_original,
            "resposta": resposta
        })

        salvar_memoria(memoria)

        return resposta

    # ===============================
    # RAIVA
    # ===============================

    if "jarvis" in texto:

        estado["raiva"] += 1

        respostas = [
            "Meu nome é Jarbas.",
            "Já falei que é Jarbas.",
            "PARA. É JARBAS.",
            "Tá testando minha paciência..."
        ]

        resposta = respostas[min(
            estado["raiva"],
            len(respostas) - 1
        )]

        salvar_estado(estado)

        return resposta

    # ===============================
    # IA
    # ===============================

    resposta = perguntar_ia(texto_original)

    memoria.append({
        "pergunta": texto_original,
        "resposta": resposta
    })

    salvar_memoria(memoria)

    log(f"Resposta: {resposta}")

    return resposta
