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
    ajustar_tampas_no_pedido,
    consolidar_embalagem,
)


TIPOS_EMBALAGEM = [
    "caixa",
    "blister",
    "saco_feno_palha",
    "rolo_bolha",
    "rolo_cartonado",
    "tampa",
    "caixa_desmontada",
    "esferovite",
]


# =========================
# ESTILO
# =========================

def aplicar_estilo():
    st.markdown(
        """
        <style>
            .main-title {
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }
            .sub-title {
                color: #94a3b8;
                font-size: 0.95rem;
                margin-bottom: 1.2rem;
            }
            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                margin-bottom: 0.6rem;
            }
            .soft-card {
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 14px 16px;
                background: rgba(255,255,255,0.02);
                margin-bottom: 12px;
            }
            .metric-card {
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 16px;
                background: rgba(255,255,255,0.03);
                text-align: center;
            }
            .metric-label {
                font-size: 0.9rem;
                color: #94a3b8;
            }
            .metric-value {
                font-size: 1.6rem;
                font-weight: 700;
                margin-top: 4px;
            }
            .result-box {
                border-left: 4px solid #3b82f6;
                padding: 10px 14px;
                border-radius: 10px;
                background: rgba(59,130,246,0.08);
                margin-bottom: 10px;
            }
            .warning-box {
                border-left: 4px solid #f59e0b;
                padding: 10px 14px;
                border-radius: 10px;
                background: rgba(245,158,11,0.08);
                margin-bottom: 10px;
            }
            .danger-box {
                border-left: 4px solid #ef4444;
                padding: 10px 14px;
                border-radius: 10px;
                background: rgba(239,68,68,0.08);
                margin-bottom: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown('<div class="main-title">📦 Sistema Inteligente de Embalagem</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Gestão de caixas, produtos e definição de embalagem por pedido.</div>',
        unsafe_allow_html=True,
    )


def render_metricas_topo():
    total_caixas = len(listar_caixas())
    total_produtos = len(listar_produtos())
    itens_pedido = len(st.session_state.get("itens_pedido", []))
    resultados = len(st.session_state.get("resultado_pedido", []))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Caixas cadastradas</div>
                <div class="metric-value">{total_caixas}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Produtos cadastrados</div>
                <div class="metric-value">{total_produtos}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Itens no pedido</div>
                <div class="metric-value">{itens_pedido}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Resultados gerados</div>
                <div class="metric-value">{resultados}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def titulo_secao(texto):
    st.markdown(f'<div class="section-title">{texto}</div>', unsafe_allow_html=True)


def badge_tipo(tipo):
    mapa = {
        "caixa": "📦 Caixa",
        "blister": "📦 Blister",
        "saco_feno_palha": "🧻 Saco de feno/palha",
        "rolo_bolha": "🫧 Rolo de plástico bolha",
        "rolo_cartonado": "📜 Rolo cartonado",
        "tampa": "🔩 Tampa",
        "caixa_desmontada": "📦 Caixa desmontada",
    }
    return mapa.get(tipo, tipo)


# =========================
# CAIXAS
# =========================

def tela_consultar_caixas():
    titulo_secao("📋 Consultar caixas cadastradas")

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
            col1, col2 = st.columns([3, 1.2])

            with col1:
                st.write(f"**{nome}**")
                st.caption(f"ID: {caixa_id}")
                st.write(f"Altura: **{altura} cm**")
                st.write(f"Largura: **{largura} cm**")
                st.write(f"Comprimento: **{comprimento} cm**")

            with col2:
                if st.button("Editar", key=f"editar_caixa_{caixa_id}", use_container_width=True):
                    st.session_state.caixa_em_edicao = caixa_id
                    st.session_state.caixa_em_exclusao = None
                    st.rerun()

                if st.button("Excluir", key=f"excluir_caixa_{caixa_id}", use_container_width=True):
                    st.session_state.caixa_em_exclusao = caixa_id
                    st.session_state.caixa_em_edicao = None
                    st.rerun()

            if caixa_em_exclusao == caixa_id:
                st.error(f"Confirma a exclusão da caixa '{nome}'?")
                c1, c2 = st.columns(2)

                if c1.button("✅ Confirmar exclusão", key=f"confirmar_exclusao_caixa_{caixa_id}", use_container_width=True):
                    excluir_caixa(caixa_id)
                    st.session_state.caixa_em_exclusao = None
                    st.success("Caixa excluída com sucesso.")
                    st.rerun()

                if c2.button("❌ Cancelar", key=f"cancelar_exclusao_caixa_{caixa_id}", use_container_width=True):
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

                    c1, c2 = st.columns(2)
                    salvar = c1.form_submit_button("Salvar alterações", use_container_width=True)
                    cancelar = c2.form_submit_button("Cancelar", use_container_width=True)

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
    titulo_secao("📦 Cadastrar nova caixa")

    with st.form("form_cadastro_caixa", clear_on_submit=True):
        nome = st.text_input("Nome da caixa")
        col1, col2, col3 = st.columns(3)
        with col1:
            altura = st.number_input("Altura (cm)", min_value=0.01, format="%.2f")
        with col2:
            largura = st.number_input("Largura (cm)", min_value=0.01, format="%.2f")
        with col3:
            comprimento = st.number_input("Comprimento (cm)", min_value=0.01, format="%.2f")

        submitted = st.form_submit_button("Cadastrar caixa", use_container_width=True)

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
    titulo_secao("📋 Consultar produtos cadastrados")

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
            col1, col2 = st.columns([3, 1.2])

            with col1:
                st.write(f"**{nome}**")
                st.caption(f"ID: {produto_id}")
                st.write(f"Altura: **{altura} cm**")
                st.write(f"Largura: **{largura} cm**")
                st.write(f"Comprimento: **{comprimento} cm**")
                st.write(f"Tipo de embalagem: **{badge_tipo(tipo_embalagem)}**")

            with col2:
                if st.button("Editar", key=f"editar_produto_{produto_id}", use_container_width=True):
                    st.session_state.produto_em_edicao = produto_id
                    st.session_state.produto_em_exclusao = None
                    st.rerun()

                if st.button("Excluir", key=f"excluir_produto_{produto_id}", use_container_width=True):
                    st.session_state.produto_em_exclusao = produto_id
                    st.session_state.produto_em_edicao = None
                    st.rerun()

            if produto_em_exclusao == produto_id:
                st.error(f"Confirma a exclusão do produto '{nome}'?")
                c1, c2 = st.columns(2)

                if c1.button("✅ Confirmar exclusão", key=f"confirmar_exclusao_produto_{produto_id}", use_container_width=True):
                    excluir_produto(produto_id)
                    st.session_state.produto_em_exclusao = None
                    st.success("Produto excluído com sucesso.")
                    st.rerun()

                if c2.button("❌ Cancelar", key=f"cancelar_exclusao_produto_{produto_id}", use_container_width=True):
                    st.session_state.produto_em_exclusao = None
                    st.rerun()

            if produto_em_edicao == produto_id:
                st.divider()
                st.subheader("✏️ Editar produto")

                with st.form(f"form_editar_produto_{produto_id}"):
                    novo_nome = st.text_input("Nome do produto", value=nome)

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        nova_altura = st.number_input("Altura (cm)", min_value=0.01, value=float(altura), format="%.2f", key=f"altura_produto_{produto_id}")
                    with c2:
                        nova_largura = st.number_input("Largura (cm)", min_value=0.01, value=float(largura), format="%.2f", key=f"largura_produto_{produto_id}")
                    with c3:
                        novo_comprimento = st.number_input("Comprimento (cm)", min_value=0.01, value=float(comprimento), format="%.2f", key=f"comprimento_produto_{produto_id}")

                    indice_tipo = TIPOS_EMBALAGEM.index(tipo_embalagem) if tipo_embalagem in TIPOS_EMBALAGEM else 0
                    novo_tipo_embalagem = st.selectbox(
                        "Tipo de embalagem",
                        TIPOS_EMBALAGEM,
                        index=indice_tipo,
                        format_func=badge_tipo,
                        key=f"tipo_produto_{produto_id}"
                    )

                    c1, c2 = st.columns(2)
                    salvar = c1.form_submit_button("Salvar alterações", use_container_width=True)
                    cancelar = c2.form_submit_button("Cancelar", use_container_width=True)

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
    titulo_secao("📦 Cadastrar novo produto")

    with st.form("form_cadastro_produto", clear_on_submit=True):
        nome = st.text_input("Nome do produto")

        c1, c2, c3 = st.columns(3)
        with c1:
            altura = st.number_input("Altura (cm)", min_value=0.01, format="%.2f")
        with c2:
            largura = st.number_input("Largura (cm)", min_value=0.01, format="%.2f")
        with c3:
            comprimento = st.number_input("Comprimento (cm)", min_value=0.01, format="%.2f")

        tipo_embalagem = st.selectbox("Tipo de embalagem", TIPOS_EMBALAGEM, format_func=badge_tipo)

        submitted = st.form_submit_button("Cadastrar produto", use_container_width=True)

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
# CÁLCULO UNITÁRIO
# =========================

def tela_calcular_melhor_caixa():
    titulo_secao("🧠 Calcular melhor caixa (item único)")

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

        submitted = st.form_submit_button("Calcular melhor caixa", use_container_width=True)

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

                with st.container(border=True):
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
    titulo_secao("🕘 Histórico de cálculos")

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
# PESO
# =========================

def tela_calcular_quantidade_por_peso():
    titulo_secao("⚖️ Calcular quantidade por peso")
    st.info("Todos os pesos devem ser informados em gramas (g).")

    with st.form("form_calculo_peso"):
        item = st.text_input("Nome do item")

        c1, c2, c3 = st.columns(3)
        with c1:
            quantidade_amostra = st.number_input("Quantidade da amostra", min_value=1, step=1)
        with c2:
            peso_amostra = st.number_input("Peso da amostra (g)", min_value=0.01, format="%.2f")
        with c3:
            peso_total = st.number_input("Peso total (g)", min_value=0.01, format="%.2f")

        submitted = st.form_submit_button("Calcular quantidade", use_container_width=True)

        if submitted:
            item_limpo = item.strip()

            if not item_limpo:
                st.error("Informe o nome do item.")
                return

            peso_unitario = peso_amostra / quantidade_amostra
            quantidade_estimada = peso_total / peso_unitario
            quantidade_arredondada = round(quantidade_estimada)

            st.success("Cálculo realizado com sucesso.")

            with st.container(border=True):
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

def render_resultado_item(resultado):
    embalagem = resultado["embalagem_principal"] or ""
    observacao = resultado["observacao"] or ""

    if "Verificar manualmente" in embalagem or "Verificar manualmente" in observacao:
        classe = "danger-box"
    elif "Incluir junto na caixa" in embalagem or "Acompanhar item principal" in observacao:
        classe = "warning-box"
    else:
        classe = "result-box"

    st.markdown(
        f"""
        <div class="{classe}">
            <strong>{resultado['produto']}</strong><br>
            Quantidade: {resultado['quantidade']}<br>
            Tipo: {badge_tipo(resultado['tipo_embalagem'])}<br>
            Embalagem principal: {resultado['embalagem_principal']}<br>
            Observação: {resultado['observacao']}
        </div>
        """,
        unsafe_allow_html=True,
    )


def tela_pedido_embalagem():
    titulo_secao("🧾 Pedido de embalagem")
    st.caption("Monte o pedido com vários itens e gere automaticamente a instrução de embalagem por item.")

    produtos = listar_produtos()
    caixas = listar_caixas()

    if not produtos:
        st.warning("Cadastre produtos antes de montar um pedido.")
        return

    if "itens_pedido" not in st.session_state:
        st.session_state.itens_pedido = []

    if "resultado_pedido" not in st.session_state:
        st.session_state.resultado_pedido = []

    if "resumo_pedido" not in st.session_state:
        st.session_state.resumo_pedido = {}

    mapa_produtos = {produto[1]: produto for produto in produtos}
    nomes_produtos = list(mapa_produtos.keys())

    col_esq, col_dir = st.columns([2, 1])

    with col_esq:
        with st.container(border=True):
            st.subheader("Adicionar item ao pedido")

            with st.form("form_adicionar_item_pedido"):
                nome_produto = st.selectbox("Produto", nomes_produtos)
                quantidade = st.number_input("Quantidade", min_value=1, step=1)
                submitted = st.form_submit_button("Adicionar item", use_container_width=True)

                if submitted:
                    produto = mapa_produtos[nome_produto]
                    st.session_state.itens_pedido.append({
                        "produto": produto,
                        "quantidade": quantidade
                    })
                    st.success("Item adicionado ao pedido.")
                    st.rerun()

    with col_dir:
        with st.container(border=True):
            st.subheader("Ações")
            st.write(f"Itens no pedido: **{len(st.session_state.itens_pedido)}**")

            gerar = st.button("Gerar embalagem do pedido", use_container_width=True)
            limpar = st.button("Limpar pedido", use_container_width=True)

            if gerar:
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

                    resultados = ajustar_tampas_no_pedido(resultados)
                    resumo = consolidar_embalagem(resultados)

                    st.session_state.resultado_pedido = resultados
                    st.session_state.resumo_pedido = resumo
                    st.rerun()

            if limpar:
                st.session_state.itens_pedido = []
                st.session_state.resultado_pedido = []
                st.session_state.resumo_pedido = {}
                st.rerun()

    st.subheader("Itens do pedido")

    if not st.session_state.itens_pedido:
        st.info("Nenhum item adicionado ainda.")
    else:
        for i, item in enumerate(st.session_state.itens_pedido):
            produto = item["produto"]
            quantidade = item["quantidade"]

            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"**{produto[1]}**")
                    st.write(f"Quantidade: **{quantidade}**")
                    st.write(f"Tipo de embalagem: **{badge_tipo(produto[5])}**")
                with c2:
                    if st.button("Remover", key=f"remover_item_{i}", use_container_width=True):
                        st.session_state.itens_pedido.pop(i)
                        st.rerun()

    if st.session_state.resultado_pedido:
        st.subheader("Resultado do pedido")
        for resultado in st.session_state.resultado_pedido:
            render_resultado_item(resultado)

    if st.session_state.resumo_pedido:
        resumo = st.session_state.resumo_pedido

        st.subheader("📊 Resumo consolidado")

        c1, c2, c3 = st.columns(3)

        with c1:
            with st.container(border=True):
                st.write("**📦 Caixas**")
                if resumo["caixas"]:
                    for nome, qtd in resumo["caixas"].items():
                        st.write(f"- {nome} → {qtd}")
                else:
                    st.caption("Nenhuma caixa utilizada.")

        with c2:
            with st.container(border=True):
                st.write("**🧻 Filme preto**")
                if resumo["filme_preto"] > 0:
                    st.write(f"- {resumo['filme_preto']} itens")
                else:
                    st.caption("Sem uso de filme preto.")

        with c3:
            with st.container(border=True):
                st.write("**🫧 Plástico bolha**")
                if resumo["plastico_bolha"]:
                    for tipo, qtd in resumo["plastico_bolha"].items():
                        st.write(f"- {tipo} → {qtd}")
                else:
                    st.caption("Sem uso de plástico bolha.")

        if resumo["outros"]:
            with st.container(border=True):
                st.write("**⚠️ Outros / verificar manualmente**")
                for item in resumo["outros"]:
                    st.write(f"- {item}")


def run_app():
    st.set_page_config(page_title="Sistema de Embalagem", layout="wide")
    aplicar_estilo()
    init_db()

    if "caixa_em_edicao" not in st.session_state:
        st.session_state.caixa_em_edicao = None
    if "caixa_em_exclusao" not in st.session_state:
        st.session_state.caixa_em_exclusao = None
    if "produto_em_edicao" not in st.session_state:
        st.session_state.produto_em_edicao = None
    if "produto_em_exclusao" not in st.session_state:
        st.session_state.produto_em_exclusao = None

    render_header()
    render_metricas_topo()
    st.divider()

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