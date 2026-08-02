from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

def desenhar_etiqueta_a6(c, item, x_base, y_base, col_w, row_h, scale):
    """Desenha a etiqueta com precisão milimétrica para o modelo A6 Vertical"""

    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h  # Borda superior de cada etiqueta (0 a 99mm)

    # -------------------------------------------------------------------
    # 1. DESCRIÇÃO DO PRODUTO (Margem exata de 2mm em cada lado = 4mm total)
    # -------------------------------------------------------------------
    tam_fonte_desc = int(16 * scale)
    c.setFont("Arial-Black", tam_fonte_desc)

    # Caixa de texto: Largura total da etiqueta - 4mm de margem total (2mm esq + 2mm dir)
    max_largura_texto = col_w - (4.0 * mm * scale)

    y_primeira_linha = topo_etiqueta - (40.8 * mm * scale)
    desc = item["desc"]

    # Se a descrição inteira couber dentro da caixa de 2mm de margem, imprime em 1 linha
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

        espacamento_linhas = (tam_fonte_desc * 0.35 + 1.8) * mm
        y_segunda_linha = y_primeira_linha - espacamento_linhas

        c.drawCentredString(x_center, y_primeira_linha, linha1)
        c.drawCentredString(x_center, y_segunda_linha, linha2)

    # -------------------------------------------------------------------
    # 2. BLOCO DE PREÇOS ("DE / POR" OU "PREÇO ÚNICO")
    # -------------------------------------------------------------------
    if item["de"]:
        # --- MODO PROMOCIONAL (DE / POR) ---
        
        # Rótulo "De" e "R$" (Afastados 2mm para a esquerda)
        tam_fonte_de = int(12 * scale)
        c.setFont("Arial-Black", tam_fonte_de)

        x_de = x_base + (7.2 * mm * scale)
        y_de = topo_etiqueta - (62.2 * mm * scale)
        y_rs_de = topo_etiqueta - (66.5 * mm * scale)

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

        # Reais DE
        tam_fonte_reais_de = int(26 * scale)
        c.setFont("Arial-Black", tam_fonte_reais_de)

        x_reais_de = x_base + (14.5 * mm * scale)
        y_reais_de = topo_etiqueta - (66.8 * mm * scale)
        c.drawString(x_reais_de, y_reais_de, reais_de_str)

        largura_reais_de = c.stringWidth(reais_de_str, "Arial-Black", tam_fonte_reais_de)

        # Centavos DE
        tam_fonte_centavos_de = int(17 * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_de)

        x_centavos_de = x_reais_de + largura_reais_de + (0.3 * mm * scale)
        y_centavos_de = topo_etiqueta - (64.0 * mm * scale)
        c.drawString(x_centavos_de, y_centavos_de, centavos_de_str)

        largura_centavos_de = c.stringWidth(centavos_de_str, "Arial-Black", tam_fonte_centavos_de)

        # Unidade "De"
        tam_fonte_un_de = int(8 * scale)
        c.setFont("Arial-Black", tam_fonte_un_de)
        x_un_de = x_centavos_de + (largura_centavos_de / 2.0) + (4.0 * mm * scale)
        y_un_de = y_centavos_de - (3.0 * mm * scale)
        c.drawCentredString(x_un_de, y_un_de, item["un"])

        # Risco Diagonal DE
        x_inicio_risco = x_reais_de - (0.5 * mm * scale)
        x_fim_risco = x_centavos_de + largura_centavos_de + (0.5 * mm * scale)

        y_inicio_risco = y_reais_de - (0.5 * mm * scale)
        y_fim_risco = y_centavos_de + (3.8 * mm * scale)

        c.setLineWidth(2.0 * scale)
        c.line(x_inicio_risco, y_inicio_risco, x_fim_risco, y_fim_risco)

        # Rótulos "Por" e "R$" (Afastados 2mm para a esquerda)
        tam_fonte_por_rotulo = int(18 * scale)
        c.setFont("Arial-Black", tam_fonte_por_rotulo)

        x_por = x_base + (44.3 * mm * scale)
        y_por = topo_etiqueta - (60.0 * mm * scale)

        x_rs_por = x_base + (46.4 * mm * scale)
        y_rs_por = topo_etiqueta - (67.1 * mm * scale)

        c.drawString(x_por, y_por, "Por")
        c.drawString(x_rs_por, y_rs_por, "R$")

        # Preço POR
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

        # Unidade "Por"
        tam_fonte_un_por = int(12 * scale)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0) + (4.0 * mm * scale)
        y_un_por = y_centavos_por - (6.0 * mm * scale)
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

        # Fontes definidas: R$ 20pt | Reais 84pt | Centavos 40pt
        tam_fonte_rs = int(20 * scale)
        tam_fonte_reais_por = int(84 * scale)
        tam_fonte_centavos_por = int(40 * scale)
        tam_fonte_un_por = int(12 * scale)

        # Medição física das larguras
        c.setFont("Arial-Black", tam_fonte_rs)
        largura_rs = c.stringWidth("R$", "Arial-Black", tam_fonte_rs)

        c.setFont("Arial-Black", tam_fonte_reais_por)
        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

        c.setFont("Arial-Black", tam_fonte_centavos_por)
        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        # Largura total: R$ + 2mm + REAIS + 1mm + CENTAVOS
        largura_total_bloco = (
            largura_rs
            + (2.0 * mm * scale)
            + largura_reais_por
            + (1.0 * mm * scale)
            + largura_centavos_por
        )

        # Ponto X inicial para centralizar perfeitamente no meio da etiqueta
        x_inicio_bloco = x_center - (largura_total_bloco / 2.0)

        # Posições X encadeadas
        x_rs = x_inicio_bloco
        x_reais_por = x_rs + largura_rs + (2.0 * mm * scale)
        x_centavos_por = x_reais_por + largura_reais_por + (1.0 * mm * scale)

        # 1. Desenha R$ (20pt)
        c.setFont("Arial-Black", tam_fonte_rs)
        y_rs = topo_etiqueta - (66.0 * mm * scale)
        c.drawString(x_rs, y_rs, "R$")

        # 2. Desenha Reais (84pt)
        c.setFont("Arial-Black", tam_fonte_reais_por)
        y_reais_por = topo_etiqueta - (70.5 * mm * scale)
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        # 3. Desenha Centavos (40pt)
        c.setFont("Arial-Black", tam_fonte_centavos_por)
        y_centavos_por = topo_etiqueta - (58.5 * mm * scale)
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        # 4. Desenha Unidade (12pt - abaixo dos centavos)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0)
        y_un_por = y_centavos_por - (7.0 * mm * scale)
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    # -------------------------------------------------------------------
    # 3. TARJA / AVISO DE REBAIXA (CAIXA CINZA NO RODAPÉ)
    # -------------------------------------------------------------------
    if item["e_rebaixa"]:
        # Caixa Cinza (#CCCCCC): 2mm da borda inferior, 8mm de altura, 104.4mm de largura
        x_caixa = x_base + (2.0 * mm * scale)
        y_caixa = y_base + (2.0 * mm * scale)
        largura_caixa = 104.4 * mm * scale
        altura_caixa = 8.0 * mm * scale

        # Desenha o retângulo preenchido
        c.setFillColor(HexColor("#CCCCCC"))
        c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, fill=1, stroke=0)

        # Cor do texto em Preto (#000000)
        c.setFillColor(HexColor("#000000"))

        # Validade: Fonte Arial-Black 20pt
        tam_fonte_val = int(20 * scale)
        c.setFont("Arial-Black", tam_fonte_val)
        y_val = y_caixa + (1.5 * mm * scale)
        c.drawCentredString(x_center, y_val, f"VALIDADE: {item['val']}")

        # Mensagem de Aviso: Fonte Arial-Black 15pt (Logo acima da caixa cinza)
        tam_fonte_aviso = int(15 * scale)
        c.setFont("Arial-Black", tam_fonte_aviso)
        y_aviso2 = y_caixa + altura_caixa + (2.0 * mm * scale)
        y_aviso1 = y_aviso2 + (5.5 * mm * scale)

        c.drawCentredString(x_center, y_aviso1, "PRODUTO PRÓXIMO")
        c.drawCentredString(x_center, y_aviso2, "A DATA DE VENCIMENTO")
