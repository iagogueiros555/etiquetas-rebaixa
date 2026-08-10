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

  # --- 2. RODAPÉ CINZA: PREÇO DA CAIXA ---
  largura_caixa = page_w - (2 * x_margem_estatica)
  altura_caixa = 52 * mm
  x_caixa = x_margem_estatica
  y_caixa = 15 * mm

  c.setFillColor(lightgrey)
  c.rect(x_caixa, y_caixa, largura_caixa, altura_caixa, stroke=0, fill=1)
  c.setFillColor(black)

  f_rotulo_cx = 36
  c.setFont("Arial-Black", f_rotulo_cx)
  qtd_fardo_val = item.get("qtd_fardo", 1)
  unidade_fardo = item.get("un", "UN")
  texto_fardo_rotulo = f"PREÇO DA CAIXA ({qtd_fardo_val} {unidade_fardo})"
  c.drawCentredString(page_w / 2, y_caixa + altura_caixa - 13 * mm, texto_fardo_rotulo)

  caixa_raw = item.get("por", "0,00").strip().replace(".", ",")
  cx_int, cx_cent = caixa_raw.split(",")[0], caixa_raw.split(",")[1][:2] if "," in caixa_raw else (caixa_raw, "00")

  f_cx, f_cx_cent, f_cx_rs = 90, 42, 24
  y_valor_cx = y_caixa + 8 * mm
  gap_cx_rs = 2.5 * mm

  w_cx_rs = c.stringWidth("R$", "Arial-Black", f_cx_rs)
  w_cx_real = calcular_largura_inteiro_forcado(c, cx_int, "Arial-Black", f_cx)
  w_cx_cent = c.stringWidth(f",{cx_cent}", "Arial-Black", f_cx_cent)
  largura_total_cx = w_cx_rs + gap_cx_rs + w_cx_real + w_cx_cent

  x_cx_bloco_inicio = (page_w - largura_total_cx) / 2
  c.setFont("Arial-Black", f_cx_rs)
  c.drawString(x_cx_bloco_inicio, y_valor_cx + (f_cx * 0.65), "R$")

  x_cx_num = x_cx_bloco_inicio + w_cx_rs + gap_cx_rs
  x_cx_fim = desenhar_inteiro_forcado(c, cx_int, x_cx_num, y_valor_cx, "Arial-Black", f_cx)

  c.setFont("Arial-Black", f_cx_cent)
  c.drawString(x_cx_fim - 6, y_valor_cx + f_cx - f_cx_cent - (f_cx * 0.12), f",{cx_cent}")

  # --- 3. PREÇO UNITÁRIO GIGANTE ---
  y_linha_por = y_caixa + altura_caixa + 62 * mm
  
  unit_raw = item.get("preco_unit", "0,00").strip().replace(".", ",")
  unit_int, unit_cent = unit_raw.split(",")[0], unit_raw.split(",")[1][:2] if "," in unit_raw else (unit_raw, "00")

  num_unit = len(unit_int)
  f_unit, f_unit_cent, f_unit_rs, f_unit_un = (240, 110, 50, 32) if num_unit <= 2 else (180, 85, 38, 26)

  y_valor_unit = y_linha_por - (f_unit * 0.35)
  gap_unit_rs = 3 * mm

  w_unit_rs = c.stringWidth("R$", "Arial-Black", f_unit_rs)
  w_unit_real = calcular_largura_inteiro_forcado(c, unit_int, "Arial-Black", f_unit)
  w_unit_cent = c.stringWidth(f",{unit_cent}", "Arial-Black", f_unit_cent)
  largura_total_unit = w_unit_rs + gap_unit_rs + w_unit_real + w_unit_cent

  x_unit_bloco_inicio = (page_w - largura_total_unit) / 2
  c.setFont("Arial-Black", f_unit_rs)
  c.drawString(x_unit_bloco_inicio, y_valor_unit + (f_unit * 0.75), "R$")

  x_unit_num = x_unit_bloco_inicio + w_unit_rs + gap_unit_rs
  x_unit_fim = desenhar_inteiro_forcado(c, unit_int, x_unit_num, y_valor_unit, "Arial-Black", f_unit)

  y_unit_cent = y_valor_unit + f_unit - f_unit_cent - (f_unit * 0.15)
  c.setFont("Arial-Black", f_unit_cent)
  c.drawString(x_unit_fim - 10, y_unit_cent, f",{unit_cent}")

  # Unidade com o respiro exato de 7mm abaixo dos centavos
  c.setFont("Arial-Black", f_unit_un)
  c.drawCentredString(
      x_unit_fim - 10 + (c.stringWidth(f",{unit_cent}", "Arial-Black", f_unit_cent) / 2),
      y_unit_cent - f_unit_un - (7 * mm),
      f"1 {unidade_fardo}"
  )
