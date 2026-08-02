from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

def desenhar_etiqueta_a5(c, item, x_base, y_base, col_w, row_h, scale):
    """Desenha a etiqueta com precisão milimétrica para o modelo A5 Vertical (2 por A4)"""

    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h  # Borda superior de cada etiqueta (0 a 148.5mm)

    # -------------------------------------------------------------------
    # 1. DESCRIÇÃO DO PRODUTO (Margem exata de 4.5mm em cada lado = 9mm total)
    # -------------------------------------------------------------------
    tam_fonte_desc = int(36 * scale)
    c.setFont("Arial-Black", tam_fonte_desc)

    max_largura_texto = col_w - (9.0 * mm * scale)
    y_primeira_linha = topo_etiqueta - (62.0 * mm * scale)
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

        espacamento_linhas = (tam_fonte_desc * 0.35 + 3.0) * mm
        y_segunda_linha = y_primeira_linha - espacamento_linhas

        c.drawCentredString(x_center, y_primeira_linha, linha1)
        c.drawCentredString(x_center, y_segunda_linha, linha2)

    # -------------------------------------------------------------------
    # 2. BLOCO DE PREÇOS ("DE / POR" OU "PREÇO ÚNICO")
    # -------------------------------------------------------------------
    if item["de"]:
        # --- MODO PROMOCIONAL (DE / POR) ---
        
        val_de_raw = item["de"].replace(".", ",")
        if "," in val_de_raw:
            partes_de = val_de_raw.split(",")
            reais_de_str = partes_de[0]
            centavos_de_str = f",{partes_de[1]}"
        else:
            reais_de_str = val_de_raw
            centavos_de_str = ",00"

        num_digitos_de = len(reais_de_str)

        if num_digitos_de <= 1:
            x_de_pos = 28.0
            fonte_reais_de = 64
            fonte_centavos_de = 35
            offset_y_reais_de = 43.0
            offset_y_centavos_de = 34.0
        elif num_digitos_de == 2:
            x_de_pos = 14.0
            fonte_reais_de = 52
            fonte_centavos_de = 28
            offset_y_reais_de = 41.0
            offset_y_centavos_de = 34.0
        else:
            x_de_pos = 8.0
            fonte_reais_de = 40
            fonte_centavos_de = 22
            offset_y_reais_de = 39.0
            offset_y_centavos_de = 32.0

        # Rótulos "De" e "R$"
        tam_fonte_de = int(20 * scale)
        c.setFont("Arial-Black", tam_fonte_de)

        x_de = x_base + (x_de_pos * mm * scale)
        y_de = topo_etiqueta - (93.0 * mm * scale)
        y_rs_de = y_de - (7.5 * mm * scale)

        c.drawString(x_de, y_de, "De")
        c.drawString(x_de, y_rs_de, "R$")

        # Reais DE
        tam_fonte_reais_de = int(fonte_reais_de * scale)
        c.setFont("Arial-Black", tam_fonte_reais_de)

        largura_rs_de = c.stringWidth("R$", "Arial-Black", tam_fonte_de)
        x_reais_de = x_de + largura_rs_de + (2.0 * mm * scale)
        y_reais_de = y_primeira_linha - (offset_y_reais_de * mm * scale)
        c.drawString(x_reais_de, y_reais_de, reais_de_str)

        largura_reais_de = c.stringWidth(reais_de_str, "Arial-Black", tam_fonte_reais_de)

        # Centavos DE
        tam_fonte_centavos_de = int(fonte_centavos_de * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_de)

        x_centavos_de = x_reais_de + largura_reais_de + (1.5 * mm * scale)
        y_centavos_de = y_primeira_linha - (offset_y_centavos_de * mm * scale)
        c.drawString(x_centavos_de, y_centavos_de, centavos_de_str)

        largura_centavos_de = c.stringWidth(centavos_de_str, "Arial-Black", tam_fonte_centavos_de)

        # Unidade "De"
        tam_fonte_un_de = int(12 * scale)
        c.setFont("Arial-Black", tam_fonte_un_de)
        x_un_de = x_centavos_de + (largura_centavos_de / 2.0) + (5.0 * mm * scale)
        y_un_de = y_centavos_de - (5.0 * mm * scale)
        c.drawCentredString(x_un_de, y_un_de, item["un"])

        # Risco Diagonal DE
        x_inicio_risco = x_reais_de - (1.0 * mm * scale)
        x_fim_risco = x_centavos_de + largura_centavos_de + (1.0 * mm * scale)
        y_inicio_risco = y_reais_de - (1.0 * mm * scale)
        y_fim_risco = y_centavos_de + (6.0 * mm * scale)

        c.setLineWidth(3.0 * scale)
        c.line(x_inicio_risco, y_inicio_risco, x_fim_risco, y_fim_risco)

        # Bloco "POR" Promocional
        val_por_raw = item["por"].replace(".", ",")
        if "," in val_por_raw:
            partes_por = val_por_raw.split(",")
            reais_por_str = partes_por[0]
            centavos_por_str = f",{partes_por[1]}"
        else:
            reais_por_str = val_por_raw
            centavos_por_str = ",00"

        num_digitos_reais = len(reais_por_str)

        if num_digitos_reais <= 1:
            fonte_reais = 144
            fonte_centavos = 72
            offset_y_reais = 57.0
            offset_y_centavos = 38.0
        elif num_digitos_reais == 2:
            fonte_reais = 110
            fonte_centavos = 55
            offset_y_reais = 52.0
            offset_y_centavos = 38.0
        else:
            fonte_reais = 85
            fonte_centavos = 42
            offset_y_reais = 46.0
            offset_y_centavos = 38.0

        tam_fonte_reais_por = int(fonte_reais * scale)
        tam_fonte_centavos_por = int(fonte_centavos * scale)

        tam_fonte_por_rotulo = int(30 * scale)
        c.setFont("Arial-Black", tam_fonte_por_rotulo)

        x_por = x_base + ((90.0 if num_digitos_reais >= 2 else 95.0) * mm * scale)
        y_por = topo_etiqueta - (93.0 * mm * scale)
        x_rs_por = x_por
        y_rs_por = y_por - (11.0 * mm * scale)

        c.drawString(x_por, y_por, "Por")
        c.drawString(x_rs_por, y_rs_por, "R$")

        c.setFont("Arial-Black", tam_fonte_reais_por)
        x_reais_por = x_por + (20.9 * mm * scale)
        y_reais_por = y_primeira_linha - (offset_y_reais * mm * scale)
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

        c.setFont("Arial-Black", tam_fonte_centavos_por)
        x_centavos_por = x_reais_por + largura_reais_por + (1.5 * mm * scale)
        y_centavos_por = y_primeira_linha - (offset_y_centavos * mm * scale)
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        tam_fonte_un_por = int(18 * scale)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
        y_un_por = y_centavos_por - (12.0 * mm * scale)
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    else:
        # --- MODO PREÇO ÚNICO INTELIGENTE (COM AJUSTE AUTOMÁTICO DE MARGEM) ---
        val_por_raw = item["por"].replace(".", ",")
        if "," in val_por_raw:
            partes_por = val_por_raw.split(",")
            reais_por_str = partes_por[0]
            centavos_por_str = f",{partes_por[1]}"
        else:
            reais_por_str = val_por_raw
            centavos_por_str = ",00"

        num_digitos_reais = len(reais_por_str)

        # Seleção de tamanhos iniciais com base na quantidade de dígitos
        if num_digitos_reais <= 1:
            fonte_reais = 144
            fonte_centavos = 72
            offset_y_reais = 57.0
            offset_y_centavos = 38.0
        elif num_digitos_reais == 2:
            fonte_reais = 110
            fonte_centavos = 55
            offset_y_reais = 52.0
            offset_y_centavos = 38.0
        else:  # 3 ou mais dígitos (ex: 111,97)
            fonte_reais = 80
            fonte_centavos = 40
            offset_y_reais = 46.0
            offset_y_centavos = 38.0

        tam_fonte_rs = int(30 * scale)
        tam_fonte_reais_por = int(fonte_reais * scale)
        tam_fonte_centavos_por = int(fonte_centavos * scale)
        tam_fonte_un_por = int(20 * scale)

        # Verificação de segurança de largura máxima permitida na etiqueta
        # Largura útil total da etiqueta menos 9mm de margem total (4.5mm de cada lado)
        largura_util_maxima = col_w - (9.0 * mm * scale)

        # Loop de segurança: se a largura total calculada ultrapassar o limite da etiqueta, reduz o tamanho proporcionalmente
        while True:
            c.setFont("Arial-Black", tam_fonte_rs)
            largura_rs = c.stringWidth("R$", "Arial-Black", tam_fonte_rs)

            c.setFont("Arial-Black", tam_fonte_reais_por)
            largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

            c.setFont("Arial-Black", tam_fonte_centavos_por)
            largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

            largura_total_bloco = (
                largura_rs
                + (4.0 * mm * scale)
                + largura_reais_por
                + (1.5 * mm * scale)
                + largura_centavos_por
            )

            # Se coube na largura útil ou se a fonte já chegou num limite seguro mínimo, sai do loop
            if largura_total_bloco <= largura_util_maxima or tam_fonte_reais_por <= 50:
                break

            # Se ainda estiver passando, reduz um pouco os tamanhos das fontes e tenta de novo
            tam_fonte_reais_por = int(tam_fonte_reais_por * 0.90)
            tam_fonte_centavos_por = int(tam_fonte_centavos_por * 0.90)
            tam_fonte_rs = int(tam_fonte_rs * 0.90)

        # Posicionamento centralizado dinâmico com a largura final garantida
        x_inicio_bloco = x_center - (largura_total_bloco / 2.0)

        x_rs = x_inicio_bloco
        x_reais_por = x_rs + largura_rs + (4.0 * mm * scale)
        x_centavos_por = x_reais_por + largura_reais_por + (1.5 * mm * scale)

        y_rs = y_primeira_linha - (34.0 * mm * scale)
        y_reais_por = y_primeira_linha - (offset_y_reais * mm * scale)
        y_centavos_por = y_primeira_linha - (offset_y_centavos * mm * scale)

        # 1. Desenha R$
        c.setFont("Arial-Black", tam_fonte_rs)
        c.drawString(x_rs, y_rs, "R$")

        # 2. Desenha Reais
        c.setFont("Arial-Black", tam_fonte_reais_por)
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        # 3. Desenha Centavos
        c.setFont("Arial-Black", tam_fonte_centavos_por)
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        # 4. Desenha Unidade (abaixo dos centavos)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
        y_un_por = y_centavos_por - (12.0 * mm * scale)
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    # -------------------------------------------------------------------
    # 3. TARJA / AVISO DE REBAIXA (CAIXA CINZA NO RODAPÉ)
    # -------------------------------------------------------------------
    if item["e_rebaixa"]:
        x_caixa = x_base + (4.5 * mm * scale)
        y_caixa = y_base + (4.5 * mm * scale)
        largura_caixa = col_w - (9.0 * mm * scale)
        altura_caixa = 12.0 * mm * scale

        c.setFillColor(HexColor("#CCCCCC"))
        c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, fill=1, stroke=0)

        c.setFillColor(HexColor("#000000"))

        tam_fonte_val = int(34 * scale)
        c.setFont("Arial-Black", tam_fonte_val)
        y_val = y_caixa + (2.5 * mm * scale)
        c.drawCentredString(x_center, y_val, f"VALIDADE: {item['val']}")

        tam_fonte_aviso = int(20 * scale)
        c.setFont("Arial-Black", tam_fonte_aviso)
        y_aviso = y_caixa + altura_caixa + (3.0 * mm * scale)

        c.drawCentredString(x_center, y_aviso, "PRODUTO PRÓXIMO A DATA DE VENCIMENTO")
