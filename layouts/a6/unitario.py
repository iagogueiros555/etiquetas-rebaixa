from reportlab.lib.units import mm

def desenhar_etiqueta_a6(c, item, x_base, y_base, col_w, row_h, scale):
    """Etiqueta A6 - Preço Único, sem validade"""

    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h  # Borda superior de cada etiqueta (0 a 99mm)

    # -------------------------------------------------------------------
    # 1. DESCRIÇÃO DO PRODUTO (Margem exata de 2mm em cada lado = 4mm total)
    # -------------------------------------------------------------------
    tam_fonte_desc = int(16 * scale)
    c.setFont("Arial-Black", tam_fonte_desc)

    max_largura_texto = col_w - (4.0 * mm * scale)
    y_primeira_linha = topo_etiqueta - (40.8 * mm * scale)
    desc = item["desc"]

    if c.stringWidth(desc, "Arial-Black", tam_fonte_desc) <= max_largura_texto:
        c.drawCentredString(x_center, y_primeira_linha, desc)
    else:
        palavras = desc.split()
        linha1 = ""
        linha2 = ""

        for palavra in palavras:
            teste_linha1 = f"{linha1} {palavra}".strip()
            if c.stringWidth(teste_linha1, "Arial-Black", tam_fonte_desc) <= max_largura_texto and not linha2:
                linha1 = teste_linha1
            else:
                linha2 = f"{linha2} {palavra}".strip()

        espacamento_linhas = (tam_fonte_desc * 0.35 + 1.8) * mm
        y_segunda_linha = y_primeira_linha - espacamento_linhas

        c.drawCentredString(x_center, y_primeira_linha, linha1)
        c.drawCentredString(x_center, y_segunda_linha, linha2)

    # -------------------------------------------------------------------
    # 2. BLOCO DE PREÇO ÚNICO (DINAMICAMENTE CENTRALIZADO) - Fonte 104pt
    # -------------------------------------------------------------------
    val_por_raw = item["por"].replace(".", ",")
    if "," in val_por_raw:
        partes_por = val_por_raw.split(",")
        reais_por_str = partes_por[0]
        centavos_por_str = f",{partes_por[1]}"
    else:
        reais_por_str = val_por_raw
        centavos_por_str = ",00"

    tam_fonte_rs = int(20 * scale)
    tam_fonte_reais_por = int(104 * scale)
    tam_fonte_centavos_por = int(52 * scale)
    tam_fonte_un_por = int(14 * scale)

    y_offset_rs = 62.0 * mm * scale
    y_offset_reais = 85.0 * mm * scale
    y_offset_centavos = 68.5 * mm * scale
    dist_un = 8.5 * mm * scale

    # Medição física das larguras
    c.setFont("Arial-Black", tam_fonte_rs)
    largura_rs = c.stringWidth("R$", "Arial-Black", tam_fonte_rs)

    c.setFont("Arial-Black", tam_fonte_reais_por)
    largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

    c.setFont("Arial-Black", tam_fonte_centavos_por)
    largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

    # Largura total: R$ + 2mm + REAIS + 0mm + CENTAVOS
    largura_total_bloco = (
        largura_rs
        + (2.0 * mm * scale)
        + largura_reais_por
        + (0.0 * mm * scale)
        + largura_centavos_por
    )

    # Ponto X inicial para centralizar no meio da etiqueta
    x_inicio_bloco = x_center - (largura_total_bloco / 2.0)

    x_rs = x_inicio_bloco
    x_reais_por = x_rs + largura_rs + (2.0 * mm * scale)
    x_centavos_por = x_reais_por + largura_reais_por + (0.0 * mm * scale)

    c.setFont("Arial-Black", tam_fonte_rs)
    y_rs = topo_etiqueta - y_offset_rs
    c.drawString(x_rs, y_rs, "R$")

    c.setFont("Arial-Black", tam_fonte_reais_por)
    y_reais_por = topo_etiqueta - y_offset_reais
    c.drawString(x_reais_por, y_reais_por, reais_por_str)

    c.setFont("Arial-Black", tam_fonte_centavos_por)
    y_centavos_por = topo_etiqueta - y_offset_centavos
    c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

    c.setFont("Arial-Black", tam_fonte_un_por)
    x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
    y_un_por = y_centavos_por - dist_un
    c.drawCentredString(x_un_por, y_un_por, item["un"])
