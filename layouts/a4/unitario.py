from reportlab.lib.colors import black
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit


def desenhar_inteiro_forcado(c, texto, x_inicial, y, fonte, tamanho):
  x_atual = x_inicial
  c.setFont(fonte, tamanho)

  for i, char in enumerate(texto):
    c.drawString(x_atual, y, char)
    largura_char = c.stringWidth(char, fonte, tamanho)

    if char == "1":
      x_atual += largura_char * 0.60
    elif i + 1 < len(texto) and texto[i + 1] == "1":
      x_atual += largura_char * 0.75
    else:
      x_atual += largura_char

  return x_atual


def calcular_largura_inteiro_forcado(c, texto, fonte, tamanho):
  largura = 0
  for i, char in enumerate(texto):
    l_char = c.stringWidth(char, fonte, tamanho)
    if char == "1":
      largura += l_char * 0.60
    elif i + 1 < len(texto) and texto[i + 1] == "1":
      largura += l_char * 0.75
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

  # --- 3. BLOCO DO PREÇO COM AS MEDIDAS EXATAS ---
  por_raw = item.get("por", "0,00").strip().replace(".", ",")

  if "," in por_raw:
    partes = por_raw.split(",")
    inteiro_str = partes[0]
    centavos_str = partes[1][:2]
  else:
    inteiro_str = por_raw
    centavos_str = "00"

  # Medidas de referência fornecidas (em mm convertidas para pontos Y do ReportLab):
  # No ReportLab o ponto Y=0 fica no rodapé, então Y_reportlab = page_h - Y_medida
  x_rs = 17.2 * mm
  y_rs = page_h - (154.5 * mm)
  f_rs = 52

  x_real = 26.2 * mm
  y_real = page_h - (170.7 * mm)
  f_real = 336

  x_cent = 88.4 * mm
  y_cent = page_h - (176.0 * mm)
  f_cent = 168

  x_un = 118.7 * mm
  y_un = page_h - (244.6 * mm)
  f_un = 48

  # Cálculo da largura ocupada pelo inteiro e centavos
  w_real = calcular_largura_inteiro_forcado(
      c, inteiro_str, "Arial-Black", f_real
  )
  w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)

  # Posição onde o bloco do preço termina
  x_fim_total = x_real + w_real + w_cent

  # Verificação da margem lateral direita (não pode ultrapassar page_w - 8mm)
  limite_direita = page_w - margem_lateral_geral

  if x_fim_total > limite_direita:
    # Fator de redução dinâmico para caber na folha
    fator_red = (limite_direita - x_real) / (w_real + w_cent)
    f_real = int(f_real * fator_red)
    f_cent = int(f_cent * fator_red)
    f_rs = int(f_rs * fator_red)
    f_un = int(f_un * fator_red)

    # Recalcula larguras reduzidas
    w_real = calcular_largura_inteiro_forcado(
        c, inteiro_str, "Arial-Black", f_real
    )
    w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)

  # A) R$: Estático no ponto estipulado
  c.setFont("Arial-Black", f_rs)
  c.drawString(x_rs, y_rs, "R$")

  # B) VALOR REAL
  x_final_real = desenhar_inteiro_forcado(
      c, inteiro_str, x_real, y_real, "Arial-Black", f_real
  )

  # C) CENTAVOS (Inicia logo onde o valor real termina ou no X relativo)
  x_pos_cent = max(x_cent, x_final_real)
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_pos_cent, y_cent, f",{centavos_str}")

  # D) UNIDADE
  c.setFont("Arial-Black", f_un)
  un_str = item.get("un", "1 UN")
  c.drawString(x_un, y_un, un_str)
