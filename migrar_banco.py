import sqlite3


DB_NAME = "caixas.db"


def migrar():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            altura REAL NOT NULL CHECK (altura > 0),
            largura REAL NOT NULL CHECK (largura > 0),
            comprimento REAL NOT NULL CHECK (comprimento > 0)
        )
    """)

    cursor.execute("""
        SELECT id, TRIM(nome), altura, largura, comprimento
        FROM caixas
        ORDER BY id
    """)
    registros = cursor.fetchall()

    nomes_usados = set()

    for registro in registros:
        caixa_id, nome, altura, largura, comprimento = registro

        nome_normalizado = nome.strip().lower()

        if not nome.strip():
            print(f"Ignorado ID {caixa_id}: nome vazio")
            continue

        if altura <= 0 or largura <= 0 or comprimento <= 0:
            print(f"Ignorado ID {caixa_id}: dimensão inválida")
            continue

        if nome_normalizado in nomes_usados:
            print(f"Ignorado ID {caixa_id}: nome duplicado -> {nome}")
            continue

        cursor.execute("""
            INSERT INTO caixas_new (nome, altura, largura, comprimento)
            VALUES (?, ?, ?, ?)
        """, (nome.strip(), altura, largura, comprimento))

        nomes_usados.add(nome_normalizado)

    cursor.execute("DROP TABLE caixas")
    cursor.execute("ALTER TABLE caixas_new RENAME TO caixas")

    conn.commit()
    conn.close()

    print("Migração concluída com sucesso.")


if __name__ == "__main__":
    migrar()