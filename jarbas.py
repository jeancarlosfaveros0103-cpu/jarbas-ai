# ==========================================
# JARBAS v9 — FUSÃO v6 + MEMÓRIA VETORIAL
# GPT-5 + IMAGEM + CACHE + APRENDIZADO
# ==========================================

import os
import json
import base64
import re
import math
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================
# CONFIG
# ==========================================

load_dotenv()

client = OpenAI()

MEMORIA_FILE = "memoria.json"
VECTOR_FILE = "memoria_vector.json"
IMPORTANTE_FILE = "memoria_importante.json"
ESTADO_FILE = "estado.json"
LOG_FILE = "log.txt"

STATIC_FOLDER = "static"

LIMITE_CONTEXTO = 10
MAX_MEMORIA = 400

os.makedirs(STATIC_FOLDER, exist_ok=True)

# ==========================================
# LOGGER
# ==========================================

def log(texto):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {texto}\n")
    except:
        pass

# ==========================================
# UTILIDADES
# ==========================================

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

def carregar_json(file, default):

    if os.path.exists(file):
        try:
            with open(file,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    return default

def salvar_json(file,data):

    try:
        with open(file,"w",encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception as erro:
        log(f"Erro salvar {file}: {erro}")

# ==========================================
# MEMÓRIA
# ==========================================

memoria = carregar_json(MEMORIA_FILE, [])
vectors = carregar_json(VECTOR_FILE, [])
memoria_importante = carregar_json(
    IMPORTANTE_FILE,
    []
)

estado = carregar_json(
    ESTADO_FILE,
    {"raiva":0}
)

# ==========================================
# IDENTIDADE FIXA
# ==========================================

def garantir_identidade():

    pergunta = "Quem criou você?"

    if not any(
        pergunta.lower()
        in m["pergunta"].lower()
        for m in memoria_importante
    ):

        memoria_importante.append({

            "pergunta": pergunta,
            "resposta": "Eu fui criado por Jean Carlos."

        })

        salvar_json(
            IMPORTANTE_FILE,
            memoria_importante
        )

garantir_identidade()

# ==========================================
# CACHE (do v6)
# ==========================================

def buscar_cache(pergunta):

    pergunta = pergunta.lower()

    for item in memoria:

        if pergunta in item["pergunta"].lower():

            log("Resposta vinda do cache")

            return item["resposta"]

    return None

# ==========================================
# EMBEDDINGS
# ==========================================

def criar_embedding(texto):

    try:

        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=texto
        )

        return emb.data[0].embedding

    except Exception as erro:

        log(f"Erro embedding: {erro}")

        return []

# ==========================================
# SIMILARIDADE
# ==========================================

def similaridade(v1,v2):

    if not v1 or not v2:
        return 0

    dot = sum(a*b for a,b in zip(v1,v2))

    mag1 = math.sqrt(
        sum(a*a for a in v1)
    )

    mag2 = math.sqrt(
        sum(b*b for b in v2)
    )

    if mag1 == 0 or mag2 == 0:
        return 0

    return dot/(mag1*mag2)

# ==========================================
# BUSCA VETORIAL
# ==========================================

def buscar_memoria_semelhante(texto):

    emb = criar_embedding(texto)

    melhor=None
    score_max=0

    for item in vectors:

        score = similaridade(
            emb,
            item["embedding"]
        )

        if score > score_max:

            score_max = score
            melhor = item

    if score_max > 0.85:

        log("Memória vetorial usada")

        return melhor["resposta"]

    return None

# ==========================================
# CONTEXTO
# ==========================================

def gerar_contexto():

    contexto=""

    ultimos = memoria[-LIMITE_CONTEXTO:]

    for item in ultimos:

        contexto += (
            f"Usuário: {item['pergunta']}\n"
            f"Jarbas: {item['resposta']}\n"
        )

    return contexto

# ==========================================
# GERAR IMAGEM
# ==========================================

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
            )
            + ".png"
        )

        caminho = os.path.join(
            STATIC_FOLDER,
            nome
        )

        with open(caminho,"wb") as f:

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

