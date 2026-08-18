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

  # --- 1. MARGEM SUPERIOR E DESCRIÇÃO ---
  y_atual = page_h - (80 * mm)  # antes: 69mm — mais folga da curva vermelha/amarela impressa

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

  # --- 2. BLOCO INFERIOR FIXO (CAIXA ABAIXADA PARA 8MM) ---
  largura_caixa = 202.3 * mm
  altura_caixa = 22.1 * mm
  x_caixa = (page_w - largura_caixa) / 2
  y_caixa = 8 * mm  # Abaixado de 15mm para 8mm da borda inferior

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

  # --- 3. BLOCO DO PREÇO EXPANDIDO ---
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
    f_real, f_cent, f_rs, f_un = 260, 122, 48, 34  # Aumentado para 260pt
    folga_centavos = -38
  elif num_digitos == 3:
    f_real, f_cent, f_rs, f_un = 235, 110, 44, 30
    folga_centavos = -32
  else:
    f_real, f_cent, f_rs, f_un = 190, 90, 36, 24
    folga_centavos = -24

  w_real = (
      calcular_largura_inteiro_forcado(c, inteiro_str, "Arial-Black", f_real)
      + folga_centavos
  )
  w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)
  largura_total_preco = w_real + w_cent

  # Trava de segurança para não ultrapassar as margens laterais de 8mm
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

  # Ponto médio geométrico cravado
  centro_area_livre = (limite_superior_preco + limite_inferior_preco) / 2
  y_linha_base_preco = centro_area_livre - (f_real * 0.35)
  x_inicio_real = (page_w - largura_total_preco) / 2

  # A) R$
  c.setFont("Arial-Black", f_rs)
  c.drawString(x_inicio_real, y_linha_base_preco + (f_real * 0.81), "R$")

  # B) VALOR REAL
  x_final_real = desenhar_inteiro_forcado(
      c, inteiro_str, x_inicio_real, y_linha_base_preco, "Arial-Black", f_real
  )

  # C) CENTAVOS
  x_centavos = x_final_real + folga_centavos
  y_centavos = y_linha_base_preco + f_real - f_cent - (f_real * 0.12)
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_centavos, y_centavos, f",{centavos_str}")

  # D) UNIDADE
  x_unidade = x_centavos + (w_cent / 2)
  y_unidade = y_centavos - f_un - (8 * mm)
  c.setFont("Arial-Black", f_un)
  un_str = item.get("un", "1 UN")
  c.drawCentredString(x_unidade, y_unidade, un_str)
