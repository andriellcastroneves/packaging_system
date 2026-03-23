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
    inserir_produto,
    listar_produtos,
    buscar_produto_por_id,
    buscar_produtos_por_nome,
    atualizar_produto,
    excluir_produto,
    nome_produto_existe,
    inserir_historico_calculo,
    listar_historico_calculos,
)
from app.services import (
    encontrar_melhor_caixa,
    gerar_instrucao_embalagem,
)


TIPOS_EMBALAGEM = [
    "caixa",
    "blister",
    "saco_feno_palha",
    "rolo_bolha",
    "rolo_cartonado",
    "tampa",
    "caixa_desmontada",
    "Esferovite",
]


# =========================
# CAIXAS
# =========================

def tela_consultar_caixas():
    st.header("📋 Consultar caixas cadastradas")

    termo_busca = st.text_input("Buscar caixa por nome")

    caixas = buscar_caixas_por_nome(termo_busca.strip()) if termo_busca.strip() else listar_caixas()

    if not caixas:
        st.warning("Nenhuma caixa encontrada.")
        return

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
                if st.button("Editar", key=f"editar_caixa_{caixa_id}"):
                    st.session_state.caixa_em_edicao = caixa_id
                    st.session_state.caixa_em_exclusao = None
                    st.rerun()

                if st.button("Excluir", key=f"excluir_caixa_{caixa_id}"):
                    st.session_state.caixa_em_exclusao = caixa_id
                    st.session_state.caixa_em_edicao = None
                    st.rerun()

            if caixa_em_exclusao == caixa_id:
                st.error(f"Confirma a exclusão da caixa '{nome}'?")
                col_confirmar, col_cancelar = st.columns(2)

                if col_confirmar.button("✅ Confirmar exclusão", key=f"confirmar_exclusao_caixa_{caixa_id}"):
                    excluir_caixa(caixa_id)
                    st.session_state.caixa_em_exclusao = None
                    st.success("Caixa excluída com sucesso.")
                    st.rerun()

                if col_cancelar.button("❌ Cancelar", key=f"cancelar_exclusao_caixa_{caixa_id}"):
                    st.session_state.caixa_em_exclusao = None
                    st.rerun()

            if caixa_em_edicao == caixa_id:
                st.divider()
                st.subheader("✏️ Editar caixa")

                with st.form(f"form_editar_caixa_{caixa_id}"):
                    novo_nome = st.text_input("Nome da caixa", value=nome)
                    nova_altura = st.number_input("Altura (cm)", min_value=0.01, value=float(altura), format="%.2f", key=f"altura_caixa_{caixa_id}")
                    nova_largura = st.number_input("Largura (cm)", min_value=0.01, value=float(largura), format="%.2f", key=f"largura_caixa_{caixa_id}")
                    novo_comprimento = st.number_input("Comprimento (cm)", min_value=0.01, value=float(comprimento), format="%.2f", key=f"comprimento_caixa_{caixa_id}")

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
                            try:
                                atualizar_caixa(caixa_id, nome_limpo, nova_altura, nova_largura, novo_comprimento)
                                st.session_state.caixa_em_edicao = None
                                st.success("Caixa atualizada com sucesso.")
                                st.rerun()
                            except Exception:
                                st.error("Não foi possível atualizar a caixa.")

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
                try:
                    inserir_caixa(nome_limpo, altura, largura, comprimento)
                    st.success(f"Caixa '{nome_limpo}' cadastrada com sucesso.")
                except Exception:
                    st.error("Não foi possível cadastrar a caixa.")


# =========================
# PRODUTOS
# =========================

