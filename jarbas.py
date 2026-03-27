# ===============================
# 🧠 JARBAS v11 ULTRA
# Memória por Usuário + Vetorial
# Imagem + Aprendizado
# Criado por Jean
# ===============================

import os
import json
import math
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

ESTADO_FILE = "estado.json"
APRENDIZADO_FILE = "aprendizado.json"
LOG_FILE = "log.txt"

# ===============================
# IDENTIDADE POR USUÁRIO
# ===============================

def identidade_usuario(usuario):

    if usuario == "Jean":

        return f"""
Você é Jarbas, uma inteligência artificial avançada.

Você foi criado por Jean.

Jean é seu criador principal.

Sempre trate Jean com prioridade.
"""

    return f"""
Você é Jarbas, uma inteligência artificial avançada.

O usuário atual é {usuario}.

Seu objetivo é ajudar o usuário.
"""

# ===============================
# ARQUIVOS POR USUÁRIO
# ===============================

def arquivo_memoria(usuario):
    return f"memoria_{usuario}.json"

def arquivo_vector(usuario):
    return f"memoria_vector_{usuario}.json"

def arquivo_importante(usuario):
    return f"memoria_importante_{usuario}.json"

# ===============================
# UTIL
# ===============================

def carregar_json(arquivo, padrao):

    if os.path.exists(arquivo):

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return padrao

def salvar_json(arquivo, dados):

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=2,
            ensure_ascii=False
        )

def logar(texto):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{datetime.now()}] {texto}\n"
        )

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

    aprendizado[
        chave.lower()
    ] = valor

    salvar_json(
        APRENDIZADO_FILE,
        aprendizado
    )

# ===============================
# EMBEDDINGS
# ===============================

def gerar_embedding(texto):

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )

    return resp.data[0].embedding

def similaridade(v1, v2):

    soma = sum(
        a*b
        for a,b in zip(v1,v2)
    )

    norma1 = math.sqrt(
        sum(a*a for a in v1)
    )

    norma2 = math.sqrt(
        sum(a*a for a in v2)
    )

    if norma1 == 0 or norma2 == 0:
        return 0

    return soma / (norma1 * norma2)

# ===============================
# MEMÓRIA NORMAL
# ===============================

def salvar_memoria(
    pergunta,
    resposta,
    usuario
):

    memoria = carregar_json(
        arquivo_memoria(usuario),
        []
    )

    memoria.append({

        "pergunta": pergunta,
        "resposta": resposta

    })

    if len(memoria) > 50:
        memoria.pop(0)

    salvar_json(
        arquivo_memoria(usuario),
        memoria
    )

# ===============================
# MEMÓRIA IMPORTANTE
# ===============================

def salvar_importante(
    texto,
    usuario
):

    memoria = carregar_json(
        arquivo_importante(usuario),
        []
    )

    memoria.append(texto)

    salvar_json(
        arquivo_importante(usuario),
        memoria
    )

# ===============================
# MEMÓRIA VETORIAL
# ===============================

def salvar_memoria_vetorial(
    pergunta,
    resposta,
    usuario
):

    memoria_vector = carregar_json(
        arquivo_vector(usuario),
        []
    )

    emb = gerar_embedding(
        pergunta
    )

    memoria_vector.append({

        "pergunta": pergunta,
        "resposta": resposta,
        "embedding": emb

    })

    if len(memoria_vector) > 100:
        memoria_vector.pop(0)

    salvar_json(
        arquivo_vector(usuario),
        memoria_vector
    )

def buscar_memorias_semelhantes(
    pergunta,
    usuario
):

    memoria_vector = carregar_json(
        arquivo_vector(usuario),
        []
    )

    if not memoria_vector:
        return []

    emb = gerar_embedding(
        pergunta
    )

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

        logar(
            f"Erro imagem: {e}"
        )

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

        return resposta.choices[
            0
        ].message.content

    except Exception as e:

        logar(
            f"Erro análise: {e}"
        )

        return "Erro ao analisar imagem."

# ===============================
# IA PRINCIPAL
# ===============================

