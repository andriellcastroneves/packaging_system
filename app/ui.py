import streamlit as st
from app.database import init_db, inserir_caixa, listar_caixas
from app.services import encontrar_melhor_caixa


def tela_consultar_caixas():
    st.header("📋 Consultar caixas cadastradas")

    caixas = listar_caixas()

    if not caixas:
        st.warning("Nenhuma caixa cadastrada ainda.")
        return

    for caixa in caixas:
        st.write(
            f"**{caixa[1]}** — "
            f"Altura: {caixa[2]} cm | "
            f"Largura: {caixa[3]} cm | "
            f"Comprimento: {caixa[4]} cm"
        )


def tela_cadastrar_caixa():
    st.header("📦 Cadastrar nova caixa")

    with st.form("form_cadastro_caixa"):
        nome = st.text_input("Nome da caixa")
        altura = st.number_input("Altura (cm)", min_value=0.0, format="%.2f")
        largura = st.number_input("Largura (cm)", min_value=0.0, format="%.2f")
        comprimento = st.number_input("Comprimento (cm)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Cadastrar caixa")

        if submitted:
            if not nome.strip():
                st.error("Informe o nome da caixa.")
            elif altura <= 0 or largura <= 0 or comprimento <= 0:
                st.error("As dimensões devem ser maiores que zero.")
            else:
                inserir_caixa(
                    nome=nome.strip(),
                    altura=altura,
                    largura=largura,
                    comprimento=comprimento,
                )
                st.success(f"Caixa '{nome}' cadastrada com sucesso.")


def tela_calcular_melhor_caixa():
    st.header("🧠 Calcular melhor caixa")

    caixas = listar_caixas()

    if not caixas:
        st.warning("Cadastre pelo menos uma caixa antes de fazer o cálculo.")
        return

    with st.form("form_calculo"):
        altura_item = st.number_input("Altura do item (cm)", min_value=0.0, format="%.2f")
        largura_item = st.number_input("Largura do item (cm)", min_value=0.0, format="%.2f")
        comprimento_item = st.number_input("Comprimento do item (cm)", min_value=0.0, format="%.2f")
        quantidade = st.number_input("Quantidade de itens", min_value=1, step=1)

        submitted = st.form_submit_button("Calcular melhor caixa")

        if submitted:
            if altura_item <= 0 or largura_item <= 0 or comprimento_item <= 0:
                st.error("As dimensões do item devem ser maiores que zero.")
                return

            item_dim = (altura_item, largura_item, comprimento_item)

            melhor_caixa, capacidade, rotacao = encontrar_melhor_caixa(
                item_dim=item_dim,
                quantidade=quantidade,
                caixas=caixas,
            )

            if melhor_caixa:
                st.success(f"Melhor caixa encontrada: {melhor_caixa[1]}")
                st.write(f"Capacidade máxima nesta caixa: **{capacidade} itens**")

                if rotacao:
                    st.write(
                        "Melhor rotação do item: "
                        f"**{rotacao[0]} x {rotacao[1]} x {rotacao[2]} cm**"
                    )

                st.write(
                    "Dimensões da caixa: "
                    f"**{melhor_caixa[2]} x {melhor_caixa[3]} x {melhor_caixa[4]} cm**"
                )
            else:
                st.error("Nenhuma caixa cadastrada comporta essa quantidade de itens.")


def run_app():
    st.set_page_config(page_title="Sistema de Embalagem", layout="centered")

    init_db()

    st.title("📦 Sistema Inteligente de Embalagem")
    st.info("Todas as medidas devem ser informadas em centímetros (cm).")

    opcao = st.sidebar.radio(
        "Escolha uma opção",
        [
            "Consultar caixas cadastradas",
            "Cadastrar nova caixa",
            "Calcular melhor caixa",
        ],
    )

    if opcao == "Consultar caixas cadastradas":
        tela_consultar_caixas()

    elif opcao == "Cadastrar nova caixa":
        tela_cadastrar_caixa()

    elif opcao == "Calcular melhor caixa":
        tela_calcular_melhor_caixa()