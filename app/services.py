def gerar_rotacoes(item):
    a, b, c = item
    return [
        (a, b, c),
        (a, c, b),
        (b, a, c),
        (b, c, a),
        (c, a, b),
        (c, b, a),
    ]


def calcular_max_itens(item, caixa):
    """
    caixa no formato:
    (id, nome, altura, largura, comprimento)
    """
    caixa_altura = caixa[2]
    caixa_largura = caixa[3]
    caixa_comprimento = caixa[4]

    max_itens = 0
    melhor_rotacao = None

    for rot in gerar_rotacoes(item):
        a, l, c = rot

        if a <= 0 or l <= 0 or c <= 0:
            continue

        qtd = int(caixa_altura // a) * int(caixa_largura // l) * int(caixa_comprimento // c)

        if qtd > max_itens:
            max_itens = qtd
            melhor_rotacao = rot

    return max_itens, melhor_rotacao


def encontrar_melhor_caixa(item_dim, quantidade, caixas):
    melhor_caixa = None
    melhor_capacidade = 0
    melhor_rotacao = None
    menor_volume = None

    for caixa in caixas:
        capacidade, rotacao = calcular_max_itens(item_dim, caixa)

        if capacidade >= quantidade:
            volume_caixa = caixa[2] * caixa[3] * caixa[4]

            if menor_volume is None or volume_caixa < menor_volume:
                menor_volume = volume_caixa
                melhor_caixa = caixa
                melhor_capacidade = capacidade
                melhor_rotacao = rotacao

    return melhor_caixa, melhor_capacidade, melhor_rotacao


def escolher_largura_bolha(altura, largura, comprimento):
    maior_dim = max(altura, largura, comprimento)

    if maior_dim <= 30:
        return "Plástico bolha 30 cm"
    elif maior_dim <= 60:
        return "Plástico bolha 60 cm"
    return "Plástico bolha 1 m"


def gerar_instrucao_embalagem(produto, quantidade, caixas):
    produto_id, nome, altura, largura, comprimento, tipo_embalagem = produto
    nome_upper = nome.upper().strip()

    resultado = {
        "produto": nome,
        "quantidade": quantidade,
        "tipo_embalagem": tipo_embalagem,
        "embalagem_principal": None,
        "observacao": None,
    }

    if tipo_embalagem in ["caixa", "blister"]:
        item_dim = (altura, largura, comprimento)
        melhor_caixa, capacidade, rotacao = encontrar_melhor_caixa(
            item_dim=item_dim,
            quantidade=quantidade,
            caixas=caixas,
        )

        if melhor_caixa:
            resultado["embalagem_principal"] = f"Caixa: {melhor_caixa[1]}"
            resultado["observacao"] = f"Capacidade da caixa: {capacidade} itens"
        else:
            resultado["embalagem_principal"] = "Nenhuma caixa encontrada"
            resultado["observacao"] = "Verificar manualmente"

    elif tipo_embalagem in ["saco_feno_palha", "rolo_bolha"]:
        resultado["embalagem_principal"] = "Filme preto"
        resultado["observacao"] = "Aplicar 1 volta cobrindo todo o conteúdo"

    elif tipo_embalagem == "rolo_cartonado":
        material = escolher_largura_bolha(altura, largura, comprimento)
        resultado["embalagem_principal"] = material
        resultado["observacao"] = "Aplicar 3 voltas"

    elif tipo_embalagem == "tampa":
        resultado["embalagem_principal"] = "Incluir junto na caixa"
        resultado["observacao"] = "Produto deve acompanhar embalagem principal de outro item"

    elif tipo_embalagem == "caixa_desmontada":
        material = escolher_largura_bolha(altura, largura, comprimento)
        resultado["embalagem_principal"] = material
        resultado["observacao"] = "Enrolar em plástico bolha"

    else:
        resultado["embalagem_principal"] = "Tipo não mapeado"
        resultado["observacao"] = "Verificar cadastro do produto"

    if nome_upper.startswith("VD"):
        obs_atual = resultado["observacao"] or ""
        complemento = "Aplicar reforço com plástico bolha após embalagem"
        resultado["observacao"] = f"{obs_atual} | {complemento}" if obs_atual else complemento

    return resultado


def consolidar_embalagem(resultados):
    resumo = {
        "caixas": {},
        "filme_preto": 0,
        "plastico_bolha": {},
        "outros": []
    }

    for r in resultados:
        emb = r["embalagem_principal"] or ""

        if emb.startswith("Caixa:"):
            nome_caixa = emb.replace("Caixa:", "").strip()
            resumo["caixas"][nome_caixa] = resumo["caixas"].get(nome_caixa, 0) + 1

        elif "Filme preto" in emb:
            resumo["filme_preto"] += 1

        elif "Plástico bolha" in emb:
            resumo["plastico_bolha"][emb] = resumo["plastico_bolha"].get(emb, 0) + 1

        else:
            resumo["outros"].append(r["produto"])

    return resumo