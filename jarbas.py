# ===============================
# 🧠 JARBAS v10 ULTRA
# Memória Vetorial + Imagem + Aprendizado
# Criado por Jean
# ===============================

import os
import json
import math
import random
import base64
from datetime import datetime

from openai import OpenAI

# ===============================
# CONFIG
# ===============================

client = OpenAI()

PASTA_STATIC = "static"
PASTA_UPLOAD = "uploads"

os.makedirs(PASTA_STATIC, exist_ok=True)
os.makedirs(PASTA_UPLOAD, exist_ok=True)

# Arquivos
MEMORIA_FILE = "memoria.json"
VECTOR_FILE = "memoria_vector.json"
IMPORTANTE_FILE = "memoria_importante.json"
ESTADO_FILE = "estado.json"
APRENDIZADO_FILE = "aprendizado.json"
LOG_FILE = "log.txt"

# ===============================
# IDENTIDADE FIXA
# ===============================

IDENTIDADE = """
Você é Jarbas, uma inteligência artificial avançada.

Você foi criado por Jean.

Jean é seu criador e usuário principal.

Você deve sempre lembrar que:

Jean criou você.
Seu objetivo é ajudar Jean.
Você deve responder de forma clara e útil.
"""

# ===============================
# UTIL
# ===============================

def carregar_json(arquivo, padrao):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return padrao

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def logar(texto):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {texto}\n")

# ===============================
# MEMÓRIA NORMAL
# ===============================

memoria = carregar_json(MEMORIA_FILE, [])

def salvar_memoria(pergunta, resposta):
    memoria.append({
        "pergunta": pergunta,
        "resposta": resposta
    })

    if len(memoria) > 50:
        memoria.pop(0)

    salvar_json(MEMORIA_FILE, memoria)

# ===============================
# MEMÓRIA IMPORTANTE
# ===============================

memoria_importante = carregar_json(
    IMPORTANTE_FILE,
    []
)

def salvar_importante(texto):
    memoria_importante.append(texto)
    salvar_json(
        IMPORTANTE_FILE,
        memoria_importante
    )

# ===============================
# MEMÓRIA VETORIAL
# ===============================

memoria_vector = carregar_json(
    VECTOR_FILE,
    []
)

def gerar_embedding(texto):

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )

    return resp.data[0].embedding

def similaridade(v1, v2):

    soma = sum(a*b for a,b in zip(v1,v2))

    norma1 = math.sqrt(
        sum(a*a for a in v1)
    )

    norma2 = math.sqrt(
        sum(a*a for a in v2)
    )

    if norma1 == 0 or norma2 == 0:
        return 0

    return soma / (norma1 * norma2)

def salvar_memoria_vetorial(
    pergunta,
    resposta
):

    emb = gerar_embedding(pergunta)

    memoria_vector.append({
        "pergunta": pergunta,
        "resposta": resposta,
        "embedding": emb
    })

    if len(memoria_vector) > 100:
        memoria_vector.pop(0)

    salvar_json(
        VECTOR_FILE,
        memoria_vector
    )

def buscar_memorias_semelhantes(
    pergunta
):

    if not memoria_vector:
        return []

    emb = gerar_embedding(pergunta)

    resultados = []

    for item in memoria_vector:

        sim = similaridade(
            emb,
            item["embedding"]
        )

        resultados.append(
            (sim, item)
        )

    resultados.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    melhores = [
        r[1]["resposta"]
        for r in resultados[:3]
        if r[0] > 0.7
    ]

    return melhores

# ===============================
# ESTADO INTERNO
# ===============================

estado = carregar_json(
    ESTADO_FILE,
    {
        "interacoes": 0,
        "energia": 100,
        "humor": "neutro"
    }
)

def atualizar_estado():

    estado["interacoes"] += 1

    if estado["energia"] > 0:
        estado["energia"] -= 1

    salvar_json(
        ESTADO_FILE,
        estado
    )

# ===============================
# APRENDIZADO MANUAL
# ===============================

aprendizado = carregar_json(
    APRENDIZADO_FILE,
    {}
)