# ==========================================
# ANALISAR IMAGEM (do v6 mantido)
# ==========================================

def analisar_imagem(caminho):

    try:

        with open(caminho,"rb") as f:

            imagem_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

        resposta = client.chat.completions.create(

            model="gpt-5-mini",

            messages=[

                {
                    "role":"user",
                    "content":[

                        {
                            "type":"text",
                            "text":
                            "Descreva esta imagem."
                        },

                        {
                            "type":"image_url",
                            "image_url":{
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

# ==========================================
# APRENDIZADO MANUAL
# ==========================================

def aprender_manual(texto):

    try:

        if "=" in texto:

            partes = texto.split("=")

            pergunta = partes[0].replace(
                "aprenda:",
                ""
            ).strip()

            resposta = partes[1].strip()

            memoria.append({

                "pergunta": pergunta,
                "resposta": resposta

            })

            salvar_json(
                MEMORIA_FILE,
                memoria
            )

            return "Aprendido com sucesso."

    except:

        pass

    return None

# ==========================================
# IA
# ==========================================

def perguntar_ia(texto):

    try:

        contexto = gerar_contexto()

        resposta = client.chat.completions.create(

            model="gpt-5-mini",

            messages=[

                {
                    "role":"system",
                    "content":
                    (
                        "Você é JARBAS, criado por Jean Carlos. "
                        "Jean é seu criador e dono. "
                        "Nunca esqueça isso. "
                        "Não use emojis."
                    )
                },

                {
                    "role":"user",
                    "content":
                    contexto +
                    "\nUsuário: " +
                    texto
                }

            ],

            max_tokens=800,
            temperature=0.6

        )

        texto_resp = (
            resposta.choices[0]
            .message.content
            .strip()
        )

        return remover_emojis(texto_resp)

    except Exception as erro:

        log(f"Erro IA: {erro}")

        return "Erro ao falar com Jarbas."

# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================

def responder(texto, imagem=None):

    if not texto and not imagem:

        return "Digite algo."

    log(f"Pergunta: {texto}")

    texto_lower = texto.lower()

    # ==========================
    # MEMÓRIA IMPORTANTE
    # ==========================

    for item in memoria_importante:

        if texto_lower in item["pergunta"].lower():

            return item["resposta"]

    # ==========================
    # APRENDER
    # ==========================

    if texto_lower.startswith("aprenda:"):

        resp = aprender_manual(texto)

        if resp:
            return resp

    # ==========================
    # CACHE
    # ==========================

    cache = buscar_cache(texto)

    if cache:
        return cache

    # ==========================
    # BUSCA VETORIAL
    # ==========================

    resposta_memoria = buscar_memoria_semelhante(texto)

    if resposta_memoria:

        return resposta_memoria

    # ==========================
    # IMAGEM RECEBIDA
    # ==========================

    if imagem:

        resposta = analisar_imagem(imagem)

    # ==========================
    # GERAR IMAGEM
    # ==========================

    elif any(
        cmd in texto_lower
        for cmd in [
            "crie imagem",
            "gerar imagem",
            "imagem de",
            "desenhe"
        ]
    ):

        resposta = criar_imagem(texto)

    # ==========================
    # IA NORMAL
    # ==========================

    else:

        resposta = perguntar_ia(texto)

    # ==========================
    # SALVAR MEMÓRIA
    # ==========================

    memoria.append({

        "pergunta": texto,
        "resposta": resposta

    })

    salvar_json(
        MEMORIA_FILE,
        memoria
    )

    # ==========================
    # SALVAR EMBEDDING
    # ==========================

    emb = criar_embedding(texto)

    vectors.append({

        "pergunta": texto,
        "resposta": resposta,
        "embedding": emb

    })

    salvar_json(
        VECTOR_FILE,
        vectors
    )

    log(f"Resposta: {resposta}")

    return resposta
