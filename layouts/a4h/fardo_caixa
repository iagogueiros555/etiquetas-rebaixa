from reportlab.lib.colors import HexColor, black
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics

# =====================================================================
# AJUSTES RÁPIDOS - mexa aqui para afinar depois dos testes de impressão
# =====================================================================
MARGEM_TOPO = 83 * mm        # do topo até a 1ª linha da descrição
MARGEM_LATERAL = 8 * mm      # respiro nas laterais
FONTE_DESC = 56              # tamanho inicial da descrição (reduz se precisar)
MAX_LINHAS_DESC = 2          # nome nunca passa disso: reduz a fonte até caber

# O painel tem TAMANHO E POSIÇÃO FIXOS: é sempre o mesmo retângulo, no mesmo
# lugar da folha, independente do produto ou do valor. Só o conteúdo de dentro
# se ajusta. Assim duas etiquetas lado a lado na gôndola ficam alinhadas.
COR_PAINEL = HexColor("#DCDCDC")
PAINEL_LARGURA = 130 * mm    # largura fixa do quadro cinza
PAINEL_ALTURA = 75 * mm      # altura fixa do quadro cinza
PAINEL_DIST_BASE = 18 * mm   # distância fixa entre o quadro e o pé da folha
GAP_ENTRE_COLUNAS = 12 * mm  # respiro entre a coluna da unidade e o quadro
PADDING_PAINEL = 10 * mm     # respiro entre o conteúdo e a borda do painel
GAP_ROTULO = 8 * mm          # entre o rótulo e o preço
FONTE_ROTULO = 28            # tamanho inicial dos rótulos (reduz se precisar)
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


def separar_valor(bruto):
  """Separa reais e centavos aceitando 7,58 / 1.548,00 / 1548 / 1548.00.

  O último separador (vírgula ou ponto) é o decimal; o que vier antes é
  ponto de milhar e é descartado. Sem isso, "1.548,00" viraria "1,54".
  """
  bruto = (bruto or "0,00").strip().replace(" ", "")
  corte = max(bruto.rfind(","), bruto.rfind("."))

  if corte == -1:
    inteiro, centavos = bruto, "00"
  else:
    inteiro = bruto[:corte]
    centavos = bruto[corte + 1:][:2]

  inteiro = inteiro.replace(".", "").replace(",", "") or "0"
  if len(centavos) == 1:
    centavos += "0"
  if not centavos:
    centavos = "00"
  return inteiro, centavos


def fontes_do_preco(f_real):
  """A partir do tamanho dos reais, deriva centavos, R$ e unidade."""
  return (
      f_real,
      max(8, round(f_real * 0.50)),   # centavos
      max(8, round(f_real * 0.21)),   # R$
      max(8, round(f_real * 0.13)),   # "1 UN"
  )


def medidas_bloco(f_real, f_cent, f_rs, f_un, tem_unidade):
  """Extremos do bloco de preço em relação à linha de base dos reais."""
  rel_rs = f_real * 0.53
  rel_cent = f_real - f_cent - (f_real * 0.12)
  rel_un = rel_cent - f_un - (5 * mm) if tem_unidade else 0.0
  topo = max(
      altura_digitos("Arial-Black", f_real),
      rel_rs + altura_digitos("Arial-Black", f_rs),
      rel_cent + altura_digitos("Arial-Black", f_cent),
  )
  return rel_rs, rel_cent, rel_un, topo, min(0.0, rel_un)


def largura_do_preco(c, inteiro, centavos, f_real, f_cent, f_rs, gap):
  return (c.stringWidth("R$", "Arial-Black", f_rs) + gap
          + calcular_largura_inteiro_forcado(c, inteiro, "Arial-Black", f_real)
          + c.stringWidth(f",{centavos}", "Arial-Black", f_cent))


def ajustar_rotulo(c, texto, f_rot, max_w):
  """Reduz o rótulo de 1 em 1 ponto até caber."""
  while f_rot > 10 and c.stringWidth(texto, "Arial-Black", f_rot) > max_w:
    f_rot -= 1
  return f_rot


