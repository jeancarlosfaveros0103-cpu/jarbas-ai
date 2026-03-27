import sqlite3

DB_NAME = "usuarios.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabela():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
