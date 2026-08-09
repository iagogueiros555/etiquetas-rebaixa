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

  limite_superior_preco = y_atual

  # --- 2. RODAPÉ DE VALIDADE (8MM DO FUNDO) ---
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

  limite_inferior_preco = y_linha_aviso

  # --- 3. DADOS DO PREÇO "POR" ---
  por_raw = item.get("por", "0,00").strip().replace(".", ",")
  if "," in por_raw:
    por_int, por_cent = por_raw.split(",")[0], por_raw.split(",")[1][:2]
  else:
    por_int, por_cent = por_raw, "00"

  num_por = len(por_int)
  if num_por <= 2:
    f_por, f_por_cent, f_por_rs, f_por_un = 170, 80, 36, 24
    folga_por_cent = -26
  elif num_por == 3:
    f_por, f_por_cent, f_por_rs, f_por_un = 140, 66, 32, 22
    folga_por_cent = -20
  else:
    f_por, f_por_cent, f_por_rs, f_por_un = 110, 52, 26, 18
    folga_por_cent = -16

  w_por_real = (
      calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
      + folga_por_cent
  )
  w_por_cent = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)
  largura_bloco_por = (
      c.stringWidth("Por ", "Arial-Black", 40)
      + c.stringWidth("R$ ", "Arial-Black", f_por_rs)
      + w_por_real
      + w_por_cent
  )

  # --- 4. DADOS DO PREÇO "DE" ---
  de_raw = item.get("de", "0,00").strip().replace(".", ",")
  if "," in de_raw:
    de_int, de_cent = de_raw.split(",")[0], de_raw.split(",")[1][:2]
  else:
    de_int, de_cent = de_raw, "00"

  f_de, f_de_cent, f_de_rs, f_de_un = 80, 38, 22, 14
  w_de_real = calcular_largura_inteiro_forcado(c, de_int, "Arial-Black", f_de)
  w_de_cent = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)
  largura_bloco_de = (
      c.stringWidth("De ", "Arial-Black", 40)
      + c.stringWidth("R$ ", "Arial-Black", f_de_rs)
      + w_de_real
      + w_de_cent
  )

  # --- 5. CENTRALIZAÇÃO E POSICIONAMENTO ---
  y_linha_por = limite_inferior_preco + 10 * mm
  y_linha_de = y_linha_por + f_por + 10 * mm

  # Centraliza o bloco principal ("Por") horizontalmente
  x_inicio_conjunto = (page_w - largura_bloco_por) / 2

  f_rotulo = 40
  c.setFont("Arial-Black", f_rotulo)

  # --- A) DESENHA O "DE" ---
  x_de_rotulo = (page_w - largura_bloco_de) / 2
  c.drawString(x_de_rotulo, y_linha_de + 5, "De")

  x_inicio_de = x_de_rotulo + c.stringWidth("De ", "Arial-Black", f_rotulo)
  c.setFont("Arial-Black", f_de_rs)
  c.drawString(x_inicio_de, y_linha_de + (f_de * 0.65), "R$")

  x_de_num = x_inicio_de + c.stringWidth("R$ ", "Arial-Black", f_de_rs)
  x_de_fim = desenhar_inteiro_forcado(
      c, de_int, x_de_num, y_linha_de, "Arial-Black", f_de
  )

  x_de_cent = x_de_fim - 6
  y_de_cent = y_linha_de + f_de - f_de_cent - (f_de * 0.12)
  c.setFont("Arial-Black", f_de_cent)
  c.drawString(x_de_cent, y_de_cent, f",{de_cent}")

  c.setFont("Arial-Black", f_de_un)
  c.drawCentredString(
      x_de_cent + (w_de_cent / 2),
      y_de_cent - f_de_un - (3 * mm),
      item.get("un", "1 UN"),
  )

  # Risco do De
  c.setLineWidth(3.5)
  c.line(
      x_inicio_de,
      y_linha_de - 2 * mm,
      x_de_cent + w_de_cent + 2 * mm,
      y_linha_de + f_de + 2 * mm,
  )
  c.setLineWidth(1)

  # --- B) DESENHA O "POR" ---
  c.setFont("Arial-Black", f_rotulo)
  c.drawString(x_inicio_conjunto, y_linha_por + 5, "Por")

  x_inicio_por = x_inicio_conjunto + c.stringWidth(
      "Por ", "Arial-Black", f_rotulo
  )
  c.setFont("Arial-Black", f_por_rs)
  c.drawString(x_inicio_por, y_linha_por + (f_por * 0.75), "R$")

  x_por_num = x_inicio_por + c.stringWidth("R$ ", "Arial-Black", f_por_rs)
  x_por_fim = desenhar_inteiro_forcado(
      c, por_int, x_por_num, y_linha_por, "Arial-Black", f_por
  )

  x_por_cent = x_por_fim + folga_por_cent
  y_por_cent = y_linha_por + f_por - f_por_cent - (f_por * 0.12)
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_por_cent, y_por_cent, f",{por_cent}")

  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(
      x_por_cent + (w_por_cent / 2),
      y_por_cent - f_por_un - (5 * mm),
      item.get("un", "1 UN"),
  )