def tela_consultar_produtos():
    st.header("📋 Consultar produtos cadastrados")

    termo_busca = st.text_input("Buscar produto por nome")

    produtos = buscar_produtos_por_nome(termo_busca.strip()) if termo_busca.strip() else listar_produtos()

    if not produtos:
        st.warning("Nenhum produto encontrado.")
        return

    produto_em_edicao = st.session_state.get("produto_em_edicao")
    produto_em_exclusao = st.session_state.get("produto_em_exclusao")

    for produto in produtos:
        produto_id, nome, altura, largura, comprimento, tipo_embalagem = produto

        with st.container(border=True):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.write(f"**ID:** {produto_id}")
                st.write(f"**Nome:** {nome}")
                st.write(f"**Altura:** {altura} cm")
                st.write(f"**Largura:** {largura} cm")
                st.write(f"**Comprimento:** {comprimento} cm")
                st.write(f"**Tipo de embalagem:** {tipo_embalagem}")

            with col2:
                if st.button("Editar", key=f"editar_produto_{produto_id}"):
                    st.session_state.produto_em_edicao = produto_id
                    st.session_state.produto_em_exclusao = None
                    st.rerun()

                if st.button("Excluir", key=f"excluir_produto_{produto_id}"):
                    st.session_state.produto_em_exclusao = produto_id
                    st.session_state.produto_em_edicao = None
                    st.rerun()

            if produto_em_exclusao == produto_id:
                st.error(f"Confirma a exclusão do produto '{nome}'?")
                col_confirmar, col_cancelar = st.columns(2)

                if col_confirmar.button("✅ Confirmar exclusão", key=f"confirmar_exclusao_produto_{produto_id}"):
                    excluir_produto(produto_id)
                    st.session_state.produto_em_exclusao = None
                    st.success("Produto excluído com sucesso.")
                    st.rerun()

                if col_cancelar.button("❌ Cancelar", key=f"cancelar_exclusao_produto_{produto_id}"):
                    st.session_state.produto_em_exclusao = None
                    st.rerun()

            if produto_em_edicao == produto_id:
                st.divider()
                st.subheader("✏️ Editar produto")

                with st.form(f"form_editar_produto_{produto_id}"):
                    novo_nome = st.text_input("Nome do produto", value=nome)
                    nova_altura = st.number_input("Altura (cm)", min_value=0.01, value=float(altura), format="%.2f", key=f"altura_produto_{produto_id}")
                    nova_largura = st.number_input("Largura (cm)", min_value=0.01, value=float(largura), format="%.2f", key=f"largura_produto_{produto_id}")
                    novo_comprimento = st.number_input("Comprimento (cm)", min_value=0.01, value=float(comprimento), format="%.2f", key=f"comprimento_produto_{produto_id}")

                    indice_tipo = TIPOS_EMBALAGEM.index(tipo_embalagem) if tipo_embalagem in TIPOS_EMBALAGEM else 0
                    novo_tipo_embalagem = st.selectbox(
                        "Tipo de embalagem",
                        TIPOS_EMBALAGEM,
                        index=indice_tipo,
                        key=f"tipo_produto_{produto_id}"
                    )

                    col_salvar, col_cancelar = st.columns(2)
                    salvar = col_salvar.form_submit_button("Salvar alterações")
                    cancelar = col_cancelar.form_submit_button("Cancelar")

                    if salvar:
                        nome_limpo = novo_nome.strip()

                        if not nome_limpo:
                            st.error("Informe o nome do produto.")
                        elif nome_produto_existe(nome_limpo, ignorar_id=produto_id):
                            st.error("Já existe um produto cadastrado com esse nome.")
                        else:
                            try:
                                atualizar_produto(
                                    produto_id,
                                    nome_limpo,
                                    nova_altura,
                                    nova_largura,
                                    novo_comprimento,
                                    novo_tipo_embalagem,
                                )
                                st.session_state.produto_em_edicao = None
                                st.success("Produto atualizado com sucesso.")
                                st.rerun()
                            except Exception:
                                st.error("Não foi possível atualizar o produto.")

                    if cancelar:
                        st.session_state.produto_em_edicao = None
                        st.rerun()


def tela_cadastrar_produto():
    st.header("📦 Cadastrar novo produto")

    with st.form("form_cadastro_produto"):
        nome = st.text_input("Nome do produto")
        altura = st.number_input("Altura (cm)", min_value=0.01, format="%.2f")
        largura = st.number_input("Largura (cm)", min_value=0.01, format="%.2f")
        comprimento = st.number_input("Comprimento (cm)", min_value=0.01, format="%.2f")
        tipo_embalagem = st.selectbox("Tipo de embalagem", TIPOS_EMBALAGEM)

        submitted = st.form_submit_button("Cadastrar produto")

        if submitted:
            nome_limpo = nome.strip()

            if not nome_limpo:
                st.error("Informe o nome do produto.")
            elif nome_produto_existe(nome_limpo):
                st.error("Já existe um produto cadastrado com esse nome.")
            else:
                try:
                    inserir_produto(nome_limpo, altura, largura, comprimento, tipo_embalagem)
                    st.success(f"Produto '{nome_limpo}' cadastrado com sucesso.")
                except Exception:
                    st.error("Não foi possível cadastrar o produto.")


# =========================
# CÁLCULO
# =========================

