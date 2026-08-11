from reportlab.lib.units import mm

def desenhar_etiqueta_a5(c, item, x_base, y_base, col_w, row_h, scale):
    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h

    # --- 1. DESCRIÇÃO DO PRODUTO ---
    tam_fonte_desc = int(36 * scale)
    c.setFont("Arial-Black", tam_fonte_desc)
    max_largura_texto = col_w - (9.0 * mm * scale)
    y_primeira_linha = topo_etiqueta - (62.0 * mm * scale)
    desc = item.get("desc", "")

    if c.stringWidth(desc, "Arial-Black", tam_fonte_desc) <= max_largura_texto:
        c.drawCentredString(x_center, y_primeira_linha, desc)
    else:
        palavras = desc.split()
        linha1, linha2 = "", ""
        for palavra in palavras:
            teste_linha1 = f"{linha1} {palavra}".strip()
            if c.stringWidth(teste_linha1, "Arial-Black", tam_fonte_desc) <= max_largura_texto and not linha2:
                linha1 = teste_linha1
            else:
                linha2 = f"{linha2} {palavra}".strip()
        y_segunda_linha = y_primeira_linha - ((tam_fonte_desc * 0.35 + 3.0) * mm)
        c.drawCentredString(x_center, y_primeira_linha, linha1)
        c.drawCentredString(x_center, y_segunda_linha, linha2)

    # --- 2. OFFSETS CENTRAIS (Sem Rebaixa) ---
    offset_rs_unico_y = 44.0
    offset_reais_padrao = 62.0
    offset_centavos_padrao = 48.0

    # --- 3. BLOCO PREÇO UNITÁRIO CENTRALIZADO ---
    val_por_raw = item.get("por", "").replace(".", ",")
    if "," in val_por_raw:
        reais_por_str, centavos_por_str = val_por_raw.split(",")[0], f",{val_por_raw.split(',')[1]}"
    else:
        reais_por_str, centavos_por_str = val_por_raw, ",00"

    num_digitos_reais = len(reais_por_str)
    if num_digitos_reais <= 2:
        fonte_reais, fonte_centavos = 144, 72
        offset_y_reais, offset_y_centavos = offset_reais_padrao, offset_centavos_padrao
    elif num_digitos_reais == 3:
        fonte_reais, fonte_centavos = 110, 55
        offset_y_reais, offset_y_centavos = offset_reais_padrao - 5.0, offset_centavos_padrao
    else:
        fonte_reais, fonte_centavos = 85, 42
        offset_y_reais, offset_y_centavos = offset_reais_padrao - 11.0, offset_centavos_padrao

    tam_fonte_rs = int(30 * scale)
    tam_fonte_reais_por = int(fonte_reais * scale)
    tam_fonte_centavos_por = int(fonte_centavos * scale)
    tam_fonte_un_por = int(20 * scale)

    largura_util_maxima = col_w - (9.0 * mm * scale)

    while True:
        c.setFont("Arial-Black", tam_fonte_rs)
        largura_rs = c.stringWidth("R$", "Arial-Black", tam_fonte_rs)
        c.setFont("Arial-Black", tam_fonte_reais_por)
        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)
        c.setFont("Arial-Black", tam_fonte_centavos_por)
        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        largura_total_bloco = largura_rs + (4.0 * mm * scale) + largura_reais_por + (1.5 * mm * scale) + largura_centavos_por

        if largura_total_bloco <= largura_util_maxima or tam_fonte_reais_por <= 40:
            break

        tam_fonte_reais_por = int(tam_fonte_reais_por * 0.90)
        tam_fonte_centavos_por = int(tam_fonte_centavos_por * 0.90)
        tam_fonte_rs = int(tam_fonte_rs * 0.90)

    x_inicio_bloco = x_center - (largura_total_bloco / 2.0)
    
    y_rs = y_primeira_linha - (offset_rs_unico_y * mm * scale)
    c.setFont("Arial-Black", tam_fonte_rs)
    c.drawString(x_inicio_bloco, y_rs, "R$")

    x_reais_por = x_inicio_bloco + largura_rs + (4.0 * mm * scale)
    y_reais_por = y_primeira_linha - (offset_y_reais * mm * scale)
    c.setFont("Arial-Black", tam_fonte_reais_por)
    c.drawString(x_reais_por, y_reais_por, reais_por_str)

    x_centavos_por = x_reais_por + largura_reais_por + (1.5 * mm * scale)
    y_centavos_por = y_primeira_linha - (offset_y_centavos * mm * scale)
    c.setFont("Arial-Black", tam_fonte_centavos_por)
    c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

    c.setFont("Arial-Black", tam_fonte_un_por)
    x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
    c.drawCentredString(x_un_por, y_centavos_por - (12.0 * mm * scale), item.get("un", ""))
