import sqlite3


DB_NAME = "caixas.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn


def normalizar_nome(nome):
    return nome.strip()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            altura REAL NOT NULL CHECK (altura > 0),
            largura REAL NOT NULL CHECK (largura > 0),
            comprimento REAL NOT NULL CHECK (comprimento > 0)
        )
    """)

    conn.commit()
    conn.close()


def inserir_caixa(nome, altura, largura, comprimento):
    conn = get_connection()
    cursor = conn.cursor()

    nome = normalizar_nome(nome)

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


def buscar_caixas_por_nome(termo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, altura, largura, comprimento
        FROM caixas
        WHERE LOWER(nome) LIKE LOWER(?)
        ORDER BY id DESC
    """, (f"%{termo.strip()}%",))
    caixas = cursor.fetchall()

    conn.close()
    return caixas


def nome_caixa_existe(nome, ignorar_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    nome = normalizar_nome(nome)

    if ignorar_id is None:
        cursor.execute("""
            SELECT 1
            FROM caixas
            WHERE LOWER(nome) = LOWER(?)
            LIMIT 1
        """, (nome,))
    else:
        cursor.execute("""
            SELECT 1
            FROM caixas
            WHERE LOWER(nome) = LOWER(?)
              AND id <> ?
            LIMIT 1
        """, (nome, ignorar_id))

    resultado = cursor.fetchone()
    conn.close()

    return resultado is not None


def atualizar_caixa(caixa_id, nome, altura, largura, comprimento):
    conn = get_connection()
    cursor = conn.cursor()

    nome = normalizar_nome(nome)

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