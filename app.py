from flask import Flask, render_template, request, jsonify
import jarbas

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    pergunta = request.form.get("mensagem", "")
    imagem = request.files.get("imagem")  # pega a imagem enviada

    if imagem:
        resposta = jarbas.responder(pergunta, imagem)
    else:
        resposta = jarbas.responder(pergunta)

    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
