import sqlite3

DB_NAME = "jarbas.db"

# ===============================
# CONECTAR AO BANCO
# ===============================

def conectar():
    return sqlite3.connect(DB_NAME)

# ===============================
# CRIAR TABELAS
# ===============================

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

# ===============================
# ADICIONAR USUÁRIO
# ===============================

def adicionar_usuario(nome, email, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios
        (nome, email, senha)
        VALUES (?, ?, ?)
        """,
        (nome, email, senha)
    )

    conn.commit()
    conn.close()

# ===============================
# BUSCAR USUÁRIO POR EMAIL
# ===============================

def buscar_usuario(email):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        (email,)
    )

    usuario = cursor.fetchone()

    conn.close()

    return usuario

# ===============================
# LISTAR USUÁRIOS
# ===============================

def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios")

    usuarios = cursor.fetchall()

    conn.close()

    return usuarios

# ===============================
# DELETAR USUÁRIO
# ===============================

def deletar_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM usuarios WHERE id = ?",
        (usuario_id,)
    )

    conn.commit()
    conn.close()
