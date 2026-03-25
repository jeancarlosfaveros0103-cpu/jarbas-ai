# ===============================
# JARBAS — CÉREBRO SUPREMO v5
# COMPLETO E AVANÇADO
# ===============================

import os
import json
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

STATIC_FOLDER = "static"

LIMITE_CONTEXTO = 8
MAX_MEMORIA = 100

# Criar pasta static
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# ===============================
# LOGGER
# ===============================

def log(texto):

    try:

        with open(LOG_FILE, "a", encoding="utf-8") as f:

            f.write(
                f"[{datetime.now()}] {texto}\n"
            )

    except:

        pass

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

            with open(
                MEMORIA_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

    except Exception as erro:

        log(f"Erro carregar memória: {erro}")

    return []

def salvar_memoria(memoria):

    try:

        if len(memoria) > MAX_MEMORIA:

            memoria[:] = memoria[-MAX_MEMORIA:]

        with open(
            MEMORIA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memoria,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as erro:

        log(f"Erro salvar memória: {erro}")

memoria = carregar_memoria()

# ===============================
# ESTADO
# ===============================

def carregar_estado():

    try:

        if os.path.exists(ESTADO_FILE):

            with open(
                ESTADO_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

    except Exception as erro:

        log(f"Erro carregar estado: {erro}")

    return {"raiva": 0}

def salvar_estado(estado):

    try:

        with open(
            ESTADO_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                estado,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as erro:

        log(f"Erro salvar estado: {erro}")

estado = carregar_estado()

# ===============================
# CONTEXTO
# ===============================

def gerar_contexto():

    contexto = ""

    ultimos = memoria[-LIMITE_CONTEXTO:]

    for item in ultimos:

        contexto += (
            f"Usuário: {item['pergunta']}\n"
            f"Jarbas: {item['resposta']}\n"
        )

    return contexto

# ===============================
# CACHE INTELIGENTE
# ===============================

def buscar_cache(pergunta):

    pergunta = pergunta.lower()

    for item in memoria:

        if pergunta in item["pergunta"].lower():

            log("Resposta vinda do cache")

            return item["resposta"]

    return None

# ===============================
# GERADOR DE IMAGEM
# ===============================

def criar_imagem(prompt):

    try:

        resultado = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        imagem_base64 = (
            resultado.data[0].b64_json
        )

        nome = (
            "img_" +
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            ) +
            ".png"
        )

        caminho = os.path.join(
            STATIC_FOLDER,
            nome
        )

        with open(caminho, "wb") as f:

            f.write(
                base64.b64decode(
                    imagem_base64
                )
            )

        log(f"Imagem criada: {caminho}")

        return f"/static/{nome}"

    except Exception as erro:

        log(f"Erro imagem: {erro}")

        return "Erro ao gerar imagem."

# ===============================
# ANALISAR IMAGEM
# ===============================

def analisar_imagem(caminho):

    try:

        with open(caminho, "rb") as f:

            imagem_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Descreva esta imagem."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":
                                f"data:image/png;base64,{imagem_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        texto = (
            resposta.choices[0]
            .message.content
        )

        return remover_emojis(texto)

    except Exception as erro:

        log(f"Erro análise imagem: {erro}")

        return "Erro ao analisar imagem."

# ===============================
# IA PRINCIPAL
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
                    (
                        "Você é JARBAS, "
                        "assistente brasileiro inteligente, "
                        "direto ao ponto, "
                        "sem usar emojis."
                    )
                },

                {
                    "role": "user",
                    "content":
                    contexto +
                    "\nUsuário: " +
                    texto
                }

            ],
            max_tokens=700,
            temperature=0.7
        )

        texto_resp = (
            resposta.choices[0]
            .message.content
            .strip()
        )

        return remover_emojis(
            texto_resp
        )

    except Exception as erro:

        log(f"Erro IA: {erro}")

        return "Erro ao falar com a IA."

# ===============================
# FUNÇÃO PRINCIPAL
# ===============================

def responder(texto, imagem=None):

    if not texto and not imagem:

        return "Digite algo."

    texto_original = texto or ""

    log(f"Pergunta: {texto_original}")

    # ===============================
    # IMAGEM ENVIADA
    # ===============================

    if imagem:

        resposta = analisar_imagem(imagem)

        memoria.append({
            "pergunta":
            "[imagem enviada]",
            "resposta":
            resposta
        })

        salvar_memoria(memoria)

        return resposta

    # ===============================
    # CACHE
    # ===============================

    cache = buscar_cache(texto_original)

    if cache:

        return cache

    texto_lower = texto_original.lower()

    # ===============================
    # COMANDOS DE IMAGEM
    # ===============================

    comandos_imagem = [

        "crie uma imagem",
        "gerar imagem",
        "desenhe",
        "faça uma imagem",
        "imagem de",
        "ilustre"

    ]

    if any(cmd in texto_lower for cmd in comandos_imagem):

        resposta = criar_imagem(
            texto_original
        )

        memoria.append({
            "pergunta":
            texto_original,
            "resposta":
            resposta
        })

        salvar_memoria(memoria)

        return resposta

    # ===============================
    # SISTEMA RAIVA
    # ===============================

    if "jarvis" in texto_lower:

        estado["raiva"] += 1

        respostas = [

            "Meu nome é Jarbas.",
            "Já falei que é Jarbas.",
            "PARA. É JARBAS.",
            "Tá testando minha paciência."

        ]

        resposta = respostas[
            min(
                estado["raiva"],
                len(respostas) - 1
            )
        ]

        salvar_estado(estado)

        return resposta

    # ===============================
    # IA NORMAL
    # ===============================

    resposta = perguntar_ia(
        texto_original
    )

    memoria.append({

        "pergunta":
        texto_original,

        "resposta":
        resposta

    })

    salvar_memoria(memoria)

    log(f"Resposta: {resposta}")

    return resposta
