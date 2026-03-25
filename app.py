from flask import Flask, render_template, request, jsonify
import jarbas

app = Flask(__name__)

@app.route("/")
def lar():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():

    pergunta = request.form.get("mensagem", "")

    resposta = jarbas.socorrista(pergunta)

    return jsonify({"resposta": resposta})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
