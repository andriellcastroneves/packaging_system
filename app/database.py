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
        ORDER BY id DESC
    """)
    caixas = cursor.fetchall()

    conn.close()
    return caixas


def buscar_caixa_por_id(caixa_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, altura, largura, comprimento
        FROM caixas
        WHERE id = ?
    """, (caixa_id,))
    caixa = cursor.fetchone()

    conn.close()
    return caixa


def atualizar_caixa(caixa_id, nome, altura, largura, comprimento):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE caixas
        SET nome = ?, altura = ?, largura = ?, comprimento = ?
        WHERE id = ?
    """, (nome, altura, largura, comprimento, caixa_id))

    conn.commit()
    conn.close()


def excluir_caixa(caixa_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM caixas WHERE id = ?", (caixa_id,))

    conn.commit()
    conn.close()