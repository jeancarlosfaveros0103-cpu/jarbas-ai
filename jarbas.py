# ===============================
# 🧠 JARBAS v12 COMPLETO
# Memória Inteligente
# Painel Admin
# Memória Vetorial
# Imagens
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

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

PASTA_STATIC = "static"
PASTA_UPLOAD = "uploads"

os.makedirs(PASTA_STATIC, exist_ok=True)
os.makedirs(PASTA_UPLOAD, exist_ok=True)

ESTADO_FILE = "estado.json"
LOG_FILE = "log.txt"
ADMIN_SENHA = "311514"

estado_admin = {}

# ===============================
# UTIL NOME
# ===============================

def primeiro_nome(nome):

    if not nome:
        return "Usuário"

    return nome.split()[0]

# ===============================
# MEMÓRIA NOME
# ===============================

def aprender_nome(pergunta, usuario):

    pergunta_lower = pergunta.lower()

    if "meu nome é" in pergunta_lower:

        nome = pergunta_lower.replace(
            "meu nome é",
            ""
        ).strip().title()

        nomes = carregar_json(
            "nomes.json",
            {}
        )

        nomes[usuario] = nome

        salvar_json(
            "nomes.json",
            nomes
        )

        return f"Entendi! Vou lembrar que seu nome é {nome}."

    return None


def obter_nome(usuario):

    nomes = carregar_json(
        "nomes.json",
        {}
    )

    return nomes.get(
        usuario,
        primeiro_nome(usuario)
    )

# ===============================
# IDENTIDADE
# ===============================

def identidade_usuario(usuario):

    nome_curto = obter_nome(usuario)

    if nome_curto.lower() == "jean":

        return f"""
Você é Jarbas.

Você foi criado por Jean.

Jean é seu criador principal.

Sempre trate Jean com prioridade.

Nunca diga que foi criado pela OpenAI.
"""

    return f"""
Você é Jarbas, uma inteligência artificial criada por Jean.

O nome do usuário é {nome_curto}.

Sempre chame o usuário pelo primeiro nome.

Nunca diga que foi criado pela OpenAI.

Seu objetivo é ajudar o usuário.
"""

# ===============================
# ARQUIVOS
# ===============================

def arquivo_memoria(usuario):
    return f"memoria_{usuario}.json"

def arquivo_vector(usuario):
    return f"memoria_vector_{usuario}.json"

# ===============================
# JSON
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
# ESTADO
# ===============================

estado = carregar_json(
    ESTADO_FILE,
    {
        "interacoes": 0,
        "energia": 100
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
# PAINEL ADMIN
# ===============================

def verificar_admin(pergunta, usuario):

    pergunta_lower = pergunta.lower()

    if pergunta_lower == "painel admin01":

        estado_admin[usuario] = "aguardando"

        return "Digite a senha do admin:"

    if estado_admin.get(usuario) == "aguardando":

        if pergunta == ADMIN_SENHA:

            estado_admin[usuario] = "logado"

            return mostrar_painel_admin()

        else:

            estado_admin.pop(usuario, None)

            return "Senha incorreta."

    return None


def mostrar_painel_admin():

    arquivos = os.listdir()

    usuarios = []

    for arq in arquivos:

        if arq.startswith("memoria_"):

            nome = arq.replace(
                "memoria_",
                ""
            ).replace(
                ".json",
                ""
            )

            usuarios.append(nome)

    if not usuarios:

        return "Nenhum usuário encontrado."

    texto = "📊 USUÁRIOS CADASTRADOS:\n\n"

    for u in usuarios:

        texto += f"- {u}\n"

    return texto

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

        return f"Imagem criada: /static/{nome}"

    except Exception as e:

        logar(
            f"Erro imagem: {e}"
        )

        return "Erro ao gerar imagem."

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

        # ADMIN

        resposta_admin = verificar_admin(
            pergunta,
            usuario
        )

        if resposta_admin:
            return resposta_admin

        # MEMÓRIA NOME

        resposta_nome = aprender_nome(
            pergunta,
            usuario
        )

        if resposta_nome:
            return resposta_nome

        # GERAR IMAGEM

        if "crie imagem" in pergunta.lower():

            prompt = pergunta.replace(
                "crie imagem de",
                ""
            )

            return gerar_imagem(prompt)

        # MEMÓRIA

        memorias = buscar_memorias_semelhantes(
            pergunta,
            usuario
        )

        contexto_memoria = "\n".join(
            memorias
        )

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

        resposta = client.chat.completions.create(

            model="gpt-4.1-mini",

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

        return "Erro ao falar com Jarbas."
