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
F_DESC_MARGEM = 6.1 / 74.9   # respiro entre o topo da célula e a descrição
F_GAP_DESC_PRECO = 2.5 / 74.9  # respiro mínimo entre a descrição e o "R$"
F_ESPACO_LINHA = 8.0 / 74.9  # entre as linhas da descrição
# Medidas conferidas no PDF oficial (célula de 74,9mm):
F_X_RS = 6.9 / 74.9          # onde começa o "R$"
F_RS_BASE = 48.4 / 74.9      # linha de base do "R$"
F_X_PRECO = 20.8 / 74.9      # onde começam os dígitos
F_PRECO_BASE = 65.7 / 74.9   # linha de base dos DÍGITOS. Cuidado: o pé da
                             # vírgula desce até 68,5mm, e usar esse valor
                             # empurrava o preço todo 2,8mm para baixo.

FONTE_DESC = 20              # tamanhos de referência, reescalados pela célula
MAX_LINHAS_DESC = 4
FONTE_PRECO = 80
F_FONTE_RS = 0.34            # "R$" como fração do tamanho dos dígitos
F_FONTE_UN = 0.22            # unidade como fração do tamanho dos dígitos
F_UN_DESCE = 1.5 / 160      # unidade abaixo da linha dos dígitos (oficial)
F_UN_DIREITA = 4.0 / 74.9    # desloca a unidade para a direita (negativo = esquerda)
F_MARGEM_PRECO = 2.0 / 74.9  # respiro à direita da linha do preço (menor que
                             # o das outras linhas, para o valor ficar grande)

COR_LINHA = HexColor("#B0B0B0")   # linhas de corte
# =====================================================================


def altura_letras(tamanho):
  """Altura real das maiúsculas, para centralizar o bloco de texto."""
  return pdfmetrics.getFont("Arial-Black").face.capHeight / 1000.0 * tamanho
# =====================================================================


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

  # O bloco fica CENTRALIZADO entre o topo da célula e o "R$", em vez de
  # ancorado no alto. Ancorado, um nome de 1 linha deixava um vazio enorme
  # até o preço, enquanto um de 4 linhas quase encostava nele - dois
  # cartazes lado a lado ficavam com aparências bem diferentes.
  f_rs = max(8, round(FONTE_PRECO * F_FONTE_RS * k))
  topo_rs = (topo - (row_h * F_RS_BASE)) + altura_letras(f_rs)

  area_topo = topo - (row_h * F_DESC_MARGEM)
  area_base = topo_rs + (row_h * F_GAP_DESC_PRECO)

  espaco = row_h * F_ESPACO_LINHA
  altura_bloco = ((len(linhas) - 1) * espaco) + altura_letras(tam)
  centro_area = (area_topo + area_base) / 2

  c.setFillColor(black)
  c.setFont("Arial-Black", tam)
  y = centro_area + (altura_bloco / 2) - altura_letras(tam)
  for linha in linhas:
    c.drawCentredString(x_centro, y, linha)
    y -= espaco

  # --- 2. PREÇO ---
  inteiro, centavos = separar_valor(item.get("por"))
  unidade = (item.get("un") or "UN").strip()

  f_un = max(8, round(FONTE_PRECO * F_FONTE_UN * k))
  f_real = max(8, round(FONTE_PRECO * k))
  f_cent = max(8, round(f_real * 0.50))

  x_preco = x_base + (col_w * F_X_PRECO)
  w_un = c.stringWidth(unidade, "Arial-Black", f_un)

  # Só os dígitos cedem espaço: "R$" e unidade ficam do tamanho oficial,
  # senão um preço de 3 casas miniaturiza o cartaz inteiro. A unidade fica
  # sob os centavos, então não disputa largura com o preço.
  disponivel = (x_base + col_w - (col_w * F_MARGEM_PRECO)) - x_preco

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

  # A unidade fica CENTRALIZADA sob os centavos, não depois deles: ao lado
  # ela ficava longe na diagonal, porque os centavos são elevados.
  c.setFont("Arial-Black", f_un)
  x_un = x_preco + w_int + (w_cent / 2) + (col_w * F_UN_DIREITA)

  # Trava: nomes compridos ("PORCAO", "BANDEJA") somados ao deslocamento
  # passavam da borda e saíam cortados na impressão.
  limite = x_base + col_w - (col_w * F_MARGEM_PRECO) - (w_un / 2)
  minimo = x_base + margem + (w_un / 2)
  x_un = max(minimo, min(x_un, limite))

  c.drawCentredString(x_un, y_preco - (row_h * F_UN_DESCE), unidade)
