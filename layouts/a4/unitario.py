from reportlab.lib.colors import black
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

  # --- 1. MARGEM SUPERIOR DE 69 MM ATÉ A DESCRIÇÃO ---
  y_atual = page_h - (69 * mm)

  # --- 2. DESCRIÇÃO DO PRODUTO (Fonte 56pt) ---
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
  limite_inferior_preco = 15 * mm

  # --- 3. BLOCO DO PREÇO PROPORCIONAL E ALINHADO ---
  por_raw = item.get("por", "0,00").strip().replace(".", ",")

  if "," in por_raw:
    partes = por_raw.split(",")
    inteiro_str = partes[0]
    centavos_str = partes[1][:2]
  else:
    inteiro_str = por_raw
    centavos_str = "00"

  num_digitos = len(inteiro_str)

  if num_digitos <= 2:
    f_real, f_cent, f_rs, f_un = 310, 145, 52, 40
    folga_centavos = -45
  elif num_digitos == 3:
    f_real, f_cent, f_rs, f_un = 210, 98, 42, 28
    folga_centavos = -28
  else:
    f_real, f_cent, f_rs, f_un = 140, 65, 32, 20
    folga_centavos = -18

  w_real = (
      calcular_largura_inteiro_forcado(c, inteiro_str, "Arial-Black", f_real)
      + folga_centavos
  )
  w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)
  largura_total_preco = w_real + w_cent

  if largura_total_preco > largura_util_geral:
    fator_red = largura_util_geral / largura_total_preco
    f_real = int(f_real * fator_red)
    f_cent = int(f_cent * fator_red)
    f_rs = int(f_rs * fator_red)
    f_un = int(f_un * fator_red)
    folga_centavos = int(folga_centavos * fator_red)

    w_real = (
        calcular_largura_inteiro_forcado(c, inteiro_str, "Arial-Black", f_real)
        + folga_centavos
    )
    w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)
    largura_total_preco = w_real + w_cent

  centro_area = (limite_superior_preco + limite_inferior_preco) / 2
  y_linha_base_preco = centro_area - (f_real / 2) + 20
  x_inicio_real = (page_w - largura_total_preco) / 2

  # A) R$: Alinhado dinamicamente ao topo do inteiro
  c.setFont("Arial-Black", f_rs)
  c.drawString(x_inicio_real, y_linha_base_preco + (f_real * 0.81), "R$")

  # B) VALOR REAL
  x_final_real = desenhar_inteiro_forcado(
      c, inteiro_str, x_inicio_real, y_linha_base_preco, "Arial-Black", f_real
  )

  # C) CENTAVOS: Alinhamento de topo proporcional exato ao inteiro
  x_centavos = x_final_real + folga_centavos
  y_centavos = y_linha_base_preco + f_real - f_cent - (f_real * 0.12)
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_centavos, y_centavos, f",{centavos_str}")

  # D) UNIDADE: Distância proporcional aos centavos
  x_unidade = x_centavos + (w_cent / 2)
  y_unidade = y_centavos - f_un - (10 * mm)
  c.setFont("Arial-Black", f_un)
  un_str = item.get("un", "1 UN")
  c.drawCentredString(x_unidade, y_unidade, un_str)
