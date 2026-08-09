from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit


def desenhar_inteiro_forcado(c, texto, x_inicial, y, fonte, tamanho):
  x_atual = x_inicial
  c.setFont(fonte, tamanho)
  total_chars = len(texto)

  for i, char in enumerate(texto):
    c.drawString(x_atual, y, char)
    largura_char = c.stringWidth(char, fonte, tamanho)

    if i == total_chars - 1:
      x_atual += largura_char
    elif char == "1":
      x_atual += largura_char * 0.78
    elif i + 1 < total_chars and texto[i + 1] == "1":
      x_atual += largura_char * 0.85
    else:
      x_atual += largura_char

  return x_atual


def calcular_largura_inteiro_forcado(c, texto, fonte, tamanho):
  largura = 0
  total_chars = len(texto)
  for i, char in enumerate(texto):
    l_char = c.stringWidth(char, fonte, tamanho)
    if i == total_chars - 1:
      largura += l_char
    elif char == "1":
      largura += l_char * 0.78
    elif i + 1 < total_chars and texto[i + 1] == "1":
      largura += l_char * 0.85
    else:
      largura += l_char
  return largura


def desenhar_etiqueta_a4(c, item, x_base, y_base, col_w, row_h, scale):
  page_w = col_w
  page_h = row_h

  margem_lateral_geral = 8 * mm
  largura_util_geral = page_w - (2 * margem_lateral_geral)

  # --- 1. DESCRIÇÃO DO PRODUTO (NÃO MUDOU) ---
  y_atual = page_h - (69 * mm)
  tamanho_fonte_desc = 56
  c.setFont("Arial-Black", tamanho_fonte_desc)
  desc = item.get("desc", "")

  linhas_desc = simpleSplit(
      desc, "Arial-Black", tamanho_fonte_desc, largura_util_geral
  )
  for linha in linhas_desc:
    c.drawCentredString(page_w / 2, y_atual, linha)
    y_atual -= tamanho_fonte_desc + 2

  limite_superior_preco = y_atual

  # --- 2. RODAPÉ DE VALIDADE (Abaixado para 8mm da borda) ---
  largura_caixa = 202.3 * mm
  altura_caixa = 22.1 * mm
  x_caixa = (page_w - largura_caixa) / 2
  y_caixa = 8 * mm  # Ajustado para 8mm do fundo

  # Caixa Cinza
  c.setFillColor(lightgrey)
  c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, stroke=0, fill=1)

  # Texto Validade
  val_str = item.get("val", "")
  texto_validade = f"VALIDADE: {val_str}" if val_str else "VALIDADE:"
  f_validade = 46
  c.setFillColor(black)
  c.setFont("Arial-Black", f_validade)
  y_texto_validade = y_caixa + (altura_caixa / 2) - (f_validade / 3)
  c.drawCentredString(page_w / 2, y_texto_validade, texto_validade)

  # Frase Aviso ANVISA
  f_aviso = 44
  margem_aviso = 5.3 * mm
  largura_util_aviso = page_w - (2 * margem_aviso)
  c.setFont("Arial-Black", f_aviso)

  texto_aviso = "PRODUTO PRÓXIMO A DATA DE VENCIMENTO"
  linhas_aviso = simpleSplit(
      texto_aviso, "Arial-Black", f_aviso, largura_util_aviso
  )

  y_linha_aviso = y_caixa + altura_caixa + (3 * mm) + 10
  for linha in reversed(linhas_aviso):
    c.drawCentredString(page_w / 2, y_linha_aviso, linha)
    y_linha_aviso += f_aviso + 2

  limite_inferior_preco = y_linha_aviso

  # --- 3. BLOCO DO PREÇO "DE / POR" (PROMOCIONAL) ---
  de_raw = item.get("de", "0,00").strip().replace(".", ",")
  por_raw = item.get("por", "0,00").strip().replace(".", ",")

  # A) ESTRUTURA DO PREÇO "POR" (INFERIOR - MAIOR)
  if "," in por_raw:
    partes_por = por_raw.split(",")
    por_int, por_cent = partes_por[0], partes_por[1][:2]
  else:
    por_int, por_cent = por_raw, "00"

  num_por = len(por_int)
  if num_por <= 2:
    f_por, f_por_cent, f_por_rs, f_por_un = 200, 95, 38, 24
    folga_por_cent = -30
  elif num_por == 3:
    f_por, f_por_cent, f_por_rs, f_por_un = 160, 75, 32, 20
    folga_por_cent = -24
  else:
    f_por, f_por_cent, f_por_rs, f_un = 130, 60, 28, 18
    folga_por_cent = -18

  w_por_real = (
      calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
      + folga_por_cent
  )
  w_por_cent = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)
  largura_total_por = w_por_real + w_por_cent

  # Posicionamento vertical do bloco
  centro_livre = (limite_superior_preco + limite_inferior_preco) / 2
  y_por_base = centro_livre - 60  # Puxa o 'Por' levemente para baixo
  x_por_inicio = (page_w - largura_total_por) / 2 + 15 * mm

  # R$ Por
  c.setFont("Arial-Black", f_por_rs)
  c.drawString(x_por_inicio - (25 * mm), y_por_base + (f_por * 0.75), "R$")

  # Rótulo "Por" na esquerda
  c.setFont("Arial-Black", 38)
  c.drawString(15 * mm, y_por_base + 10, "Por")

  # Valor Por (Inteiro, Centavos e Unidade)
  x_por_fim = desenhar_inteiro_forcado(
      c, por_int, x_por_inicio, y_por_base, "Arial-Black", f_por
  )
  x_por_cent = x_por_fim + folga_por_cent
  y_por_cent = y_por_base + f_por - f_por_cent - (f_por * 0.12)
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_por_cent, y_por_cent, f",{por_cent}")

  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(
      x_por_cent + (w_por_cent / 2),
      y_por_cent - f_por_un - (6 * mm),
      item.get("un", "1 UN"),
  )

  # B) ESTRUTURA DO PREÇO "DE" (SUPERIOR - MENOR COM RISCO)
  if "," in de_raw:
    partes_de = de_raw.split(",")
    de_int, de_cent = partes_de[0], partes_de[1][:2]
  else:
    de_int, de_cent = de_raw, "00"

  f_de, f_de_cent, f_de_rs, f_de_un = 120, 56, 26, 16
  w_de_real = calcular_largura_inteiro_forcado(
      c, de_int, "Arial-Black", f_de
  ) - 15
  w_de_cent = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)
  largura_total_de = w_de_real + w_de_cent

  y_de_base = y_por_base + f_por + (10 * mm)
  x_de_inicio = x_por_inicio

  # Rótulo "De" na esquerda
  c.setFont("Arial-Black", 38)
  c.drawString(15 * mm, y_de_base + 10, "De")

  # R$ De
  c.setFont("Arial-Black", f_de_rs)
  c.drawString(x_de_inicio - (18 * mm), y_de_base + (f_de * 0.75), "R$")

  # Valor De (Inteiro + Centavos)
  x_de_fim = desenhar_inteiro_forcado(
      c, de_int, x_de_inicio, y_de_base, "Arial-Black", f_de
  )
  x_de_cent = x_de_fim - 15
  y_de_cent = y_de_base + f_de - f_de_cent - (f_de * 0.12)
  c.setFont("Arial-Black", f_de_cent)
  c.drawString(x_de_cent, y_de_cent, f",{de_cent}")

  c.setFont("Arial-Black", f_de_un)
  c.drawCentredString(
      x_de_cent + (w_de_cent / 2),
      y_de_cent - f_de_un - (4 * mm),
      item.get("un", "1 UN"),
  )

  # LINHA DIAGONAL DE RISCO NO PREÇO "DE"
  c.setLineWidth(4)
  c.line(
      x_de_inicio - (18 * mm),
      y_de_base - (5 * mm),
      x_de_cent + w_de_cent + (2 * mm),
      y_de_base + f_de + (5 * mm),
  )
  c.setLineWidth(1)
