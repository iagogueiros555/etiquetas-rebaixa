from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit


def desenhar_etiqueta_a4(c, item, x_base, y_base, col_w, row_h, scale):
  page_w = col_w
  page_h = row_h

  # --- 1. MARGEM SUPERIOR DE 69 MM ATÉ A DESCRIÇÃO ---
  margem_topo_pts = 69 * mm
  y_atual = page_h - margem_topo_pts

  # --- 2. DESCRIÇÃO DO PRODUTO (Fonte 56pt e Margens de 8mm) ---
  tamanho_fonte_desc = 56
  c.setFont("Arial-Black", tamanho_fonte_desc)
  desc = item.get("desc", "")

  margem_lateral = 8 * mm
  largura_util = page_w - (2 * margem_lateral)

  # Quebra o texto respeitando a largura entre as margens
  linhas_desc = simpleSplit(desc, "Arial-Black", tamanho_fonte_desc, largura_util)

  for linha in linhas_desc:
    c.drawCentredString(page_w / 2, y_atual, linha)
    y_atual -= tamanho_fonte_desc + 2  # Espaçamento de linha justo para fonte 56

  # Espaço de transição para o preço
  y_atual -= 20

  # --- 3. PREÇO (R$ e Valor Principal) ---
  c.setFont("Arial-Black", 30)
  c.drawCentredString(page_w / 2, y_atual, "R$")
  y_atual -= 75

  c.setFont("Arial-Black", 110)
  por_str = item.get("por", "0,00")
  c.drawCentredString(page_w / 2, y_atual, por_str)
  y_atual -= 35

  c.setFont("Arial-Black", 24)
  un_str = item.get("un", "1 UN")
  c.drawCentredString(page_w / 2, y_atual, un_str)
  y_atual -= 45

  # --- 4. AVISO DE VENCIMENTO ---
  c.setFont("Arial-Black", 26)
  c.drawCentredString(page_w / 2, y_atual, "PRODUTO PRÓXIMO A")
  y_atual -= 30
  c.drawCentredString(page_w / 2, y_atual, "DATA DE VENCIMENTO")
  y_atual -= 40

  # --- 5. BLOCO DE VALIDADE COM FUNDO CINZA ---
  val_str = item.get("val", "")
  if val_str:
    texto_validade = f"VALIDADE: {val_str}"

    largura_faixa = page_w - (2 * margem_lateral)
    altura_faixa = 45
    x_faixa = margem_lateral
    y_faixa = y_atual - 10

    c.setFillColor(lightgrey)
    c.rect(x_faixa, y_faixa, largura_faixa, altura_faixa, stroke=0, fill=1)

    c.setFillColor(black)
    c.setFont("Arial-Black", 28)
    c.drawCentredString(page_w / 2, y_atual, texto_validade)
