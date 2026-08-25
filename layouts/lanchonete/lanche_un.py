from reportlab.lib.colors import black, HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics

# =====================================================================
# AJUSTES RÁPIDOS
# =====================================================================
MARGEM_LATERAL = 4 * mm      # respiro dentro da célula
DESC_TOPO = 11.2 * mm        # linha de base da 1ª linha da descrição
FONTE_DESC = 20              # tamanho inicial (reduz se precisar)
MAX_LINHAS_DESC = 4
ESPACO_LINHA = 8 * mm        # entre as linhas da descrição

PRECO_BASE = 68.5 * mm       # linha de base do preço, medida do TOPO da célula
FONTE_PRECO = 80             # tamanho inicial dos reais
X_RS = 6.3 * mm              # onde começa o "R$"
RS_BASE = 48.6 * mm          # linha de base do "R$", medida do TOPO da célula
X_PRECO = 20.6 * mm          # onde começam os dígitos

COR_LINHA = HexColor("#B0B0B0")   # linhas de corte
# =====================================================================


def altura_digitos(fonte, tamanho):
  return pdfmetrics.getFont(fonte).face.capHeight / 1000.0 * tamanho


def separar_valor(bruto):
  """Aceita 7,98 / 1.548,00 / 1548 — o último separador é o decimal."""
  bruto = (bruto or "0,00").strip().replace(" ", "")
  corte = max(bruto.rfind(","), bruto.rfind("."))
  if corte == -1:
    inteiro, centavos = bruto, "00"
  else:
    inteiro, centavos = bruto[:corte], bruto[corte + 1:][:2]
  inteiro = inteiro.replace(".", "").replace(",", "") or "0"
  return inteiro, (centavos + "00")[:2]


def fontes_do_preco(f_real):
  return (f_real,
          max(8, round(f_real * 0.50)),   # centavos
          max(8, round(f_real * 0.40)),   # R$
          max(8, round(f_real * 0.30)))   # UN


def desenhar_etiqueta_padaria(c, item, x_base, y_base, col_w, row_h, scale=1.0):
  """Etiqueta da padaria - produto vendido por UNIDADE.

  x_base / y_base são o canto inferior esquerdo da célula.
  """
  topo = y_base + row_h                      # borda superior da célula
  x_centro = x_base + (col_w / 2)
  largura_util = col_w - (2 * MARGEM_LATERAL)

  # --- 1. DESCRIÇÃO (reduz até caber nas linhas disponíveis) ---
  tam = FONTE_DESC
  desc = (item.get("desc", "") or "").upper()
  linhas = []
  while tam > 8:
    linhas = simpleSplit(desc, "Arial-Black", tam, largura_util)
    if len(linhas) <= MAX_LINHAS_DESC:
      break
    tam -= 1
  linhas = linhas[:MAX_LINHAS_DESC]

  c.setFillColor(black)
  c.setFont("Arial-Black", tam)
  y = topo - DESC_TOPO
  for linha in linhas:
    c.drawCentredString(x_centro, y, linha)
    y -= ESPACO_LINHA

  # --- 2. PREÇO (posição fixa, como no modelo oficial) ---
  inteiro, centavos = separar_valor(item.get("por"))
  unidade = item.get("un", "UN")

  f_real, f_cent, f_rs, f_un = fontes_do_preco(FONTE_PRECO)

  # se o valor for largo demais, o conjunto encolhe de 1 em 1 ponto
  def largura(fr, fc):
    return (c.stringWidth(inteiro, "Arial-Black", fr)
            + c.stringWidth(f",{centavos}", "Arial-Black", fc))

  # a unidade fica ancorada na margem direita, então o preço tem que caber
  # ANTES dela - senão um valor largo passa por baixo do "UN"
  larg_un = c.stringWidth(unidade, "Arial-Black", f_un) + (3 * mm)
  disponivel = col_w - X_PRECO - MARGEM_LATERAL - larg_un
  while f_real > 30 and largura(f_real, f_cent) > disponivel:
    f_real -= 1
    f_real, f_cent, f_rs, f_un = fontes_do_preco(f_real)

  y_preco = topo - PRECO_BASE

  # o "R$" tem posição própria no modelo oficial, não derivada do preço:
  # calculado por proporção ele descia 5mm e encostava no número
  c.setFont("Arial-Black", f_rs)
  c.drawString(x_base + X_RS, topo - RS_BASE, "R$")

  c.setFont("Arial-Black", f_real)
  c.drawString(x_base + X_PRECO, y_preco, inteiro)
  w_int = c.stringWidth(inteiro, "Arial-Black", f_real)

  rel_cent = f_real - f_cent - (f_real * 0.12)
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_base + X_PRECO + w_int, y_preco + rel_cent, f",{centavos}")
  w_cent = c.stringWidth(f",{centavos}", "Arial-Black", f_cent)

  # ancorada à direita: assim nunca escapa da célula, seja qual for a largura
  c.setFont("Arial-Black", f_un)
  c.drawRightString(x_base + col_w - MARGEM_LATERAL, y_preco, unidade)


def desenhar_linhas_corte(c, x, y, largura, altura):
  """Moldura da célula, para saber onde recortar."""
  c.setStrokeColor(COR_LINHA)
  c.setLineWidth(0.5)
  c.rect(x, y, largura, altura, stroke=1, fill=0)
