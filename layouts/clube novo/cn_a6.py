from reportlab.lib.colors import black
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit

# =====================================================================
# CLUBE NOVO - A6 (6 por folha A4), papel pré-impresso
#
# O papel já traz o amarelo, o azul e o logo. Aqui só entra o texto preto,
# e ele precisa cair dentro das formas impressas - por isso as posições
# são fixas, medidas no PDF oficial de uma célula de 105 x 99 mm.
# Todas as medidas são FRAÇÕES da célula, para acompanhar se ela mudar.
# =====================================================================
CEL_W_REF, CEL_H_REF = 105.0, 99.0

# Fonte da marca. O app registra "Identidad" no início; se por algum motivo
# ela não estiver disponível, cai na Arial-Black e o cartaz continua saindo.
FONTE = "Identidad"

# --- Descrição ---
# Não é centralizada na célula: fica em 45,3mm de 105, para desviar da
# forma amarela do papel.
# As alturas abaixo são LINHAS DE BASE reais. As medidas tiradas do PDF
# oficial vinham como base da caixa do texto (que inclui a descida de "ç" e
# "$"); usá-las direto deixava tudo 1 a 2,5mm abaixo do lugar.
F_DESC_CENTRO = 45.3 / CEL_W_REF
F_DESC_LARGURA = 84.0 / CEL_W_REF   # limite antes de encostar na borda
F_DESC_BASE = 41.02 / CEL_H_REF      # linha de base da 1ª linha
F_DESC_ESPACO = 5.3 / CEL_H_REF     # entre as linhas
FONTE_DESC = 15                     # tamanho inicial; REDUZ até caber
MAX_LINHAS_DESC = 2

# --- Preço normal (forma branca, à esquerda) ---
F_N_CENTRO = 26.6 / CEL_W_REF       # centro do conjunto dígitos+centavos
F_N_BASE = 80.76 / CEL_H_REF
F_N_RS_X = 6.6 / CEL_W_REF
F_N_RS_BASE = 67.85 / CEL_H_REF
F_N_CENT_BASE = 74.48 / CEL_H_REF   # centavos têm linha própria no oficial
F_N_UN_BASE = 81.24 / CEL_H_REF
FONTE_N = 45
FONTE_N_CENT = 22.5

# --- Preço do clube (forma amarela, à direita) ---
F_C_CENTRO = 75.7 / CEL_W_REF
F_C_BASE = 80.27 / CEL_H_REF
F_C_RS_X = 49.3 / CEL_W_REF
F_C_RS_BASE = 62.25 / CEL_H_REF
F_C_CENT_BASE = 71.44 / CEL_H_REF
F_C_UN_BASE = 81.54 / CEL_H_REF
FONTE_C = 60
FONTE_C_CENT = 30

FONTE_RS = 13.5
FONTE_UN = 11.2

# Largura máxima de cada conjunto de preço, para não invadir a outra forma
F_N_LARGURA = 40.0 / CEL_W_REF
F_C_LARGURA = 47.0 / CEL_W_REF
# =====================================================================


def separar_valor(bruto):
  """Aceita 7,98 / 1.548,00 / 1548 - o último separador é o decimal."""
  bruto = (bruto or "0,00").strip().replace(" ", "")
  corte = max(bruto.rfind(","), bruto.rfind("."))
  if corte == -1:
    inteiro, centavos = bruto, "00"
  else:
    inteiro, centavos = bruto[:corte], bruto[corte + 1:][:2]
  inteiro = inteiro.replace(".", "").replace(",", "") or "0"
  return inteiro, (centavos + "00")[:2]


def desenhar_preco(c, valor, unidade, x_centro, y_base, f_real, f_cent,
                   x_rs, y_rs, y_cent, y_un, f_rs, f_un, largura_max):
  """Desenha R$ + dígitos + centavos + unidade.

  O conjunto dígitos+centavos fica centralizado em x_centro, como no
  modelo oficial: assim um preço de 1 ou de 3 dígitos continua dentro da
  forma impressa. Só os dígitos encolhem se o valor for largo demais.
  """
  inteiro, centavos = separar_valor(valor)

  while f_real > 12:
    w_int = c.stringWidth(inteiro, FONTE, f_real)
    w_cent = c.stringWidth(f",{centavos}", FONTE, f_cent)
    if (w_int + w_cent) <= largura_max:
      break
    f_real -= 1
    f_cent = f_real * 0.5

  total = w_int + w_cent
  x = x_centro - (total / 2)

  c.setFont(FONTE, f_rs)
  c.drawString(x_rs, y_rs, "R$")

  c.setFont(FONTE, f_real)
  c.drawString(x, y_base, inteiro)

  # Os centavos têm linha de base própria no modelo oficial. Calculada por
  # proporção, ela caía 2,5mm mais baixo e encostava no "1 UN".
  c.setFont(FONTE, f_cent)
  c.drawString(x + w_int, y_cent, f",{centavos}")

  # unidade centralizada sob os centavos, como no oficial
  c.setFont(FONTE, f_un)
  c.drawCentredString(x + w_int + (w_cent / 2), y_un, unidade)


def desenhar_etiqueta_clube(c, item, x_base, y_base, col_w, row_h, scale=1.0):
  """Cartaz do Clube Novo - preço normal + preço exclusivo do clube."""
  topo = y_base + row_h
  kx, ky = col_w / (CEL_W_REF * mm), row_h / (CEL_H_REF * mm)

  c.setFillColor(black)

  # --- 1. DESCRIÇÃO (reduz até caber; no oficial ela era fixa em 15pt e
  #        os nomes compridos saíam cortados na impressão) ---
  desc = (item.get("desc", "") or "").upper()
  largura_max = col_w * F_DESC_LARGURA
  tam = FONTE_DESC * kx
  linhas = []
  while tam > 6:
    linhas = simpleSplit(desc, FONTE, tam, largura_max)
    if len(linhas) <= MAX_LINHAS_DESC:
      break
    tam -= 0.5
  linhas = linhas[:MAX_LINHAS_DESC]

  x_desc = x_base + (col_w * F_DESC_CENTRO)
  y = topo - (row_h * F_DESC_BASE)
  c.setFont(FONTE, tam)
  for linha in linhas:
    c.drawCentredString(x_desc, y, linha)
    y -= row_h * F_DESC_ESPACO

  unidade = item.get("un", "1 UN")

  # --- 2. PREÇO NORMAL (forma branca) ---
  desenhar_preco(
      c, item.get("de") or item.get("por"), unidade,
      x_base + (col_w * F_N_CENTRO), topo - (row_h * F_N_BASE),
      FONTE_N * kx, FONTE_N_CENT * kx,
      x_base + (col_w * F_N_RS_X), topo - (row_h * F_N_RS_BASE),
      topo - (row_h * F_N_CENT_BASE), topo - (row_h * F_N_UN_BASE),
      FONTE_RS * kx, FONTE_UN * kx, col_w * F_N_LARGURA,
  )

  # --- 3. PREÇO DO CLUBE (forma amarela) ---
  desenhar_preco(
      c, item.get("por"), unidade,
      x_base + (col_w * F_C_CENTRO), topo - (row_h * F_C_BASE),
      FONTE_C * kx, FONTE_C_CENT * kx,
      x_base + (col_w * F_C_RS_X), topo - (row_h * F_C_RS_BASE),
      topo - (row_h * F_C_CENT_BASE), topo - (row_h * F_C_UN_BASE),
      FONTE_RS * kx, FONTE_UN * kx, col_w * F_C_LARGURA,
  )
