import sqlite3

DB_NAME = "jarbas.db"

# ===============================
# CONECTAR BANCO
# ===============================

def conectar():
    return sqlite3.connect(DB_NAME)

# ===============================
# CRIAR TABELAS
# ===============================

def criar_tabela():

    conn = conectar()
    cursor = conn.cursor()

    # ===============================
    # USUÁRIOS
    # ===============================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        email TEXT NOT NULL UNIQUE,

        senha TEXT NOT NULL,

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # ===============================
    # HISTÓRICO FUTURO (JARBAS)
    # ===============================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        usuario_id INTEGER,

        pergunta TEXT,

        resposta TEXT,

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (usuario_id)
        REFERENCES users(id)

    )
    """)

    conn.commit()
    conn.close()