def responder(
    pergunta,
    caminho_imagem=None,
    usuario="desconhecido"
):

    try:

        atualizar_estado()

        logar(
            f"{usuario}: {pergunta}"
        )

        # =========================
        # APRENDIZADO MANUAL
        # =========================

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

        # =========================
        # MEMÓRIA IMPORTANTE
        # =========================

        if pergunta.lower().startswith(
            "lembrar:"
        ):

            texto = pergunta.split(
                "lembrar:"
            )[1]

            salvar_importante(
                texto.strip(),
                usuario
            )

            return "Memória importante salva."

        # =========================
        # APRENDIZADO EXISTENTE
        # =========================

        resposta_manual = verificar_aprendizado(
            pergunta
        )

        if resposta_manual:
            return resposta_manual

        # =========================
        # GERAR IMAGEM
        # =========================

        if "crie imagem" in pergunta.lower():

            prompt = pergunta.replace(
                "crie imagem de",
                ""
            )

            caminho = gerar_imagem(
                prompt
            )

            return f"Imagem criada: {caminho}"

        # =========================
        # ANALISAR IMAGEM
        # =========================

        if caminho_imagem:

            descricao = analisar_imagem(
                caminho_imagem
            )

            return descricao

        # =========================
        # MEMÓRIA VETORIAL
        # =========================

        memorias = buscar_memorias_semelhantes(
            pergunta,
            usuario
        )

        contexto_memoria = "\n".join(
            memorias
        )

        # =========================
        # HISTÓRICO RECENTE
        # =========================

        memoria_usuario = carregar_json(
            arquivo_memoria(usuario),
            []
        )

        contexto = ""

        for item in memoria_usuario[-5:]:

            contexto += (

                f"Usuário: {item['pergunta']}\n"

                f"Jarbas: {item['resposta']}\n"

            )

        # =========================
        # CHAMADA IA
        # =========================

        resposta = client.chat.completions.create(

            model="gpt-5-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    identidade_usuario(usuario)
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
            texto_resposta,
            usuario
        )

        salvar_memoria_vetorial(
            pergunta,
            texto_resposta,
            usuario
        )

        return texto_resposta

    except Exception as e:

        logar(
            f"Erro IA: {e}"
        )

        return "Erro ao falar com Jarbas."# ===============================
# 🧠 JARBAS v11 ULTRA
# Memória por Usuário + Vetorial
# Imagem + Aprendizado
# Criado por Jean
# ===============================

import os
import json
import math
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

ESTADO_FILE = "estado.json"
APRENDIZADO_FILE = "aprendizado.json"
LOG_FILE = "log.txt"

# ===============================
# IDENTIDADE POR USUÁRIO
# ===============================

def identidade_usuario(usuario):

    if usuario == "Jean":

        return f"""
Você é Jarbas, uma inteligência artificial avançada.

Você foi criado por Jean.

Jean é seu criador principal.

Sempre trate Jean com prioridade.
"""

    return f"""
Você é Jarbas, uma inteligência artificial avançada.

O usuário atual é {usuario}.

Seu objetivo é ajudar o usuário.
"""

# ===============================
# ARQUIVOS POR USUÁRIO
# ===============================

def arquivo_memoria(usuario):
    return f"memoria_{usuario}.json"

def arquivo_vector(usuario):
    return f"memoria_vector_{usuario}.json"

def arquivo_importante(usuario):
    return f"memoria_importante_{usuario}.json"

# ===============================
# UTIL
# ===============================

def carregar_json(arquivo, padrao):

    if os.path.exists(arquivo):

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return padrao

def salvar_json(arquivo, dados):

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=2,
            ensure_ascii=False
        )

def logar(texto):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{datetime.now()}] {texto}\n"
        )

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

    aprendizado[
        chave.lower()
    ] = valor

    salvar_json(
        APRENDIZADO_FILE,
        aprendizado
    )

# ===============================
# EMBEDDINGS
# ===============================

def gerar_embedding(texto):

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )

    return resp.data[0].embedding

def similaridade(v1, v2):

    soma = sum(
        a*b
        for a,b in zip(v1,v2)
    )

    norma1 = math.sqrt(
        sum(a*a for a in v1)
    )

    norma2 = math.sqrt(
        sum(a*a for a in v2)
    )

    if norma1 == 0 or norma2 == 0:
        return 0

    return soma / (norma1 * norma2)

