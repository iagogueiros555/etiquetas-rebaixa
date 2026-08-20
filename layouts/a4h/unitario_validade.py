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

# --- Rodapé de validade ---
COR_TARJA = HexColor("#DCDCDC")
TARJA_ALTURA = 22.1 * mm     # altura da tarja cinza
TARJA_DIST_BASE = 6 * mm     # distância da tarja até o pé da folha
GAP_AVISO_TARJA = 1.5 * mm   # entre a frase de aviso e a tarja
FONTE_VALIDADE = 56          # tamanho inicial do "VALIDADE: ..." (reduz p/ caber)
FONTE_AVISO = 34             # tamanho inicial da frase (reduz até caber em 1 linha)
PADDING_TARJA = 3 * mm       # respiro do texto dentro da tarja
FOLGA_PRECO = 7 * mm         # respiro mínimo do preço até a descrição e o aviso

TEXTO_AVISO = "PRODUTO PRÓXIMO A DATA DE VENCIMENTO"
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


def medidas_bloco(f_real, f_cent, f_rs, f_un):
  """Extremos do bloco de preço em relação à linha de base dos reais."""
  rel_rs = f_real * 0.53
  rel_cent = f_real - f_cent - (f_real * 0.12)
  rel_un = rel_cent - f_un - (8 * mm)
  topo = max(
      altura_digitos("Arial-Black", f_real),
      rel_rs + altura_digitos("Arial-Black", f_rs),
      rel_cent + altura_digitos("Arial-Black", f_cent),
  )
  return rel_rs, rel_cent, rel_un, topo, min(0.0, rel_un)


def ajustar_preco(c, inteiro, centavos, f_inicial, gap, max_w, max_h, minimo=40):
  """Reduz o preço de 1 em 1 ponto até caber na largura E na altura livres."""
  f = f_inicial
  while f > minimo:
    f_real, f_cent, f_rs, f_un = fontes_do_preco(f)
    largura = (c.stringWidth("R$", "Arial-Black", f_rs) + gap
               + calcular_largura_inteiro_forcado(c, inteiro, "Arial-Black", f_real)
               + c.stringWidth(f",{centavos}", "Arial-Black", f_cent))
    _, _, _, topo, base = medidas_bloco(f_real, f_cent, f_rs, f_un)
    if largura <= max_w and (topo - base) <= max_h:
      break
    f -= 1
  return fontes_do_preco(f)


def ajustar_aviso_uma_linha(c, texto, f_inicial, max_w, minimo=16):
  """Reduz a frase de aviso até ela caber em UMA linha.

  Fica assim, e não num tamanho fixo, porque a largura depende da fonte
  instalada: se a Arial-Black daí for mais larga, ela se acomoda sozinha
  em vez de quebrar em duas linhas e desmontar o rodapé.
  """
  f = f_inicial
  while f > minimo and c.stringWidth(texto, "Arial-Black", f) > max_w:
    f -= 1
  return f


def ajustar_validade(c, texto, f_inicial, max_w, max_h, minimo=20):
  """Reduz o texto da validade até caber na largura e na altura da tarja."""
  f = f_inicial
  while f > minimo:
    cabe_largura = c.stringWidth(texto, "Arial-Black", f) <= max_w
    cabe_altura = altura_digitos("Arial-Black", f) <= max_h
    if cabe_largura and cabe_altura:
      break
    f -= 1
  return f


def desenhar_etiqueta_a4h(c, item, x_base, y_base, col_w, row_h, scale):
  """Etiqueta A4 HORIZONTAL - Preço único, com validade (rebaixa)."""
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

  limite_superior = y_linha + espacamento_desc   # base da última linha

  # --- 2. RODAPÉ: TARJA DE VALIDADE + FRASE DE AVISO ---
  x_tarja = x_base + MARGEM_LATERAL
  y_tarja = y_base + TARJA_DIST_BASE

  c.setFillColor(COR_TARJA)
  c.rect(x_tarja, y_tarja, largura_util, TARJA_ALTURA, stroke=0, fill=1)
  c.setFillColor(black)

  val_str = item.get("val", "")
  texto_validade = f"VALIDADE: {val_str}" if val_str else "VALIDADE:"
  f_validade = ajustar_validade(
      c, texto_validade, FONTE_VALIDADE,
      largura_util - (2 * PADDING_TARJA),
      TARJA_ALTURA - (2 * PADDING_TARJA),
  )
  # texto centralizado na altura da tarja
  y_texto_validade = (y_tarja + (TARJA_ALTURA / 2)
                      - (altura_digitos("Arial-Black", f_validade) / 2))
  c.setFont("Arial-Black", f_validade)
  c.drawCentredString(x_centro, y_texto_validade, texto_validade)

  # frase de aviso, sempre em uma linha só, logo acima da tarja
  f_aviso = ajustar_aviso_uma_linha(c, TEXTO_AVISO, FONTE_AVISO, largura_util)
  y_aviso = y_tarja + TARJA_ALTURA + GAP_AVISO_TARJA
  c.setFont("Arial-Black", f_aviso)
  c.drawCentredString(x_centro, y_aviso, TEXTO_AVISO)

  limite_inferior = y_aviso + altura_digitos("Arial-Black", f_aviso)

  # --- 3. BLOCO DO PREÇO (entre a descrição e o rodapé) ---
  inteiro, centavos = separar_valor(item.get("por"))

  gap_rs = 4 * mm
  altura_livre = (limite_superior - limite_inferior) - (2 * FOLGA_PRECO)
  f_real, f_cent, f_rs, f_un = ajustar_preco(
      c, inteiro, centavos, 300, gap_rs,
      largura_util, altura_livre,
  )

  rel_rs, rel_cent, rel_un, topo_rel, base_rel = medidas_bloco(
      f_real, f_cent, f_rs, f_un
  )

  centro_area = (limite_superior + limite_inferior) / 2
  y_preco = centro_area - ((topo_rel + base_rel) / 2)

  w_rs = c.stringWidth("R$", "Arial-Black", f_rs)
  w_int = calcular_largura_inteiro_forcado(c, inteiro, "Arial-Black", f_real)
  w_cent = c.stringWidth(f",{centavos}", "Arial-Black", f_cent)
  x_inicio = x_centro - (w_rs + gap_rs + w_int + w_cent) / 2

  c.setFont("Arial-Black", f_rs)
  c.drawString(x_inicio, y_preco + rel_rs, "R$")

  x_fim = desenhar_inteiro_forcado(
      c, inteiro, x_inicio + w_rs + gap_rs, y_preco, "Arial-Black", f_real
  )

  c.setFont("Arial-Black", f_cent)
  c.drawString(x_fim, y_preco + rel_cent, f",{centavos}")

  c.setFont("Arial-Black", f_un)
  c.drawCentredString(x_fim + (w_cent / 2), y_preco + rel_un,
                      item.get("un", "1 UN"))