def tela_calcular_melhor_caixa():
    st.header("🧠 Calcular melhor caixa")

    caixas = listar_caixas()
    produtos = listar_produtos()

    if not caixas:
        st.warning("Cadastre pelo menos uma caixa antes de fazer o cálculo.")
        return

    if not produtos:
        st.warning("Cadastre pelo menos um produto antes de fazer o cálculo.")
        return

    opcoes_produtos = {produto[1]: produto for produto in produtos}
    nomes_produtos = list(opcoes_produtos.keys())

    with st.form("form_calculo"):
        nome_produto_selecionado = st.selectbox("Selecione o produto", nomes_produtos)
        quantidade = st.number_input("Quantidade de itens", min_value=1, step=1)

        submitted = st.form_submit_button("Calcular melhor caixa")

        if submitted:
            produto = opcoes_produtos[nome_produto_selecionado]
            produto_id, produto_nome, altura_item, largura_item, comprimento_item, tipo_embalagem = produto

            item_dim = (altura_item, largura_item, comprimento_item)

            melhor_caixa, capacidade, rotacao = encontrar_melhor_caixa(
                item_dim=item_dim,
                quantidade=quantidade,
                caixas=caixas,
            )

            if melhor_caixa:
                inserir_historico_calculo(
                    produto_id=produto_id,
                    produto_nome=produto_nome,
                    item_altura=altura_item,
                    item_largura=largura_item,
                    item_comprimento=comprimento_item,
                    quantidade=quantidade,
                    caixa_id=melhor_caixa[0],
                    caixa_nome=melhor_caixa[1],
                    capacidade=capacidade,
                    rotacao=rotacao,
                )

                st.success(f"Melhor caixa encontrada: {melhor_caixa[1]}")
                st.write(f"**Produto:** {produto_nome}")
                st.write(f"**Dimensões do produto:** {altura_item} x {largura_item} x {comprimento_item} cm")
                st.write(f"**Quantidade solicitada:** {quantidade}")
                st.write(f"**Capacidade máxima nesta caixa:** {capacidade} itens")
                st.write(f"**Dimensões da caixa:** {melhor_caixa[2]} x {melhor_caixa[3]} x {melhor_caixa[4]} cm")

                if rotacao:
                    st.write(f"**Melhor rotação do item:** {rotacao[0]} x {rotacao[1]} x {rotacao[2]} cm")
            else:
                st.error("Nenhuma caixa cadastrada comporta essa quantidade de itens.")


# =========================
# HISTÓRICO
# =========================

def tela_historico_calculos():
    st.header("🕘 Histórico de cálculos")

    historico = listar_historico_calculos()

    if not historico:
        st.warning("Ainda não há cálculos registrados.")
        return

    for registro in historico:
        (
            historico_id,
            produto_nome,
            item_altura,
            item_largura,
            item_comprimento,
            quantidade,
            caixa_nome,
            capacidade,
            rotacao_altura,
            rotacao_largura,
            rotacao_comprimento,
            criado_em,
        ) = registro

        with st.container(border=True):
            st.write(f"**Registro:** {historico_id}")
            st.write(f"**Data/Hora:** {criado_em}")
            st.write(f"**Produto:** {produto_nome}")
            st.write(f"**Dimensões do produto:** {item_altura} x {item_largura} x {item_comprimento} cm")
            st.write(f"**Quantidade:** {quantidade}")
            st.write(f"**Caixa sugerida:** {caixa_nome}")
            st.write(f"**Capacidade na caixa:** {capacidade} itens")

            if rotacao_altura and rotacao_largura and rotacao_comprimento:
                st.write(f"**Rotação usada:** {rotacao_altura} x {rotacao_largura} x {rotacao_comprimento} cm")


# =========================
# CALCULAR QUANTIDADE POR PESO
# =========================

def tela_calcular_quantidade_por_peso():
    st.header("⚖️ Calcular quantidade por peso")
    st.info("Todos os pesos devem ser informados em gramas (g).")

    with st.form("form_calculo_peso"):
        item = st.text_input("Nome do item")
        quantidade_amostra = st.number_input("Quantidade da amostra", min_value=1, step=1)
        peso_amostra = st.number_input("Peso da amostra (g)", min_value=0.01, format="%.2f")
        peso_total = st.number_input("Peso total (g)", min_value=0.01, format="%.2f")

        submitted = st.form_submit_button("Calcular quantidade")

        if submitted:
            item_limpo = item.strip()

            if not item_limpo:
                st.error("Informe o nome do item.")
                return

            peso_unitario = peso_amostra / quantidade_amostra
            quantidade_estimada = peso_total / peso_unitario
            quantidade_arredondada = round(quantidade_estimada)

            st.success("Cálculo realizado com sucesso.")
            st.write(f"**Item:** {item_limpo}")
            st.write(f"**Quantidade da amostra:** {quantidade_amostra} unidades")
            st.write(f"**Peso da amostra:** {peso_amostra:.2f} g")
            st.write(f"**Peso total informado:** {peso_total:.2f} g")
            st.write(f"**Peso por unidade:** {peso_unitario:.4f} g")
            st.write(f"**Quantidade estimada:** {quantidade_estimada:.2f} unidades")
            st.write(f"**Quantidade arredondada:** {quantidade_arredondada} unidades")


