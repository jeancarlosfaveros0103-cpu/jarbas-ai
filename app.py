from flask import Flask, render_template, request, jsonify
import jarbas
import os
from datetime import datetime

# IMPORTANTE: definir static_folder
app = Flask(
    __name__,
    static_folder="static"
)

UPLOAD_FOLDER = "uploads"

# Criar pastas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

@app.route("/")
def lar():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():

    pergunta = request.form.get(
        "mensagem",
        ""
    )

    arquivo = request.files.get(
        "imagem"
    )

    caminho_imagem = None

    # ===============================
    # SE VEIO IMAGEM
    # ===============================

    if arquivo:

        nome = (
            "upload_" +
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            ) +
            ".png"
        )

        caminho_imagem = os.path.join(
            UPLOAD_FOLDER,
            nome
        )

        arquivo.save(
            caminho_imagem
        )

    # ===============================
    # CHAMAR JARBAS
    # ===============================

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
