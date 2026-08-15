from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit

def desenhar_etiqueta_a6(c, item, x_base, y_base, col_w, row_h, scale):
    """Etiqueta A6 - Promocional (De / Por), sem validade"""

    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h  # Borda superior de cada etiqueta (0 a 99mm)

    # -------------------------------------------------------------------
    # 1. DESCRIÇÃO DO PRODUTO (Margem exata de 2mm em cada lado = 4mm total)
    # -------------------------------------------------------------------
    tam_fonte_desc = int(18 * scale)  # antes: 16 — "um pouco maior"
    max_largura_texto = col_w - (4.0 * mm * scale)
    y_primeira_linha = topo_etiqueta - (40.8 * mm * scale)
    desc = item["desc"]

    # Vai diminuindo de 1 em 1 ponto (nunca abrupto) até caber em no máximo 2 linhas
    linhas_desc = []
    while tam_fonte_desc > 8:
        c.setFont("Arial-Black", tam_fonte_desc)
        linhas_desc = simpleSplit(desc, "Arial-Black", tam_fonte_desc, max_largura_texto)
        if len(linhas_desc) <= 2:
            break
        tam_fonte_desc -= 1

    linhas_desc = linhas_desc[:2]  # trava de segurança: nunca desenha uma 3ª linha
    c.setFont("Arial-Black", tam_fonte_desc)
    espacamento_desc = (tam_fonte_desc * 0.35 + 1.8) * mm * scale

    y_linha_atual = y_primeira_linha
    for linha in linhas_desc:
        c.drawCentredString(x_center, y_linha_atual, linha)
        y_linha_atual -= espacamento_desc

    # -------------------------------------------------------------------
    # 2. BLOCO "DE / POR"
    # -------------------------------------------------------------------
    tam_fonte_de = int(12 * scale)
    c.setFont("Arial-Black", tam_fonte_de)

    x_de = x_base + (7.2 * mm * scale)
    y_de = topo_etiqueta - (62.2 * mm * scale)
    y_rs_de = topo_etiqueta - (66.5 * mm * scale)

    c.drawString(x_de, y_de, "De")
    c.drawString(x_de, y_rs_de, "R$")

    val_de_raw = item["de"].replace(".", ",")
    if "," in val_de_raw:
        partes_de = val_de_raw.split(",")
        reais_de_str = partes_de[0]
        centavos_de_str = f",{partes_de[1]}"
    else:
        reais_de_str = val_de_raw
        centavos_de_str = ",00"

    tam_fonte_reais_de = int(26 * scale)
    c.setFont("Arial-Black", tam_fonte_reais_de)

    x_reais_de = x_base + (14.5 * mm * scale)
    y_reais_de = topo_etiqueta - (66.8 * mm * scale)
    c.drawString(x_reais_de, y_reais_de, reais_de_str)

    largura_reais_de = c.stringWidth(reais_de_str, "Arial-Black", tam_fonte_reais_de)

    tam_fonte_centavos_de = int(17 * scale)
    c.setFont("Arial-Black", tam_fonte_centavos_de)

    x_centavos_de = x_reais_de + largura_reais_de + (0.3 * mm * scale)
    y_centavos_de = topo_etiqueta - (64.0 * mm * scale)
    c.drawString(x_centavos_de, y_centavos_de, centavos_de_str)

    largura_centavos_de = c.stringWidth(centavos_de_str, "Arial-Black", tam_fonte_centavos_de)

    tam_fonte_un_de = int(8 * scale)
    c.setFont("Arial-Black", tam_fonte_un_de)
    x_un_de = x_centavos_de + (largura_centavos_de / 2.0) + (4.0 * mm * scale)
    y_un_de = y_centavos_de - (3.0 * mm * scale)
    c.drawCentredString(x_un_de, y_un_de, item["un"])

    x_inicio_risco = x_reais_de - (0.5 * mm * scale)
    x_fim_risco = x_centavos_de + largura_centavos_de + (0.5 * mm * scale)
    y_inicio_risco = y_reais_de - (0.5 * mm * scale)
    y_fim_risco = y_centavos_de + (3.8 * mm * scale)

    c.setLineWidth(2.0 * scale)
    c.line(x_inicio_risco, y_inicio_risco, x_fim_risco, y_fim_risco)

    tam_fonte_por_rotulo = int(18 * scale)
    c.setFont("Arial-Black", tam_fonte_por_rotulo)

    x_por = x_base + (44.3 * mm * scale)
    y_por = topo_etiqueta - (60.0 * mm * scale)

    x_rs_por = x_base + (46.4 * mm * scale)
    y_rs_por = topo_etiqueta - (67.1 * mm * scale)

    c.drawString(x_por, y_por, "Por")
    c.drawString(x_rs_por, y_rs_por, "R$")

    val_por_raw = item["por"].replace(".", ",")
    if "," in val_por_raw:
        partes_por = val_por_raw.split(",")
        reais_por_str = partes_por[0]
        centavos_por_str = f",{partes_por[1]}"
    else:
        reais_por_str = val_por_raw
        centavos_por_str = ",00"

    tam_fonte_reais_por = int(58 * scale)
    c.setFont("Arial-Black", tam_fonte_reais_por)

    x_reais_por = x_base + (56.6 * mm * scale)
    y_reais_por = topo_etiqueta - (70.5 * mm * scale)
    c.drawString(x_reais_por, y_reais_por, reais_por_str)

    largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

    tam_fonte_centavos_por = int(32 * scale)
    c.setFont("Arial-Black", tam_fonte_centavos_por)

    x_centavos_por = x_reais_por + largura_reais_por + (0.3 * mm * scale)
    y_centavos_por = topo_etiqueta - (65.5 * mm * scale)
    c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

    largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

    tam_fonte_un_por = int(12 * scale)
    c.setFont("Arial-Black", tam_fonte_un_por)
    x_un_por = x_centavos_por + (largura_centavos_por / 2.0) + (4.0 * mm * scale)
    y_un_por = y_centavos_por - (6.0 * mm * scale)
    c.drawCentredString(x_un_por, y_un_por, item["un"])
