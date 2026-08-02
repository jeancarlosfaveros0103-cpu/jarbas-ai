from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash
)

import jarbas
import os
import sqlite3

from datetime import datetime
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import criar_tabela, conectar

# ===============================
# CONFIG
# ===============================

app = Flask(
    __name__,
    static_folder="static"
)

app.secret_key = "jarbas_secret_ultra"

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

# Criar banco
criar_tabela()

# ===============================
# HOME
# ===============================

@app.route("/")
def home():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        nome=session.get("usuario_nome")
    )

# ===============================
# LOGIN
# ===============================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, senha FROM usuarios WHERE email = ?",
            (email,)
        )

        usuario = cursor.fetchone()

        conn.close()

        print("USUARIO DO BANCO:", usuario)

        if usuario:

            user_id = usuario[0]
            nome = usuario[1]
            senha_hash = usuario[2]

            print("VERIFICANDO SENHA...")

            if check_password_hash(
                senha_hash,
                senha
            ):

                print("LOGIN OK:", nome)

                session["usuario_id"] = user_id
                session["usuario_nome"] = nome

                return redirect(url_for("home"))

            else:

                print("SENHA ERRADA")

        else:

            print("USUARIO NÃO ENCONTRADO")

        flash("Email ou senha incorretos")

    return render_template("login.html")

# ===============================
# REGISTRO
# ===============================

@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")

        if senha != confirmar:
            flash("Senhas não coincidem")
            return redirect(url_for("registro"))

        senha_hash = generate_password_hash(senha)

        try:

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO usuarios
            (nome, email, senha)
            VALUES (?, ?, ?)
            """, (
                nome,
                email,
                senha_hash
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("Email já cadastrado")

    return render_template("registro.html")

# ===============================
# LOGOUT
# ===============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ===============================
# PERGUNTAR AO JARBAS
# ===============================

@app.route("/perguntar", methods=["POST"])
def perguntar():

    if "usuario_id" not in session:
        return jsonify({
            "resposta": "Usuário não autenticado."
        })

    pergunta = request.form.get(
        "mensagem",
        ""
    )

    arquivo = request.files.get(
        "imagem"
    )

    caminho_imagem = None

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

    resposta = jarbas.responder(
        pergunta,
        caminho_imagem,
        usuario=session.get("usuario_nome")
    )

    return jsonify({
        "resposta": resposta
    })

# ===============================
# RUN
# ===============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
