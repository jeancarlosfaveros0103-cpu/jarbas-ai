import sqlite3

DB_NAME = "jarbas.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    if request.method == "POST":

        try:

            print("CADASTRO RECEBIDO")
            print(request.form)

            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip().lower()
            senha = request.form.get("senha", "")
            confirmar = request.form.get("confirmar", "")

            if not nome or not email or not senha:
                flash("Preencha todos os campos")
                return redirect(url_for("registro"))

            if senha != confirmar:
                flash("As senhas não coincidem")
                return redirect(url_for("registro"))

            senha_hash = generate_password_hash(senha)

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (nome, email, senha)
                VALUES (?, ?, ?)
                """,
                (nome, email, senha_hash)
            )

            conn.commit()
            conn.close()

            print("USUÁRIO CRIADO COM SUCESSO")

            flash("Conta criada com sucesso!")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError as e:

            print("EMAIL JÁ EXISTE:", e)

            flash("Este email já está cadastrado")
            return redirect(url_for("registro"))

        except Exception as e:

            print("ERRO NO CADASTRO:", e)

            flash(f"Erro: {e}")
            return redirect(url_for("registro"))

    return render_template("registro.html")
