import streamlit as st
from app.database import (
    init_db,
    inserir_caixa,
    listar_caixas,
    buscar_caixa_por_id,
    atualizar_caixa,
    excluir_caixa,
)
from app.services import encontrar_melhor_caixa


def tela_consultar_caixas():
    st.header("📋 Consultar caixas cadastradas")

    caixas = listar_caixas()

    if not caixas:
        st.warning("Nenhuma caixa cadastrada ainda.")
        return

    st.subheader("Lista de caixas")

    for caixa in caixas:
        caixa_id, nome, altura, largura, comprimento = caixa

        with st.container(border=True):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.write(f"**ID:** {caixa_id}")
                st.write(f"**Nome:** {nome}")
                st.write(f"**Altura:** {altura} cm")
                st.write(f"**Largura:** {largura} cm")
                st.write(f"**Comprimento:** {comprimento} cm")

            with col2:
                if st.button("Editar", key=f"editar_{caixa_id}"):
                    st.session_state.caixa_em_edicao = caixa_id

                if st.button("Excluir", key=f"excluir_{caixa_id}"):
                    excluir_caixa(caixa_id)
                    st.success(f"Caixa '{nome}' excluída com sucesso.")
                    st.rerun()

    caixa_em_edicao = st.session_state.get("caixa_em_edicao")

    if caixa_em_edicao:
        caixa = buscar_caixa_por_id(caixa_em_edicao)

        if caixa:
            st.divider()
            st.subheader("✏️ Editar caixa")

            with st.form("form_editar_caixa"):
                novo_nome = st.text_input("Nome da caixa", value=caixa[1])
                nova_altura = st.number_input("Altura (cm)", min_value=0.01, value=float(caixa[2]), format="%.2f")
                nova_largura = st.number_input("Largura (cm)", min_value=0.01, value=float(caixa[3]), format="%.2f")
                novo_comprimento = st.number_input("Comprimento (cm)", min_value=0.01, value=float(caixa[4]), format="%.2f")

                col_salvar, col_cancelar = st.columns(2)

                salvar = col_salvar.form_submit_button("Salvar alterações")
                cancelar = col_cancelar.form_submit_button("Cancelar")

                if salvar:
                    if not novo_nome.strip():
                        st.error("Informe o nome da caixa.")
                    else:
                        atualizar_caixa(
                            caixa_id=caixa_em_edicao,
                            nome=novo_nome.strip(),
                            altura=nova_altura,
                            largura=nova_largura,
                            comprimento=novo_comprimento,
                        )
                        st.success("Caixa atualizada com sucesso.")
                        st.session_state.caixa_em_edicao = None
                        st.rerun()

                if cancelar:
                    st.session_state.caixa_em_edicao = None
                    st.rerun()


def tela_cadastrar_caixa():
    st.header("📦 Cadastrar nova caixa")

    with st.form("form_cadastro_caixa"):
        nome = st.text_input("Nome da caixa")
        altura = st.number_input("Altura (cm)", min_value=0.01, format="%.2f")
        largura = st.number_input("Largura (cm)", min_value=0.01, format="%.2f")
        comprimento = st.number_input("Comprimento (cm)", min_value=0.01, format="%.2f")

        submitted = st.form_submit_button("Cadastrar caixa")

        if submitted:
            if not nome.strip():
                st.error("Informe o nome da caixa.")
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
        altura_item = st.number_input("Altura do item (cm)", min_value=0.01, format="%.2f")
        largura_item = st.number_input("Largura do item (cm)", min_value=0.01, format="%.2f")
        comprimento_item = st.number_input("Comprimento do item (cm)", min_value=0.01, format="%.2f")
        quantidade = st.number_input("Quantidade de itens", min_value=1, step=1)

        submitted = st.form_submit_button("Calcular melhor caixa")

        if submitted:
            item_dim = (altura_item, largura_item, comprimento_item)

            melhor_caixa, capacidade, rotacao = encontrar_melhor_caixa(
                item_dim=item_dim,
                quantidade=quantidade,
                caixas=caixas,
            )

            if melhor_caixa:
                st.success(f"Melhor caixa encontrada: {melhor_caixa[1]}")
                st.write(f"**Capacidade máxima nesta caixa:** {capacidade} itens")
                st.write(
                    f"**Dimensões da caixa:** "
                    f"{melhor_caixa[2]} x {melhor_caixa[3]} x {melhor_caixa[4]} cm"
                )

                if rotacao:
                    st.write(
                        f"**Melhor rotação do item:** "
                        f"{rotacao[0]} x {rotacao[1]} x {rotacao[2]} cm"
                    )
            else:
                st.error("Nenhuma caixa cadastrada comporta essa quantidade de itens.")


def run_app():
    st.set_page_config(page_title="Sistema de Embalagem", layout="centered")

    init_db()

    if "caixa_em_edicao" not in st.session_state:
        st.session_state.caixa_em_edicao = None

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