def ajustar_por_largura(c, inteiro, centavos, f_inicial, gap, max_w, minimo=40):
  """Reduz o preço de 1 em 1 ponto até caber na largura disponível."""
  f = f_inicial
  while f > minimo:
    f_real, f_cent, f_rs, f_un = fontes_do_preco(f)
    if largura_do_preco(c, inteiro, centavos, f_real, f_cent, f_rs, gap) <= max_w:
      break
    f -= 1
  return fontes_do_preco(f)


def ajustar_dentro_do_painel(c, inteiro, centavos, f_inicial, f_rot, gap,
                             max_w, max_h, minimo=30):
  """Reduz o preço da caixa de 1 em 1 ponto até caber na largura E na
  altura livres dentro do painel (contando o rótulo em cima)."""
  f = f_inicial
  while f > minimo:
    f_real, f_cent, f_rs, f_un = fontes_do_preco(f)
    larg = largura_do_preco(c, inteiro, centavos, f_real, f_cent, f_rs, gap)
    _, _, _, topo, base = medidas_bloco(f_real, f_cent, f_rs, f_un, False)
    alt = altura_digitos("Arial-Black", f_rot) + GAP_ROTULO + topo - base
    if larg <= max_w and alt <= max_h:
      break
    f -= 1
  return fontes_do_preco(f)


def desenhar_preco(c, x_centro, y_base, inteiro, centavos, f_real, f_cent,
                   f_rs, f_un, gap, rel_rs, rel_cent, rel_un, unidade=None):
  w_rs = c.stringWidth("R$", "Arial-Black", f_rs)
  w_int = calcular_largura_inteiro_forcado(c, inteiro, "Arial-Black", f_real)
  w_cent = c.stringWidth(f",{centavos}", "Arial-Black", f_cent)
  x = x_centro - (w_rs + gap + w_int + w_cent) / 2

  c.setFont("Arial-Black", f_rs)
  c.drawString(x, y_base + rel_rs, "R$")

  x_fim = desenhar_inteiro_forcado(
      c, inteiro, x + w_rs + gap, y_base, "Arial-Black", f_real
  )

  c.setFont("Arial-Black", f_cent)
  c.drawString(x_fim, y_base + rel_cent, f",{centavos}")

  if unidade:
    c.setFont("Arial-Black", f_un)
    c.drawCentredString(x_fim + (w_cent / 2), y_base + rel_un, unidade)