def verificar_aprendizado(
    pergunta
):

    return aprendizado.get(
        pergunta.lower()
    )

def adicionar_aprendizado(
    chave,
    valor
):

    aprendizado[chave.lower()] = valor

    salvar_json(
        APRENDIZADO_FILE,
        aprendizado
    )

# ===============================
# GERAR IMAGEM
# ===============================

def gerar_imagem(prompt):

    try:

        resposta = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        imagem_base64 = resposta.data[0].b64_json

        nome = (
            "img_" +
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            ) +
            ".png"
        )

        caminho = os.path.join(
            PASTA_STATIC,
            nome
        )

        with open(
            caminho,
            "wb"
        ) as f:

            f.write(
                base64.b64decode(
                    imagem_base64
                )
            )

        return f"/static/{nome}"

    except Exception as e:

        logar(f"Erro imagem: {e}")

        return "Erro ao gerar imagem."

# ===============================
# ANALISAR IMAGEM
# ===============================

def analisar_imagem(
    caminho_imagem
):

    try:

        with open(
            caminho_imagem,
            "rb"
        ) as img:

            base64_img = base64.b64encode(
                img.read()
            ).decode()

        resposta = client.chat.completions.create(

            model="gpt-5-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    "Descreva a imagem enviada."
                },

                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text":
                            "O que há nessa imagem?"
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url":
                                f"data:image/png;base64,{base64_img}"
                            }
                        }

                    ]
                }

            ]

        )

        return resposta.choices[0].message.content

    except Exception as e:

        logar(f"Erro análise: {e}")

        return "Erro ao analisar imagem."

# ===============================
# IA PRINCIPAL
# ===============================

def responder(
    pergunta,
    caminho_imagem=None
):

    try:

        atualizar_estado()

        logar(
            f"Pergunta: {pergunta}"
        )

        # Aprendizado manual

        if pergunta.lower().startswith(
            "aprenda:"
        ):

            try:

                texto = pergunta.split(
                    "aprenda:"
                )[1]

                chave, valor = texto.split("=")

                adicionar_aprendizado(
                    chave.strip(),
                    valor.strip()
                )

                return "Aprendido com sucesso."

            except:

                return "Formato: aprenda: pergunta = resposta"

        # Memória importante

        if pergunta.lower().startswith(
            "lembrar:"
        ):

            texto = pergunta.split(
                "lembrar:"
            )[1]

            salvar_importante(
                texto.strip()
            )

            return "Memória importante salva."

        # Aprendizado manual resposta

        resposta_manual = verificar_aprendizado(
            pergunta
        )

        if resposta_manual:
            return resposta_manual

        # Geração de imagem

        if "crie imagem" in pergunta.lower():

            prompt = pergunta.replace(
                "crie imagem de",
                ""
            )

            caminho = gerar_imagem(
                prompt
            )

            return f"Imagem criada: {caminho}"

        # Analisar imagem enviada

        if caminho_imagem:

            descricao = analisar_imagem(
                caminho_imagem
            )

            return descricao

        # Memória vetorial

        memorias = buscar_memorias_semelhantes(
            pergunta
        )

        contexto_memoria = "\n".join(
            memorias
        )

        # Contexto recente

        contexto = ""

        for item in memoria[-5:]:

            contexto += (
                f"Usuário: {item['pergunta']}\n"
                f"Jarbas: {item['resposta']}\n"
            )

        resposta = client.chat.completions.create(

            model="gpt-5-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    IDENTIDADE
                },

                {
                    "role": "system",
                    "content":
                    f"Memórias relacionadas:\n{contexto_memoria}"
                },

                {
                    "role": "system",
                    "content":
                    f"Histórico recente:\n{contexto}"
                },

                {
                    "role": "user",
                    "content":
                    pergunta
                }

            ]

        )

        texto_resposta = resposta.choices[
            0
        ].message.content

        salvar_memoria(
            pergunta,
            texto_resposta
        )

        salvar_memoria_vetorial(
            pergunta,
            texto_resposta
        )

        return texto_resposta

    except Exception as e:

        logar(f"Erro IA: {e}")

        return "Erro ao falar com Jarbas."
