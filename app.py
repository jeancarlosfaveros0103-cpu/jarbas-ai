from flask import Flask, render_template, request, jsonify
import jarbas
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

# Criar pasta uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def lar():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():

    pergunta = request.form.get("mensagem", "")

    arquivo = request.files.get("imagem")

    caminho_imagem = None

    # Se enviar imagem
    if arquivo:

        nome = (
            "upload_" +
            datetime.now().strftime("%Y%m%d_%H%M%S") +
            ".png"
        )

        caminho_imagem = os.path.join(
            UPLOAD_FOLDER,
            nome
        )

        arquivo.save(caminho_imagem)

    # CHAMADA CORRETA
    resposta = jarbas.responder(
        pergunta,
        caminho_imagem
    )

    return jsonify({
        "resposta": resposta
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
