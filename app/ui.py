import sqlite3
import streamlit as st
from app.database import (
    init_db,
    inserir_caixa,
    listar_caixas,
    buscar_caixa_por_id,
    buscar_caixas_por_nome,
    atualizar_caixa,
    excluir_caixa,
    nome_caixa_existe,
)
from app.services import encontrar_melhor_caixa


def tela_consultar_caixas():
    st.header("📋 Consultar caixas cadastradas")

    termo_busca = st.text_input("Buscar caixa por nome")

    if termo_busca.strip():
        caixas = buscar_caixas_por_nome(termo_busca.strip())
    else:
        caixas = listar_caixas()

    if not caixas:
        st.warning("Nenhuma caixa encontrada.")
        return

    st.subheader("Lista de caixas")

    caixa_em_edicao = st.session_state.get("caixa_em_edicao")
    caixa_em_exclusao = st.session_state.get("caixa_em_exclusao")

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
                    st.session_state.caixa_em_exclusao = None
                    st.rerun()

                if st.button("Excluir", key=f"pedir_exclusao_{caixa_id}"):
                    st.session_state.caixa_em_exclusao = caixa_id
                    st.session_state.caixa_em_edicao = None
                    st.rerun()

            if caixa_em_exclusao == caixa_id:
                st.error(
                    f"Confirma a exclusão da caixa '{nome}'? Essa ação não pode ser desfeita."
                )
                col_confirmar, col_cancelar = st.columns(2)

                if col_confirmar.button("✅ Confirmar exclusão", key=f"confirmar_exclusao_{caixa_id}"):
                    excluir_caixa(caixa_id)
                    st.session_state.caixa_em_exclusao = None
                    st.success(f"Caixa '{nome}' excluída com sucesso.")
                    st.rerun()

                if col_cancelar.button("❌ Cancelar", key=f"cancelar_exclusao_{caixa_id}"):
                    st.session_state.caixa_em_exclusao = None
                    st.rerun()

            if caixa_em_edicao == caixa_id:
                st.divider()
                st.subheader("✏️ Editar caixa")

                with st.form(f"form_editar_caixa_{caixa_id}"):
                    novo_nome = st.text_input("Nome da caixa", value=nome)
                    nova_altura = st.number_input(
                        "Altura (cm)",
                        min_value=0.01,
                        value=float(altura),
                        format="%.2f",
                        key=f"altura_edit_{caixa_id}",
                    )
                    nova_largura = st.number_input(
                        "Largura (cm)",
                        min_value=0.01,
                        value=float(largura),
                        format="%.2f",
                        key=f"largura_edit_{caixa_id}",
                    )
                    novo_comprimento = st.number_input(
                        "Comprimento (cm)",
                        min_value=0.01,
                        value=float(comprimento),
                        format="%.2f",
                        key=f"comprimento_edit_{caixa_id}",
                    )

                    col_salvar, col_cancelar = st.columns(2)
                    salvar = col_salvar.form_submit_button("Salvar alterações")
                    cancelar = col_cancelar.form_submit_button("Cancelar")

                    if salvar:
                        nome_limpo = novo_nome.strip()

                        if not nome_limpo:
                            st.error("Informe o nome da caixa.")
                        elif nome_caixa_existe(nome_limpo, ignorar_id=caixa_id):
                            st.error("Já existe uma caixa cadastrada com esse nome.")
                        else:
                            atualizar_caixa(
                                caixa_id=caixa_id,
                                nome=nome_limpo,
                                altura=nova_altura,
                                largura=nova_largura,
                                comprimento=novo_comprimento,
                            )
                            st.session_state.caixa_em_edicao = None
                            st.success("Caixa atualizada com sucesso.")
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
            nome_limpo = nome.strip()

            if not nome_limpo:
                st.error("Informe o nome da caixa.")
            elif nome_caixa_existe(nome_limpo):
                st.error("Já existe uma caixa cadastrada com esse nome.")
            else:
                inserir_caixa(
                    nome=nome_limpo,
                    altura=altura,
                    largura=largura,
                    comprimento=comprimento,
                )
                st.success(f"Caixa '{nome_limpo}' cadastrada com sucesso.")
        


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

    if "caixa_em_exclusao" not in st.session_state:
        st.session_state.caixa_em_exclusao = None

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