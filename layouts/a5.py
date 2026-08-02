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

    # Caixa de texto: Largura total (210mm) - 9mm de margem total (4.5mm esq + 4.5mm dir)
    max_largura_texto = col_w - (9.0 * mm * scale)

    # Distância exata de 62mm a partir da borda superior
    y_primeira_linha = topo_etiqueta - (62.0 * mm * scale)
    desc = item["desc"]

    # Se a descrição inteira couber dentro da caixa de 4.5mm de margem, imprime em 1 linha
    if c.stringWidth(desc, "Arial-Black", tam_fonte_desc) <= max_largura_texto:
        c.drawCentredString(x_center, y_primeira_linha, desc)
    else:
        # Quebra em 2 linhas respeitando o limite físico da caixa de texto
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
        
        # 1. Rótulos "De" e "R$" (Fonte 20pt)
        tam_fonte_de = int(20 * scale)
        c.setFont("Arial-Black", tam_fonte_de)

        x_de = x_base + (28.0 * mm * scale)
        y_de = topo_etiqueta - (93.0 * mm * scale)
        y_rs_de = y_de - (7.5 * mm * scale)

        c.drawString(x_de, y_de, "De")
        c.drawString(x_de, y_rs_de, "R$")

        # Separação Reais e Centavos DE
        val_de_raw = item["de"].replace(".", ",")
        if "," in val_de_raw:
            partes_de = val_de_raw.split(",")
            reais_de_str = partes_de[0]
            centavos_de_str = f",{partes_de[1]}"
        else:
            reais_de_str = val_de_raw
            centavos_de_str = ",00"

        # 2. Reais DE (Fonte 64pt, 43mm abaixo da descrição)
        tam_fonte_reais_de = int(64 * scale)
        c.setFont("Arial-Black", tam_fonte_reais_de)

        largura_rs_de = c.stringWidth("R$", "Arial-Black", tam_fonte_de)
        x_reais_de = x_de + largura_rs_de + (2.0 * mm * scale)
        y_reais_de = y_primeira_linha - (43.0 * mm * scale)
        c.drawString(x_reais_de, y_reais_de, reais_de_str)

        largura_reais_de = c.stringWidth(reais_de_str, "Arial-Black", tam_fonte_reais_de)

        # 3. Centavos DE (Fonte 35pt, 34mm abaixo da descrição, 1.5mm do preço em Reais)
        tam_fonte_centavos_de = int(35 * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_de)

        x_centavos_de = x_reais_de + largura_reais_de + (1.5 * mm * scale)
        y_centavos_de = y_primeira_linha - (34.0 * mm * scale)
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

        # -------------------------------------------------------------------
        # BLOCO "POR" PROMOCIONAL
        # -------------------------------------------------------------------

        # 4. Rótulos "Por" e "R$" (Fonte 30pt)
        tam_fonte_por_rotulo = int(30 * scale)
        c.setFont("Arial-Black", tam_fonte_por_rotulo)

        x_por = x_base + (95.0 * mm * scale)
        y_por = topo_etiqueta - (93.0 * mm * scale)

        x_rs_por = x_por
        y_rs_por = y_por - (11.0 * mm * scale)

        c.drawString(x_por, y_por, "Por")
        c.drawString(x_rs_por, y_rs_por, "R$")

        # Separação Reais e Centavos POR
        val_por_raw = item["por"].replace(".", ",")
        if "," in val_por_raw:
            partes_por = val_por_raw.split(",")
            reais_por_str = partes_por[0]
            centavos_por_str = f",{partes_por[1]}"
        else:
            reais_por_str = val_por_raw
            centavos_por_str = ",00"

        # 5. Reais POR (Fonte 144pt, x=115.9mm)
        tam_fonte_reais_por = int(144 * scale)
        c.setFont("Arial-Black", tam_fonte_reais_por)

        x_reais_por = x_base + (115.9 * mm * scale)
        y_reais_por = y_primeira_linha - (57.0 * mm * scale)
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

        # 6. Centavos POR (Fonte 72pt)
        tam_fonte_centavos_por = int(72 * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_por)

        x_centavos_por = x_reais_por + largura_reais_por + (1.5 * mm * scale)
        y_centavos_por = y_primeira_linha - (38.0 * mm * scale)
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        # Unidade "Por" (Abaixo dos centavos)
        tam_fonte_un_por = int(18 * scale)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
        y_un_por = y_centavos_por - (12.0 * mm * scale)
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    else:
        # --- MODO PREÇO ÚNICO (DINAMICAMENTE CENTRALIZADO) ---
        val_por_raw = item["por"].replace(".", ",")
        if "," in val_por_raw:
            partes_por = val_por_raw.split(",")
            reais_por_str = partes_por[0]
            centavos_por_str = f",{partes_por[1]}"
        else:
            reais_por_str = val_por_raw
            centavos_por_str = ",00"

        if not item["e_rebaixa"]:
            # Preço Único Normal (Sem Rebaixa) -> Fonte 150pt
            tam_fonte_rs = int(32 * scale)
            tam_fonte_reais_por = int(150 * scale)
            tam_fonte_centavos_por = int(75 * scale)
            tam_fonte_un_por = int(20 * scale)

            y_offset_rs = 95.0 * mm * scale
            y_offset_reais = 127.0 * mm * scale
            y_offset_centavos = 105.0 * mm * scale
            dist_un = 12.0 * mm * scale
        else:
            # Preço Único em Rebaixa (Com Validade) -> Fonte 120pt
            tam_fonte_rs = int(28 * scale)
            tam_fonte_reais_por = int(120 * scale)
            tam_fonte_centavos_por = int(60 * scale)
            tam_fonte_un_por = int(18 * scale)

            y_offset_rs = 88.0 * mm * scale
            y_offset_reais = 112.0 * mm * scale
            y_offset_centavos = 95.0 * mm * scale
            dist_un = 10.0 * mm * scale

        # Medição física das larguras
        c.setFont("Arial-Black", tam_fonte_rs)
        largura_rs = c.stringWidth("R$", "Arial-Black", tam_fonte_rs)

        c.setFont("Arial-Black", tam_fonte_reais_por)
        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

        c.setFont("Arial-Black", tam_fonte_centavos_por)
        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        largura_total_bloco = (
            largura_rs
            + (3.0 * mm * scale)
            + largura_reais_por
            + (0.0 * mm * scale)
            + largura_centavos_por
        )

        x_inicio_bloco = x_center - (largura_total_bloco / 2.0)

        x_rs = x_inicio_bloco
        x_reais_por = x_rs + largura_rs + (3.0 * mm * scale)
        x_centavos_por = x_reais_por + largura_reais_por + (0.0 * mm * scale)

        # 1. Desenha R$
        c.setFont("Arial-Black", tam_fonte_rs)
        y_rs = topo_etiqueta - y_offset_rs
        c.drawString(x_rs, y_rs, "R$")

        # 2. Desenha Reais
        c.setFont("Arial-Black", tam_fonte_reais_por)
        y_reais_por = topo_etiqueta - y_offset_reais
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        # 3. Desenha Centavos
        c.setFont("Arial-Black", tam_fonte_centavos_por)
        y_centavos_por = topo_etiqueta - y_offset_centavos
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        # 4. Desenha Unidade
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
        y_un_por = y_centavos_por - dist_un
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    # -------------------------------------------------------------------
    # 3. TARJA / AVISO DE REBAIXA (CAIXA CINZA NO RODAPÉ)
    # -------------------------------------------------------------------
    if item["e_rebaixa"]:
        # Caixa Cinza: 4mm da borda inferior, 12mm de altura, 202mm de largura (respeita margem 4.5mm)
        x_caixa = x_base + (4.5 * mm * scale)
        y_caixa = y_base + (4.5 * mm * scale)
        largura_caixa = col_w - (9.0 * mm * scale)  # 201mm de largura útil
        altura_caixa = 12.0 * mm * scale

        c.setFillColor(HexColor("#CCCCCC"))
        c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, fill=1, stroke=0)

        c.setFillColor(HexColor("#000000"))

        # Validade: Fonte Arial-Black 28pt (no centro da caixa cinza)
        tam_fonte_val = int(28 * scale)
        c.setFont("Arial-Black", tam_fonte_val)
        y_val = y_caixa + (2.5 * mm * scale)
        c.drawCentredString(x_center, y_val, f"VALIDADE: {item['val']}")

        # Mensagem de Aviso em UMA ÚNICA LINHA (Fonte 16pt, logo acima da caixa cinza)
        tam_fonte_aviso = int(20 * scale)
        c.setFont("Arial-Black", tam_fonte_aviso)
        y_aviso = y_caixa + altura_caixa + (3.0 * mm * scale)

        c.drawCentredString(x_center, y_aviso, "PRODUTO PRÓXIMO A DATA DE VENCIMENTO")
