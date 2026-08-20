from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics


def altura_digitos(fonte, tamanho):
  """Altura real dos dígitos/maiúsculas na fonte em uso (para centralizar certo)."""
  return pdfmetrics.getFont(fonte).face.capHeight / 1000.0 * tamanho


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
  y_atual = page_h - (80 * mm)  # antes: 69mm — folga da curva vermelha/amarela impressa
  tamanho_fonte_desc = 56
  c.setFont("Arial-Black", tamanho_fonte_desc)
  desc = item.get("desc", "")

  linhas_desc = simpleSplit(
      desc, "Arial-Black", tamanho_fonte_desc, largura_util_geral
  )
  for linha in linhas_desc:
    c.drawCentredString(page_w / 2, y_atual, linha)
    y_atual -= tamanho_fonte_desc + 2

  # y_atual já desceu uma linha inteira após o laço; a tinta da descrição
  # termina na linha de base da última linha.
  limite_superior_preco = y_atual + tamanho_fonte_desc + 2

  # --- 2. RODAPÉ DE VALIDADE ---
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

  # --- 3. SEPARAÇÃO DOS VALORES ---
  de_raw = item.get("de", "0,00").strip().replace(".", ",")
  if "," in de_raw:
    de_int, de_cent = de_raw.split(",")[0], de_raw.split(",")[1][:2]
  else:
    de_int, de_cent = de_raw, "00"

  por_raw = item.get("por", "0,00").strip().replace(".", ",")
  if "," in por_raw:
    por_int, por_cent = por_raw.split(",")[0], por_raw.split(",")[1][:2]
  else:
    por_int, por_cent = por_raw, "00"

  # Fontes reduzidas ~15% em relação à versão anterior, para o bloco De/Por
  # caber com folga entre a descrição e o aviso da validade.
  num_de = len(de_int)
  if num_de <= 2:
    f_de, f_de_cent, f_de_rs, f_de_un = 94, 43, 22, 14   # antes: 110, 50, 26, 16
  elif num_de == 3:
    f_de, f_de_cent, f_de_rs, f_de_un = 77, 36, 20, 13   # antes: 90, 42, 24, 15
  else:
    f_de, f_de_cent, f_de_rs, f_de_un = 64, 31, 17, 12   # antes: 75, 36, 20, 14

  num_por = len(por_int)
  if num_por <= 2:
    f_por, f_por_cent, f_por_rs, f_por_un = 154, 73, 32, 22  # antes: 180, 85, 38, 26
  elif num_por == 3:
    f_por, f_por_cent, f_por_rs, f_por_un = 128, 60, 27, 19  # antes: 150, 70, 32, 22
  else:
    f_por, f_por_cent, f_por_rs, f_por_un = 102, 47, 24, 15  # antes: 120, 55, 28, 18

  f_rotulo = 40

  # --- 4. CENTRALIZAÇÃO DO CONJUNTO "DE + POR" NO ESPAÇO BRANCO ---
  # Distância vertical entre a linha do "De" e a linha do "Por"
  gap_de_por = 50 * mm  # antes: 58mm (acompanha a redução das fontes)

  # Extremos do "Por" (referência y = 0)
  rel_por_valor = -(f_por * 0.35)
  rel_por_rs = rel_por_valor + (f_por * 0.75)
  rel_por_cent = rel_por_valor + f_por - f_por_cent - (f_por * 0.15)
  rel_por_un = rel_por_cent - f_por_un - (5 * mm)

  # Extremos do "De" (deslocado de gap_de_por para cima)
  rel_de_valor = gap_de_por - (f_de * 0.35)
  rel_de_rs = rel_de_valor + (f_de * 0.65)
  rel_de_cent = rel_de_valor + f_de - f_de_cent - (f_de * 0.12)

  topo_rel = max(
      gap_de_por + altura_digitos("Arial-Black", f_rotulo),
      rel_de_valor + altura_digitos("Arial-Black", f_de),
      rel_de_rs + altura_digitos("Arial-Black", f_de_rs),
      rel_de_cent + altura_digitos("Arial-Black", f_de_cent),
  )
  base_rel = min(rel_por_valor, rel_por_un)

  centro_area = (limite_superior_preco + limite_inferior_preco) / 2
  y_linha_por = centro_area - ((topo_rel + base_rel) / 2)
  y_linha_de = y_linha_por + gap_de_por

  # --- 5. RÓTULOS 'DE' E 'POR' ---
  primeira_linha_aviso = linhas_aviso[0] if linhas_aviso else ""
  largura_linha_1 = c.stringWidth(
      primeira_linha_aviso, "Arial-Black", f_aviso
  )
  x_alinhado_linha_1 = (page_w - largura_linha_1) / 2

  c.setFont("Arial-Black", f_rotulo)
  c.drawString(x_alinhado_linha_1, y_linha_de, "De")
  c.drawString(x_alinhado_linha_1, y_linha_por, "Por")

  # Delimitação do quadro à direita
  x_inicio_quadro = x_alinhado_linha_1 + 24 * mm
  x_fim_quadro = page_w - x_margem_estatica
  largura_quadro = x_fim_quadro - x_inicio_quadro

  # --- 6. PREÇO "DE" ---
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

  x_de_cent = x_de_fim - 6
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

  # --- 7. PREÇO "POR" ---
  y_valor_por = y_linha_por - (f_por * 0.35)

  w_por_rs = c.stringWidth("R$ ", "Arial-Black", f_por_rs)
  w_por_real = calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
  w_por_cent = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)
  largura_total_por = w_por_rs + w_por_real + w_por_cent

  x_por_bloco_inicio = x_inicio_quadro + (largura_quadro - largura_total_por) / 2

  c.setFont("Arial-Black", f_por_rs)
  c.drawString(x_por_bloco_inicio, y_valor_por + (f_por * 0.75), "R$")

  x_por_num = x_por_bloco_inicio + w_por_rs
  x_por_fim = desenhar_inteiro_forcado(
      c, por_int, x_por_num, y_valor_por, "Arial-Black", f_por
  )

  x_por_cent = x_por_fim - 8
  y_por_cent = y_valor_por + f_por - f_por_cent - (f_por * 0.15)
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_por_cent, y_por_cent, f",{por_cent}")

  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(
      x_por_cent + (c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent) / 2),
      y_por_cent - f_por_un - (5 * mm),
      item.get("un", "1 UN"),
  )