# ===============================
# MEMÓRIA NORMAL
# ===============================

def salvar_memoria(
    pergunta,
    resposta,
    usuario
):

    memoria = carregar_json(
        arquivo_memoria(usuario),
        []
    )

    memoria.append({

        "pergunta": pergunta,
        "resposta": resposta

    })

    if len(memoria) > 50:
        memoria.pop(0)

    salvar_json(
        arquivo_memoria(usuario),
        memoria
    )

# ===============================
# MEMÓRIA IMPORTANTE
# ===============================

def salvar_importante(
    texto,
    usuario
):

    memoria = carregar_json(
        arquivo_importante(usuario),
        []
    )

    memoria.append(texto)

    salvar_json(
        arquivo_importante(usuario),
        memoria
    )

# ===============================
# MEMÓRIA VETORIAL
# ===============================

def salvar_memoria_vetorial(
    pergunta,
    resposta,
    usuario
):

    memoria_vector = carregar_json(
        arquivo_vector(usuario),
        []
    )

    emb = gerar_embedding(
        pergunta
    )

    memoria_vector.append({

        "pergunta": pergunta,
        "resposta": resposta,
        "embedding": emb

    })

    if len(memoria_vector) > 100:
        memoria_vector.pop(0)

    salvar_json(
        arquivo_vector(usuario),
        memoria_vector
    )

def buscar_memorias_semelhantes(
    pergunta,
    usuario
):

    memoria_vector = carregar_json(
        arquivo_vector(usuario),
        []
    )

    if not memoria_vector:
        return []

    emb = gerar_embedding(
        pergunta
    )

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

        logar(
            f"Erro imagem: {e}"
        )

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

        return resposta.choices[
            0
        ].message.content

    except Exception as e:

        logar(
            f"Erro análise: {e}"
        )

        return "Erro ao analisar imagem."

# ===============================
# IA PRINCIPAL
# ===============================

def responder(
    pergunta,
    caminho_imagem=None,
    usuario="desconhecido"
):

    try:

        atualizar_estado()

        logar(
            f"{usuario}: {pergunta}"
        )

        # =========================
        # APRENDIZADO MANUAL
        # =========================

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

        # =========================
        # MEMÓRIA IMPORTANTE
        # =========================

        if pergunta.lower().startswith(
            "lembrar:"
        ):

            texto = pergunta.split(
                "lembrar:"
            )[1]

            salvar_importante(
                texto.strip(),
                usuario
            )

            return "Memória importante salva."

        # =========================
        # APRENDIZADO EXISTENTE
        # =========================

        resposta_manual = verificar_aprendizado(
            pergunta
        )

        if resposta_manual:
            return resposta_manual

        # =========================
        # GERAR IMAGEM
        # =========================

        if "crie imagem" in pergunta.lower():

            prompt = pergunta.replace(
                "crie imagem de",
                ""
            )

            caminho = gerar_imagem(
                prompt
            )

            return f"Imagem criada: {caminho}"

        # =========================
        # ANALISAR IMAGEM
        # =========================

        if caminho_imagem:

            descricao = analisar_imagem(
                caminho_imagem
            )

            return descricao

        # =========================
        # MEMÓRIA VETORIAL
        # =========================

        memorias = buscar_memorias_semelhantes(
            pergunta,
            usuario
        )

        contexto_memoria = "\n".join(
            memorias
        )

        # =========================
        # HISTÓRICO RECENTE
        # =========================

        memoria_usuario = carregar_json(
            arquivo_memoria(usuario),
            []
        )

        contexto = ""

        for item in memoria_usuario[-5:]:

            contexto += (

                f"Usuário: {item['pergunta']}\n"

                f"Jarbas: {item['resposta']}\n"

            )

        # =========================
        # CHAMADA IA
        # =========================

        resposta = client.chat.completions.create(

            model="gpt-5-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    identidade_usuario(usuario)
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
            texto_resposta,
            usuario
        )

        salvar_memoria_vetorial(
            pergunta,
            texto_resposta,
            usuario
        )

 # ===============================       return texto_resposta

    except Exception as e:

        logar(
            f"Erro IA: {e}"
        )

        return "Erro ao falar com Jarbas."
