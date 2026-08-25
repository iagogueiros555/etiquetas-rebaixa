from reportlab.lib.colors import black, HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics

# =====================================================================
# AJUSTES RÁPIDOS
# =====================================================================
# Todas as medidas são FRAÇÕES da célula, tiradas do modelo oficial de
# 74,9 x 74,9 mm. Assim o cartaz fica idêntico se um dia a célula mudar de
# tamanho - foi o que quebrou quando passamos de 75mm para 70mm usando
# medidas absolutas: o preço encolheu para caber.
CELULA_REF = 74.9 * mm

F_MARGEM = 4.0 / 74.9        # respiro lateral dentro da célula
F_DESC_TOPO = 11.2 / 74.9    # linha de base da 1ª linha da descrição
F_ESPACO_LINHA = 8.0 / 74.9  # entre as linhas da descrição
F_X_RS = 6.3 / 74.9          # onde começa o "R$"
F_RS_BASE = 48.6 / 74.9      # linha de base do "R$"
F_X_PRECO = 20.6 / 74.9      # onde começam os dígitos
F_PRECO_BASE = 68.5 / 74.9   # linha de base do preço

FONTE_DESC = 20              # tamanhos de referência, reescalados pela célula
MAX_LINHAS_DESC = 4
FONTE_PRECO = 80
GAP_UNIDADE = 3.0 / 74.9     # entre os centavos e a unidade
F_MARGEM_PRECO = 2.0 / 74.9  # respiro à direita da linha do preço (menor que
                             # o das outras linhas, para o valor ficar grande)

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
  """Etiqueta da lanchonete - produto vendido por UNIDADE.

  x_base / y_base são o canto inferior esquerdo da célula. A moldura de
  corte é desenhada aqui dentro, para o app não precisar saber que este
  formato tem linhas de recorte.
  """
  c.setStrokeColor(COR_LINHA)
  c.setLineWidth(0.5)
  c.rect(x_base, y_base, col_w, row_h, stroke=1, fill=0)

  # tudo escala junto com a célula, tomando a oficial como referência
  k = col_w / CELULA_REF
  margem = col_w * F_MARGEM
  topo = y_base + row_h
  x_centro = x_base + (col_w / 2)
  largura_util = col_w - (2 * margem)

  # --- 1. DESCRIÇÃO (reduz até caber nas linhas disponíveis) ---
  tam = max(6, round(FONTE_DESC * k))
  desc = (item.get("desc", "") or "").upper()
  linhas = []
  while tam > 6:
    linhas = simpleSplit(desc, "Arial-Black", tam, largura_util)
    if len(linhas) <= MAX_LINHAS_DESC:
      break
    tam -= 1
  linhas = linhas[:MAX_LINHAS_DESC]

  c.setFillColor(black)
  c.setFont("Arial-Black", tam)
  y = topo - (row_h * F_DESC_TOPO)
  for linha in linhas:
    c.drawCentredString(x_centro, y, linha)
    y -= row_h * F_ESPACO_LINHA

  # --- 2. PREÇO ---
  inteiro, centavos = separar_valor(item.get("por"))
  unidade = (item.get("un") or "UN").strip()

  f_rs = max(8, round(FONTE_PRECO * 0.40 * k))
  f_un = max(8, round(FONTE_PRECO * 0.30 * k))
  f_real = max(8, round(FONTE_PRECO * k))
  f_cent = max(8, round(f_real * 0.50))

  x_preco = x_base + (col_w * F_X_PRECO)
  gap_un = col_w * GAP_UNIDADE
  w_un = c.stringWidth(unidade, "Arial-Black", f_un)

  # O conjunto (dígitos + centavos + unidade) precisa caber entre o início
  # do preço e a margem direita. Só os dígitos cedem: "R$" e unidade ficam
  # do tamanho oficial, senão um preço de 3 casas miniaturiza o cartaz.
  disponivel = ((x_base + col_w - (col_w * F_MARGEM_PRECO))
                - x_preco - gap_un - w_un)

  def largura_valor(fr, fc):
    return (c.stringWidth(inteiro, "Arial-Black", fr)
            + c.stringWidth(f",{centavos}", "Arial-Black", fc))

  while f_real > 20 and largura_valor(f_real, f_cent) > disponivel:
    f_real -= 1
    f_cent = max(8, round(f_real * 0.50))

  y_preco = topo - (row_h * F_PRECO_BASE)

  c.setFont("Arial-Black", f_rs)
  c.drawString(x_base + (col_w * F_X_RS), topo - (row_h * F_RS_BASE), "R$")

  c.setFont("Arial-Black", f_real)
  c.drawString(x_preco, y_preco, inteiro)
  w_int = c.stringWidth(inteiro, "Arial-Black", f_real)

  rel_cent = f_real - f_cent - (f_real * 0.12)
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_preco + w_int, y_preco + rel_cent, f",{centavos}")
  w_cent = c.stringWidth(f",{centavos}", "Arial-Black", f_cent)

  c.setFont("Arial-Black", f_un)
  c.drawString(x_preco + w_int + w_cent + gap_un, y_preco, unidade)
