from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit

def desenhar_etiqueta_a6(c, item, x_base, y_base, col_w, row_h, scale):
    """Etiqueta A6 - Preço Único, com validade"""

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
    # 2. BLOCO DE PREÇO ÚNICO (DINAMICAMENTE CENTRALIZADO) - Fonte compacta 84pt
    #    (ajustado pra não encostar na tarja de validade no rodapé)
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
    tam_fonte_reais_por = int(84 * scale)
    tam_fonte_centavos_por = int(40 * scale)
    tam_fonte_un_por = int(12 * scale)

    y_offset_rs = 60.0 * mm * scale
    y_offset_reais = 74.5 * mm * scale
    y_offset_centavos = 62.5 * mm * scale
    dist_un = 7.0 * mm * scale

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

    # -------------------------------------------------------------------
    # 3. TARJA / AVISO DE REBAIXA (CAIXA CINZA NO RODAPÉ)
    # -------------------------------------------------------------------
    x_caixa = x_base + (2.0 * mm * scale)
    y_caixa = y_base + (2.0 * mm * scale)
    largura_caixa = col_w - (4.0 * mm * scale)  # antes: 104.4mm fixo — estourava 1.4mm na etiqueta vizinha
    altura_caixa = 8.0 * mm * scale

    c.setFillColor(HexColor("#CCCCCC"))
    c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, fill=1, stroke=0)

    c.setFillColor(HexColor("#000000"))

    tam_fonte_val = int(20 * scale)
    c.setFont("Arial-Black", tam_fonte_val)
    y_val = y_caixa + (1.5 * mm * scale)
    c.drawCentredString(x_center, y_val, f"VALIDADE: {item['val']}")

    tam_fonte_aviso = int(15 * scale)
    c.setFont("Arial-Black", tam_fonte_aviso)
    y_aviso2 = y_caixa + altura_caixa + (2.0 * mm * scale)
    y_aviso1 = y_aviso2 + (5.5 * mm * scale)

    c.drawCentredString(x_center, y_aviso1, "PRODUTO PRÓXIMO")
    c.drawCentredString(x_center, y_aviso2, "A DATA DE VENCIMENTO")
