from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")
    resposta = "Jarbas está vivo 😎"  # depois liga com a IA
    return jsonify({"reply": resposta})

if __name__ == "__main__":
    app.run()
