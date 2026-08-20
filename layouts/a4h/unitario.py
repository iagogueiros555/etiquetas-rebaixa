from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics

# =====================================================================
# AJUSTES RÁPIDOS - mexa aqui para afinar depois dos testes de impressão
# =====================================================================
MARGEM_TOPO = 83 * mm      # do topo até a 1ª linha da descrição
                           # (a faixa vermelha termina a 64mm; o oficial usa 79mm)
MARGEM_LATERAL = 8 * mm    # respiro nas laterais (a impressora corta letra na borda)
FONTE_DESC = 56            # tamanho inicial da descrição (vai reduzindo se precisar)
MAX_LINHAS_DESC = 2        # nome nunca passa disso: reduz a fonte até caber
# =====================================================================


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


def desenhar_etiqueta_a4h(c, item, x_base, y_base, col_w, row_h, scale):
  """Etiqueta A4 HORIZONTAL - Preço único, sem validade."""
  page_w = col_w
  page_h = row_h
  x_centro = x_base + (page_w / 2)
  largura_util = page_w - (2 * MARGEM_LATERAL)

  # --- 1. DESCRIÇÃO DO PRODUTO (reduz sozinha até caber em 2 linhas) ---
  tam_fonte_desc = FONTE_DESC
  desc = item.get("desc", "")

  linhas_desc = []
  while tam_fonte_desc > 20:
    c.setFont("Arial-Black", tam_fonte_desc)
    linhas_desc = simpleSplit(desc, "Arial-Black", tam_fonte_desc, largura_util)
    if len(linhas_desc) <= MAX_LINHAS_DESC:
      break
    tam_fonte_desc -= 1

  linhas_desc = linhas_desc[:MAX_LINHAS_DESC]  # trava: nunca desenha uma 3ª linha
  c.setFont("Arial-Black", tam_fonte_desc)

  espacamento_desc = tam_fonte_desc + 2
  y_linha = y_base + page_h - MARGEM_TOPO
  for linha in linhas_desc:
    c.drawCentredString(x_centro, y_linha, linha)
    y_linha -= espacamento_desc

  # Onde a tinta da descrição realmente termina (linha de base da última linha)
  limite_superior_preco = y_linha + espacamento_desc

  # Sem caixa de validade embaixo: o branco vai até o pé da folha
  limite_inferior_preco = y_base

  # --- 2. BLOCO DO PREÇO ---
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
    f_real, f_cent, f_rs, f_un = 280, 140, 55, 34
    folga_centavos = -15
  elif num_digitos == 3:
    f_real, f_cent, f_rs, f_un = 230, 115, 48, 30
    folga_centavos = -10
  else:
    f_real, f_cent, f_rs, f_un = 190, 95, 42, 26
    folga_centavos = -5

  gap_rs = 4 * mm

  def medir():
    w_rs = c.stringWidth("R$", "Arial-Black", f_rs)
    w_real = (
        calcular_largura_inteiro_forcado(c, inteiro_str, "Arial-Black", f_real)
        + folga_centavos
    )
    w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)
    return w_rs, w_real, w_cent, w_rs + gap_rs + w_real + w_cent

  w_rs, w_real, w_cent, largura_total = medir()

  # Trava de segurança: se estourar a margem lateral, reduz tudo junto
  if largura_total > largura_util:
    fator = largura_util / largura_total
    f_real = int(f_real * fator)
    f_cent = int(f_cent * fator)
    f_rs = int(f_rs * fator)
    f_un = int(f_un * fator)
    folga_centavos = int(folga_centavos * fator)
    gap_rs = gap_rs * fator
    w_rs, w_real, w_cent, largura_total = medir()

  # --- 3. CENTRALIZAÇÃO REAL DO BLOCO NO ESPAÇO BRANCO ---
  # Posições relativas à linha de base dos reais. O R$ fica na altura do
  # oficial (mais baixo do que nos modelos em pé, que sobem demais).
  rel_rs = f_real * 0.53
  rel_centavos = f_real - f_cent - (f_real * 0.12)
  rel_unidade = rel_centavos - f_un - (8 * mm)

  topo_rel = max(
      altura_digitos("Arial-Black", f_real),
      rel_rs + altura_digitos("Arial-Black", f_rs),
      rel_centavos + altura_digitos("Arial-Black", f_cent),
  )
  base_rel = min(0.0, rel_unidade)

  centro_area = (limite_superior_preco + limite_inferior_preco) / 2
  y_base_preco = centro_area - ((topo_rel + base_rel) / 2)
  x_inicio = x_base + (page_w - largura_total) / 2

  # A) R$
  c.setFont("Arial-Black", f_rs)
  c.drawString(x_inicio, y_base_preco + rel_rs, "R$")

  # B) VALOR EM REAIS
  x_num = x_inicio + w_rs + gap_rs
  x_fim_real = desenhar_inteiro_forcado(
      c, inteiro_str, x_num, y_base_preco, "Arial-Black", f_real
  )

  # C) CENTAVOS
  x_centavos = x_fim_real + folga_centavos
  y_centavos = y_base_preco + rel_centavos
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_centavos, y_centavos, f",{centavos_str}")

  # D) UNIDADE
  c.setFont("Arial-Black", f_un)
  c.drawCentredString(
      x_centavos + (w_cent / 2),
      y_centavos - f_un - (8 * mm),
      item.get("un", "1 UN"),
  )
