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