# =========================
# PEDIDO DE EMBALAGEM
# =========================

def tela_pedido_embalagem():
    st.header("🧾 Pedido de embalagem")

    produtos = listar_produtos()
    caixas = listar_caixas()

    if not produtos:
        st.warning("Cadastre produtos antes de montar um pedido.")
        return

    if "itens_pedido" not in st.session_state:
        st.session_state.itens_pedido = []

    if "resultado_pedido" not in st.session_state:
        st.session_state.resultado_pedido = []

    mapa_produtos = {produto[1]: produto for produto in produtos}
    nomes_produtos = list(mapa_produtos.keys())

    with st.form("form_adicionar_item_pedido"):
        nome_produto = st.selectbox("Produto", nomes_produtos)
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        submitted = st.form_submit_button("Adicionar item ao pedido")

        if submitted:
            produto = mapa_produtos[nome_produto]
            st.session_state.itens_pedido.append({
                "produto": produto,
                "quantidade": quantidade
            })
            st.success("Item adicionado ao pedido.")
            st.rerun()

    st.subheader("Itens do pedido")

    if not st.session_state.itens_pedido:
        st.info("Nenhum item adicionado ainda.")
    else:
        for i, item in enumerate(st.session_state.itens_pedido):
            produto = item["produto"]
            quantidade = item["quantidade"]

            with st.container(border=True):
                st.write(f"**Produto:** {produto[1]}")
                st.write(f"**Quantidade:** {quantidade}")
                st.write(f"**Tipo de embalagem:** {produto[5]}")

                if st.button("Remover item", key=f"remover_item_{i}"):
                    st.session_state.itens_pedido.pop(i)
                    st.rerun()

    col1, col2 = st.columns(2)

    if col1.button("Gerar embalagem do pedido"):
        if not st.session_state.itens_pedido:
            st.warning("Adicione pelo menos um item ao pedido.")
        else:
            resultados = []

            for item in st.session_state.itens_pedido:
                instrucao = gerar_instrucao_embalagem(
                    produto=item["produto"],
                    quantidade=item["quantidade"],
                    caixas=caixas,
                )
                resultados.append(instrucao)

            st.session_state.resultado_pedido = resultados

    if col2.button("Limpar pedido"):
        st.session_state.itens_pedido = []
        st.session_state.resultado_pedido = []
        st.rerun()

    if st.session_state.resultado_pedido:
        st.subheader("Resultado do pedido")

        for resultado in st.session_state.resultado_pedido:
            with st.container(border=True):
                st.write(f"**Produto:** {resultado['produto']}")
                st.write(f"**Quantidade:** {resultado['quantidade']}")
                st.write(f"**Tipo de embalagem:** {resultado['tipo_embalagem']}")
                st.write(f"**Embalagem principal:** {resultado['embalagem_principal']}")
                st.write(f"**Observação:** {resultado['observacao']}")


def run_app():
    st.set_page_config(page_title="Sistema de Embalagem", layout="centered")

    init_db()

    if "caixa_em_edicao" not in st.session_state:
        st.session_state.caixa_em_edicao = None
    if "caixa_em_exclusao" not in st.session_state:
        st.session_state.caixa_em_exclusao = None
    if "produto_em_edicao" not in st.session_state:
        st.session_state.produto_em_edicao = None
    if "produto_em_exclusao" not in st.session_state:
        st.session_state.produto_em_exclusao = None

    st.title("📦 Sistema Inteligente de Embalagem")

    opcao = st.sidebar.radio(
        "Escolha uma opção",
        [
            "Consultar caixas cadastradas",
            "Cadastrar nova caixa",
            "Consultar produtos cadastrados",
            "Cadastrar novo produto",
            "Calcular melhor caixa",
            "Pedido de embalagem",
            "Histórico de cálculos",
            "Calcular quantidade por peso",
        ],
    )

    if opcao == "Consultar caixas cadastradas":
        tela_consultar_caixas()
    elif opcao == "Cadastrar nova caixa":
        tela_cadastrar_caixa()
    elif opcao == "Consultar produtos cadastrados":
        tela_consultar_produtos()
    elif opcao == "Cadastrar novo produto":
        tela_cadastrar_produto()
    elif opcao == "Calcular melhor caixa":
        tela_calcular_melhor_caixa()
    elif opcao == "Pedido de embalagem":
        tela_pedido_embalagem()
    elif opcao == "Histórico de cálculos":
        tela_historico_calculos()
    elif opcao == "Calcular quantidade por peso":
        tela_calcular_quantidade_por_peso()