def desenhar_etiqueta_a4h(c, item, x_base, y_base, col_w, row_h, scale):
  """Etiqueta A4 HORIZONTAL - Preço de Caixa/Fardo.

  O preço da caixa fica dentro de um painel cinza e cada preço tem seu
  rótulo, para ninguém confundir o valor da caixa com o da unidade.
  """
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

  linhas_desc = linhas_desc[:MAX_LINHAS_DESC]
  c.setFont("Arial-Black", tam_fonte_desc)
  c.setFillColor(black)

  espacamento_desc = tam_fonte_desc + 2
  y_linha = y_base + page_h - MARGEM_TOPO
  for linha in linhas_desc:
    c.drawCentredString(x_centro, y_linha, linha)
    y_linha -= espacamento_desc

  limite_superior = y_linha + espacamento_desc          # base da última linha

  # --- 2. DADOS DOS DOIS PREÇOS ---
  unidade = item.get("un", "UN")
  qtd_fardo = item.get("qtd_fardo", 1)

  un_int, un_cent = separar_valor(item.get("preco_unit"))
  cx_int, cx_cent = separar_valor(item.get("por"))

  rotulo_un = "PREÇO DA UNIDADE"
  rotulo_cx = f"PREÇO DA CAIXA ({qtd_fardo} {unidade})"

  # --- 3. PAINEL: RETÂNGULO FIXO, SEMPRE NO MESMO LUGAR ---
  # Nada aqui depende do produto nem do valor — é o que garante que todas as
  # etiquetas de fardo saiam com o quadro do mesmo tamanho e na mesma posição.
  x_painel = x_base + page_w - MARGEM_LATERAL - PAINEL_LARGURA
  painel_base = y_base + PAINEL_DIST_BASE

  # Trava de segurança: com os valores padrão o painel nunca chega perto da
  # descrição, mas se alguém aumentar PAINEL_ALTURA ou MARGEM_TOPO, ele desce
  # o necessário para não encostar no texto (mantendo o tamanho).
  folga_minima = 6 * mm
  if painel_base + PAINEL_ALTURA > limite_superior - folga_minima:
    painel_base = limite_superior - folga_minima - PAINEL_ALTURA

  painel_topo = painel_base + PAINEL_ALTURA
  centro_painel = painel_base + (PAINEL_ALTURA / 2)

  x_col_un = x_base + MARGEM_LATERAL
  larg_coluna = (x_painel - x_col_un) - GAP_ENTRE_COLUNAS
  x_centro_un = x_col_un + (larg_coluna / 2)
  x_centro_cx = x_painel + (PAINEL_LARGURA / 2)

  # --- 4. COLUNA DA UNIDADE (centralizada na mesma linha do painel) ---
  f_un_real, f_un_cent, f_un_rs, f_un_um = ajustar_por_largura(
      c, un_int, un_cent, 210, 4 * mm, larg_coluna
  )
  f_rot_un = ajustar_rotulo(c, rotulo_un, FONTE_ROTULO, larg_coluna)

  rel_rs_un, rel_cent_un, rel_um_un, topo_un, base_un = medidas_bloco(
      f_un_real, f_un_cent, f_un_rs, f_un_um, True
  )
  topo_col_un = topo_un + GAP_ROTULO + altura_digitos("Arial-Black", f_rot_un)

  y_preco = centro_painel - ((topo_col_un + base_un) / 2)

  # --- 5. PREÇO DA CAIXA: REDUZ ATÉ CABER DENTRO DO PAINEL ---
  larg_livre = PAINEL_LARGURA - (2 * PADDING_PAINEL)
  alt_livre = PAINEL_ALTURA - (2 * PADDING_PAINEL)

  f_rot_cx = ajustar_rotulo(c, rotulo_cx, FONTE_ROTULO, larg_livre)
  f_cx_real, f_cx_cent, f_cx_rs, f_cx_um = ajustar_dentro_do_painel(
      c, cx_int, cx_cent, 150, f_rot_cx, 3.5 * mm, larg_livre, alt_livre
  )

  rel_rs_cx, rel_cent_cx, rel_um_cx, topo_cx, base_cx = medidas_bloco(
      f_cx_real, f_cx_cent, f_cx_rs, f_cx_um, False
  )

  # conteúdo (rótulo + preço) centralizado verticalmente dentro do painel
  alt_conteudo = altura_digitos("Arial-Black", f_rot_cx) + GAP_ROTULO + topo_cx - base_cx
  topo_conteudo = centro_painel + (alt_conteudo / 2)
  y_preco_cx = topo_conteudo - altura_digitos("Arial-Black", f_rot_cx) - GAP_ROTULO - topo_cx

  # --- 6. PAINEL (cantos retos, desenhado antes para ficar atrás) ---
  c.setFillColor(COR_PAINEL)
  c.rect(x_painel, painel_base, PAINEL_LARGURA, PAINEL_ALTURA,
         stroke=0, fill=1)
  c.setFillColor(black)

  # --- 7. COLUNA DA UNIDADE ---
  c.setFont("Arial-Black", f_rot_un)
  c.drawCentredString(x_centro_un, y_preco + topo_un + GAP_ROTULO, rotulo_un)
  desenhar_preco(
      c, x_centro_un, y_preco, un_int, un_cent, f_un_real, f_un_cent,
      f_un_rs, f_un_um, 4 * mm, rel_rs_un, rel_cent_un, rel_um_un,
      unidade=f"1 {unidade}",
  )

  # --- 8. PAINEL DA CAIXA ---
  c.setFont("Arial-Black", f_rot_cx)
  c.drawCentredString(x_centro_cx, y_preco_cx + topo_cx + GAP_ROTULO, rotulo_cx)
  desenhar_preco(
      c, x_centro_cx, y_preco_cx, cx_int, cx_cent, f_cx_real, f_cx_cent,
      f_cx_rs, f_cx_um, 3.5 * mm, rel_rs_cx, rel_cent_cx, rel_um_cx,
  )
