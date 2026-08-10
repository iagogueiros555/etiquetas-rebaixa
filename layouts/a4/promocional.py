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

  # Como não temos mais rodapé de validade, a margem inferior é apenas um respiro
  limite_inferior_preco = 15 * mm

  # --- 2. RÓTULOS 'DE' E 'POR' FIXOS ---
  # Margem esquerda fixa para os rótulos já que a frase base sumiu
  x_alinhado_linha_1 = 15 * mm

  # Espaçamento vertical recalculado para centralizar o bloco no espaço livre
  y_linha_por = limite_inferior_preco + 35 * mm
  y_linha_de = y_linha_por + 80 * mm

  f_rotulo = 50  # Rótulos aumentados
  c.setFont("Arial-Black", f_rotulo)
  c.drawString(x_alinhado_linha_1, y_linha_de, "De")
  c.drawString(x_alinhado_linha_1, y_linha_por, "Por")

  # Delimitação do quadro à direita
  x_inicio_quadro = x_alinhado_linha_1 + 30 * mm
  x_fim_quadro = page_w - x_margem_estatica
  largura_quadro = x_fim_quadro - x_inicio_quadro

  # --- 3. PREÇO "DE" ---
  de_raw = item.get("de", "0,00").strip().replace(".", ",")
  if "," in de_raw:
    de_int, de_cent = de_raw.split(",")[0], de_raw.split(",")[1][:2]
  else:
    de_int, de_cent = de_raw, "00"

  # Fontes turbinadas para o "De"
  num_de = len(de_int)
  if num_de <= 2:
    f_de, f_de_cent, f_de_rs, f_de_un = 130, 60, 32, 20
  elif num_de == 3:
    f_de, f_de_cent, f_de_rs, f_de_un = 110, 50, 28, 18
  else:
    f_de, f_de_cent, f_de_rs, f_de_un = 90, 42, 24, 16

  y_valor_de = y_linha_de - (f_de * 0.35)

  w_de_rs = c.stringWidth("R$ ", "Arial-Black", f_de_rs)
  w_de_real = calcular_largura_inteiro_forcado(c, de_int, "Arial-Black", f_de)
  w_de_cent = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)
  largura_total_de = w_de_rs + w_de_real + w_de_cent

  x_de_bloco_inicio = x_inicio_quadro + (largura_quadro - largura_total_de) / 2

  c.setFont("Arial-Black", f_de_rs)
  c.drawString(x_de_bloco_inicio, y_valor_de + (f_de * 0.65), "R$")

  x_de_num = x_de_bloco_inicio + w_de_rs
  x_de_fim = desenhar_inteiro_forcado(
      c, de_int, x_de_num, y_valor_de, "Arial-Black", f_de
  )

  x_de_cent = x_de_fim - 8
  y_de_cent = y_valor_de + f_de - f_de_cent - (f_de * 0.12)
  c.setFont("Arial-Black", f_de_cent)
  c.drawString(x_de_cent, y_de_cent, f",{de_cent}")

  w_de_cent = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)
  c.setFont("Arial-Black", f_de_un)
  c.drawCentredString(
      x_de_cent + (w_de_cent / 2),
      y_de_cent - f_de_un - (3 * mm),
      item.get("un", "1 UN"),
  )

  c.setLineWidth(4.5)
  c.line(
      x_de_num - 2 * mm,
      y_valor_de,
      x_de_cent + w_de_cent + 2 * mm,
      y_valor_de + (f_de * 0.75),
  )
  c.setLineWidth(1)

  # --- 4. PREÇO "POR" ---
  por_raw = item.get("por", "0,00").strip().replace(".", ",")
  if "," in por_raw:
    por_int, por_cent = por_raw.split(",")[0], por_raw.split(",")[1][:2]
  else:
    por_int, por_cent = por_raw, "00"

  # Fontes turbinadas para o "Por"
  num_por = len(por_int)
  if num_por <= 2:
    f_por, f_por_cent, f_por_rs, f_por_un = 220, 100, 46, 30
  elif num_por == 3:
    f_por, f_por_cent, f_por_rs, f_por_un = 180, 85, 38, 26
  else:
    f_por, f_por_cent, f_por_rs, f_por_un = 150, 70, 32, 22

  y_valor_por = y_linha_por - (f_por * 0.35)

  w_por_rs = c.stringWidth("R$ ", "Arial-Black", f_por_rs)
  w_por_real = calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
  w_por_cent = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)
  largura_total_por = w_por_rs + w_por_real + w_por_cent

  if largura_total_por > largura_quadro:
    fator_red = largura_quadro / largura_total_por
    f_por = int(f_por * fator_red)
    f_por_cent = int(f_por_cent * fator_red)
    f_por_rs = int(f_por_rs * fator_red)
    f_por_un = int(f_por_un * fator_red)

    w_por_rs = c.stringWidth("R$ ", "Arial-Black", f_por_rs)
    w_por_real = (
        calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
    )
    w_por_cent = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)
    largura_total_por = w_por_rs + w_por_real + w_por_cent

  x_por_bloco_inicio = x_inicio_quadro + (largura_quadro - largura_total_por) / 2

  c.setFont("Arial-Black", f_por_rs)
  c.drawString(x_por_bloco_inicio, y_valor_por + (f_por * 0.75), "R$")

  x_por_num = x_por_bloco_inicio + w_por_rs
  x_por_fim = desenhar_inteiro_forcado(
      c, por_int, x_por_num, y_valor_por, "Arial-Black", f_por
  )

  x_por_cent = x_por_fim - 10
  y_por_cent = y_valor_por + f_por - f_por_cent - (f_por * 0.15)
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_por_cent, y_por_cent, f",{por_cent}")

  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(
      x_por_cent + (c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent) / 2),
      y_por_cent - f_por_un - (5 * mm),
      item.get("un", "1 UN"),
  )
