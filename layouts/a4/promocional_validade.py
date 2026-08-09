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

  # Margem estática padrão alinhada com as frases
  x_margem_estatica = 8 * mm
  largura_util_geral = page_w - (2 * x_margem_estatica)

  # --- 1. DESCRIÇÃO DO PRODUTO ---
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

  limite_superior_preco = y_atual  # Ponto mais baixo da descrição

  # --- 2. RODAPÉ DE VALIDADE (ESTÁTICO A 8MM DO FUNDO) ---
  largura_caixa = 202.3 * mm
  altura_caixa = 22.1 * mm
  x_caixa = (page_w - largura_caixa) / 2
  y_caixa = 8 * mm

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

  limite_inferior_preco = y_linha_aviso  # Ponto mais alto do aviso legal

  # --- 3. ÂNCORAS VERTICAIS ESTÁTICAS PARA O "DE" E O "POR" ---
  # Define posições verticais fixas cravadas entre a descrição e o aviso legal
  y_linha_de = limite_superior_preco - 45 * mm
  y_linha_por = limite_inferior_preco + 25 * mm

  # RÓTULOS ESTÁTICOS ALINHADOS À ESQUERDA
  f_rotulo = 42
  c.setFont("Arial-Black", f_rotulo)
  c.drawString(x_margem_estatica, y_linha_de, "De")
  c.drawString(x_margem_estatica, y_linha_por, "Por")

  # --- 4. PREÇO "DE" (SUPERIOR - MENOR COM RISCO) ---
  de_raw = item.get("de", "0,00").strip().replace(".", ",")
  if "," in de_raw:
    de_int, de_cent = de_raw.split(",")[0], de_raw.split(",")[1][:2]
  else:
    de_int, de_cent = de_raw, "00"

  num_de = len(de_int)
  if num_de <= 2:
    f_de, f_de_cent, f_de_rs, f_de_un = 100, 48, 28, 18
  elif num_de == 3:
    f_de, f_de_cent, f_de_rs, f_de_un = 85, 42, 24, 16
  else:
    f_de, f_de_cent, f_de_rs, f_de_un = 70, 35, 20, 14

  x_inicio_de_valores = x_margem_estatica + 35 * mm

  # R$ De
  c.setFont("Arial-Black", f_de_rs)
  c.drawString(x_inicio_de_valores, y_linha_de + (f_de * 0.65), "R$")

  # Valor De
  x_de_num = x_inicio_de_valores + 18 * mm
  x_de_fim = desenhar_inteiro_forcado(
      c, de_int, x_de_num, y_linha_de, "Arial-Black", f_de
  )

  # Centavos De
  x_de_cent = x_de_fim - 8
  y_de_cent = y_linha_de + f_de - f_de_cent - (f_de * 0.12)
  c.setFont("Arial-Black", f_de_cent)
  c.drawString(x_de_cent, y_de_cent, f",{de_cent}")

  w_de_cent = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)
  c.setFont("Arial-Black", f_de_un)
  c.drawCentredString(
      x_de_cent + (w_de_cent / 2),
      y_de_cent - f_de_un - (4 * mm),
      item.get("un", "1 UN"),
  )

  # Risco no "De"
  c.setLineWidth(4)
  c.line(
      x_inicio_de_valores,
      y_linha_de - 2 * mm,
      x_de_cent + w_de_cent + 2 * mm,
      y_linha_de + f_de + 2 * mm,
  )
  c.setLineWidth(1)

  # --- 5. PREÇO "POR" (INFERIOR - DESTAQUE) ---
  por_raw = item.get("por", "0,00").strip().replace(".", ",")
  if "," in por_raw:
    por_int, por_cent = por_raw.split(",")[0], por_raw.split(",")[1][:2]
  else:
    por_int, por_cent = por_raw, "00"

  num_por = len(por_int)
  if num_por <= 2:
    f_por, f_por_cent, f_por_rs, f_por_un = 180, 85, 38, 26
    folga_por_cent = -26
  elif num_por == 3:
    f_por, f_por_cent, f_por_rs, f_por_un = 145, 68, 32, 22
    folga_por_cent = -20
  else:
    f_por, f_por_cent, f_por_rs, f_por_un = 115, 54, 26, 18
    folga_por_cent = -16

  x_inicio_por_valores = x_margem_estatica + 35 * mm

  # R$ Por
  c.setFont("Arial-Black", f_por_rs)
  c.drawString(x_inicio_por_valores, y_linha_por + (f_por * 0.75), "R$")

  # Valor Por
  x_por_num = x_inicio_por_valores + 22 * mm
  x_por_fim = desenhar_inteiro_forcado(
      c, por_int, x_por_num, y_linha_por, "Arial-Black", f_por
  )

  # Centavos Por
  x_por_cent = x_por_fim + folga_por_cent
  y_por_cent = y_linha_por + f_por - f_por_cent - (f_por * 0.12)
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_por_cent, y_por_cent, f",{por_cent}")

  w_por_cent = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)
  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(
      x_por_cent + (w_por_cent / 2),
      y_por_cent - f_por_un - (6 * mm),
      item.get("un", "1 UN"),
  )
