import sqlite3


DB_NAME = "caixas.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            altura REAL NOT NULL,
            largura REAL NOT NULL,
            comprimento REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def inserir_caixa(nome, altura, largura, comprimento):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO caixas (nome, altura, largura, comprimento)
        VALUES (?, ?, ?, ?)
        """,
        (nome, altura, largura, comprimento),
    )

    conn.commit()
    conn.close()


def listar_caixas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, altura, largura, comprimento
        FROM caixas
        ORDER BY nome
    """)
    caixas = cursor.fetchall()

    conn.close()
    return caixas