import psycopg2
import streamlit as st


def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id SERIAL PRIMARY KEY,
            nome TEXT UNIQUE NOT NULL,
            altura DOUBLE PRECISION NOT NULL CHECK (altura > 0),
            largura DOUBLE PRECISION NOT NULL CHECK (largura > 0),
            comprimento DOUBLE PRECISION NOT NULL CHECK (comprimento > 0)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_calculos (
            id SERIAL PRIMARY KEY,
            item_altura DOUBLE PRECISION NOT NULL CHECK (item_altura > 0),
            item_largura DOUBLE PRECISION NOT NULL CHECK (item_largura > 0),
            item_comprimento DOUBLE PRECISION NOT NULL CHECK (item_comprimento > 0),
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            caixa_id INTEGER,
            caixa_nome TEXT NOT NULL,
            capacidade INTEGER NOT NULL CHECK (capacidade >= 0),
            rotacao_altura DOUBLE PRECISION,
            rotacao_largura DOUBLE PRECISION,
            rotacao_comprimento DOUBLE PRECISION,
            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def inserir_caixa(nome, altura, largura, comprimento):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO caixas (nome, altura, largura, comprimento)
        VALUES (%s, %s, %s, %s)
    """, (nome.strip(), altura, largura, comprimento))

    conn.commit()
    cursor.close()
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

    cursor.close()
    conn.close()
    return caixas


def buscar_caixa_por_id(caixa_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, altura, largura, comprimento
        FROM caixas
        WHERE id = %s
    """, (caixa_id,))
    caixa = cursor.fetchone()

    cursor.close()
    conn.close()
    return caixa


def buscar_caixas_por_nome(termo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, altura, largura, comprimento
        FROM caixas
        WHERE LOWER(nome) LIKE LOWER(%s)
        ORDER BY id DESC
    """, (f"%{termo.strip()}%",))
    caixas = cursor.fetchall()

    cursor.close()
    conn.close()
    return caixas


def nome_caixa_existe(nome, ignorar_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if ignorar_id is None:
        cursor.execute("""
            SELECT 1
            FROM caixas
            WHERE LOWER(nome) = LOWER(%s)
            LIMIT 1
        """, (nome.strip(),))
    else:
        cursor.execute("""
            SELECT 1
            FROM caixas
            WHERE LOWER(nome) = LOWER(%s)
              AND id <> %s
            LIMIT 1
        """, (nome.strip(), ignorar_id))

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()
    return resultado is not None


def atualizar_caixa(caixa_id, nome, altura, largura, comprimento):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE caixas
        SET nome = %s, altura = %s, largura = %s, comprimento = %s
        WHERE id = %s
    """, (nome.strip(), altura, largura, comprimento, caixa_id))

    conn.commit()
    cursor.close()
    conn.close()


def excluir_caixa(caixa_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM caixas WHERE id = %s", (caixa_id,))

    conn.commit()
    cursor.close()
    conn.close()


def inserir_historico_calculo(
    item_altura,
    item_largura,
    item_comprimento,
    quantidade,
    caixa_id,
    caixa_nome,
    capacidade,
    rotacao,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO historico_calculos (
            item_altura,
            item_largura,
            item_comprimento,
            quantidade,
            caixa_id,
            caixa_nome,
            capacidade,
            rotacao_altura,
            rotacao_largura,
            rotacao_comprimento
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        item_altura,
        item_largura,
        item_comprimento,
        quantidade,
        caixa_id,
        caixa_nome,
        capacidade,
        rotacao[0] if rotacao else None,
        rotacao[1] if rotacao else None,
        rotacao[2] if rotacao else None,
    ))

    conn.commit()
    cursor.close()
    conn.close()


def listar_historico_calculos(limite=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            item_altura,
            item_largura,
            item_comprimento,
            quantidade,
            caixa_nome,
            capacidade,
            rotacao_altura,
            rotacao_largura,
            rotacao_comprimento,
            criado_em
        FROM historico_calculos
        ORDER BY id DESC
        LIMIT %s
    """, (limite,))
    historico = cursor.fetchall()

    cursor.close()
    conn.close()
    return historico