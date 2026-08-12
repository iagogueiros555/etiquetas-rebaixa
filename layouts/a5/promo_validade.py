from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit

def desenhar_etiqueta_a5(c, item, x_base, y_base, col_w, row_h, scale):
    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h

    # --- 1. DESCRIÇÃO DO PRODUTO (mesma altura e mesma lógica da etiqueta unitária) ---
    tam_fonte_desc = int(36 * scale)
    max_largura_texto = col_w - (9.0 * mm * scale)
    y_primeira_linha = topo_etiqueta - (72.0 * mm * scale)  # antes: 62mm — descia perto demais da barra vermelha
    desc = item.get("desc", "")

    # Vai diminuindo de 1 em 1 ponto (nunca de forma abrupta) até caber em no máximo 2 linhas
    linhas_desc = []
    while tam_fonte_desc > 10:
        c.setFont("Arial-Black", tam_fonte_desc)
        linhas_desc = simpleSplit(desc, "Arial-Black", tam_fonte_desc, max_largura_texto)
        if len(linhas_desc) <= 2:
            break
        tam_fonte_desc -= 1

    linhas_desc = linhas_desc[:2]  # trava de segurança: nunca desenha uma 3ª linha
    c.setFont("Arial-Black", tam_fonte_desc)
    espacamento_desc = (tam_fonte_desc * 0.35 + 3.0) * mm * scale

    y_linha_atual = y_primeira_linha
    for linha in linhas_desc:
        c.drawCentredString(x_center, y_linha_atual, linha)
        y_linha_atual -= espacamento_desc

    # --- 2. OFFSETS CENTRAIS (Com Rebaixa - Bloco elevado) ---
    offset_base_de_y = 100.0
    offset_reais_padrao = 50.0   # antes: 59.0 — reduzido pra não bater no aviso fixo de validade
    offset_centavos_padrao = 37.0  # antes: 45.0

    # --- 3. BLOCO "DE" ---
    val_de_raw = item.get("de", "").replace(".", ",")
    if "," in val_de_raw:
        reais_de_str, centavos_de_str = val_de_raw.split(",")[0], f",{val_de_raw.split(',')[1]}"
    else:
        reais_de_str, centavos_de_str = val_de_raw, ",00"

    num_digitos_de = len(reais_de_str)
    if num_digitos_de <= 1:
        x_de_pos, fonte_reais_de, fonte_centavos_de = 28.0, 58, 32
        offset_y_reais_de, offset_y_centavos_de = offset_reais_padrao - 11.0, offset_centavos_padrao - 5.0
    elif num_digitos_de == 2:
        x_de_pos, fonte_reais_de, fonte_centavos_de = 14.0, 47, 25
        offset_y_reais_de, offset_y_centavos_de = offset_reais_padrao - 13.0, offset_centavos_padrao - 5.0
    else:
        x_de_pos, fonte_reais_de, fonte_centavos_de = 8.0, 36, 20
        offset_y_reais_de, offset_y_centavos_de = offset_reais_padrao - 15.0, offset_centavos_padrao - 7.0

    tam_fonte_de = int(20 * scale)
    c.setFont("Arial-Black", tam_fonte_de)
    x_de = x_base + (x_de_pos * mm * scale)
    y_de = topo_etiqueta - (offset_base_de_y * mm * scale)
    c.drawString(x_de, y_de, "De")
    c.drawString(x_de, y_de - (7.5 * mm * scale), "R$")

    tam_fonte_reais_de = int(fonte_reais_de * scale)
    c.setFont("Arial-Black", tam_fonte_reais_de)
    x_reais_de = x_de + c.stringWidth("R$", "Arial-Black", tam_fonte_de) + (2.0 * mm * scale)
    y_reais_de = y_primeira_linha - (offset_y_reais_de * mm * scale)
    c.drawString(x_reais_de, y_reais_de, reais_de_str)

    tam_fonte_centavos_de = int(fonte_centavos_de * scale)
    c.setFont("Arial-Black", tam_fonte_centavos_de)
    largura_reais_de = c.stringWidth(reais_de_str, "Arial-Black", tam_fonte_reais_de)
    x_centavos_de = x_reais_de + largura_reais_de + (0.6 * mm * scale)
    y_centavos_de = y_primeira_linha - (offset_y_centavos_de * mm * scale)
    c.drawString(x_centavos_de, y_centavos_de, centavos_de_str)

    tam_fonte_un_de = int(12 * scale)
    c.setFont("Arial-Black", tam_fonte_un_de)
    x_un_de = x_centavos_de + (c.stringWidth(centavos_de_str, "Arial-Black", tam_fonte_centavos_de) / 2.0) + (5.0 * mm * scale)
    c.drawCentredString(x_un_de, y_centavos_de - (5.0 * mm * scale), item.get("un", ""))

    c.setLineWidth(3.0 * scale)
    c.line(x_reais_de - (1.0 * mm * scale), y_reais_de - (1.0 * mm * scale), 
           x_centavos_de + c.stringWidth(centavos_de_str, "Arial-Black", tam_fonte_centavos_de) + (1.0 * mm * scale), 
           y_centavos_de + (6.0 * mm * scale))

    # --- 4. BLOCO "POR" ---
    val_por_raw = item.get("por", "").replace(".", ",")
    if "," in val_por_raw:
        reais_por_str, centavos_por_str = val_por_raw.split(",")[0], f",{val_por_raw.split(',')[1]}"
    else:
        reais_por_str, centavos_por_str = val_por_raw, ",00"

    num_digitos_reais = len(reais_por_str)
    if num_digitos_reais <= 1:
        fonte_reais, fonte_centavos = 128, 64
        offset_y_reais, offset_y_centavos = offset_reais_padrao, offset_centavos_padrao
    elif num_digitos_reais == 2:
        fonte_reais, fonte_centavos = 98, 50
        offset_y_reais, offset_y_centavos = offset_reais_padrao - 5.0, offset_centavos_padrao
    else:
        fonte_reais, fonte_centavos = 76, 38
        offset_y_reais, offset_y_centavos = offset_reais_padrao - 11.0, offset_centavos_padrao

    tam_fonte_por_rotulo = int(30 * scale)
    c.setFont("Arial-Black", tam_fonte_por_rotulo)
    x_por = x_base + ((90.0 if num_digitos_reais >= 2 else 95.0) * mm * scale)
    y_por = topo_etiqueta - (offset_base_de_y * mm * scale) - (4.0 * mm * scale)  # um pouco mais baixo que o "De", só pra dar folga
    c.drawString(x_por, y_por, "Por")
    c.drawString(x_por, y_por - (11.0 * mm * scale), "R$")

    tam_fonte_reais_por = int(fonte_reais * scale)
    c.setFont("Arial-Black", tam_fonte_reais_por)
    x_reais_por = x_por + (20.9 * mm * scale)
    y_reais_por = y_primeira_linha - (offset_y_reais * mm * scale)
    c.drawString(x_reais_por, y_reais_por, reais_por_str)

    tam_fonte_centavos_por = int(fonte_centavos * scale)
    c.setFont("Arial-Black", tam_fonte_centavos_por)
    x_centavos_por = x_reais_por + c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por) + (0.6 * mm * scale)
    y_centavos_por = y_primeira_linha - (offset_y_centavos * mm * scale)
    c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

    tam_fonte_un_por = int(18 * scale)
    c.setFont("Arial-Black", tam_fonte_un_por)
    x_un_por = x_centavos_por + (c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por) / 2.0)
    c.drawCentredString(x_un_por, y_centavos_por - (12.0 * mm * scale), item.get("un", ""))

    # --- 5. TARJA DE VALIDADE (CAIXA CINZA) ---
    x_caixa = x_base + (4.5 * mm * scale)
    y_caixa = y_base + (4.5 * mm * scale)
    largura_caixa = col_w - (9.0 * mm * scale)
    altura_caixa = 12.0 * mm * scale

    c.setFillColor(HexColor("#CCCCCC"))
    c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, fill=1, stroke=0)
    c.setFillColor(HexColor("#000000"))

    c.setFont("Arial-Black", int(34 * scale))
    c.drawCentredString(x_center, y_caixa + (2.5 * mm * scale), f"VALIDADE: {item.get('val', '')}")

    c.setFont("Arial-Black", int(20 * scale))
    c.drawCentredString(x_center, y_caixa + altura_caixa + (3.0 * mm * scale), "PRODUTO PRÓXIMO A DATA DE VENCIMENTO")
