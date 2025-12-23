from flask import Flask, render_template, request, jsonify
import jarbas

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    data = request.json
    pergunta = data.get("mensagem", "")

    resposta = jarbas.responder(pergunta)
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
