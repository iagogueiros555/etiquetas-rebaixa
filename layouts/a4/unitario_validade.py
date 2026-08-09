from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit


def desenhar_etiqueta_a4(c, item, x_base, y_base, col_w, row_h, scale):
  page_w = col_w
  page_h = row_h

  # --- 1. MARGEM SUPERIOR DE 69 MM ATÉ A DESCRIÇÃO ---
  margem_topo_pts = 69 * mm
  y_atual = page_h - margem_topo_pts

  # --- 2. DESCRIÇÃO DO PRODUTO (Fonte 58 e Margens Laterais de 8mm) ---
  tamanho_fonte_desc = int(58 * scale)
  c.setFont("Arial-Black", tamanho_fonte_desc)
  desc = item.get("desc", "")

  # Margem lateral de 8mm de cada lado (total de 16mm de recuo na largura útil)
  margem_lateral = 8 * mm
  largura_util = page_w - (2 * margem_lateral)

  # Quebra o texto respeitando a largura útil entre as margens de 8mm
  linhas_desc = simpleSplit(desc, "Arial-Black", tamanho_fonte_desc, largura_util)

  for linha in linhas_desc:
    # Centralizado dentro da largura útil delimitada pelas margens laterais
    c.drawCentredString(page_w / 2, y_atual, linha)
    y_atual -= int(
        tamanho_fonte_desc * 1.1 * scale
    )  # Espaçamento proporcional dinâmico entre as linhas

  # Espaço extra após a descrição
  y_atual -= int(15 * scale)

  # --- 3. PREÇO (R$ e Valor Principal) ---
  c.setFont("Arial-Black", int(20 * scale))
  c.drawCentredString(page_w / 2, y_atual, "R$")
  y_atual -= int(25 * scale)

  c.setFont("Arial-Black", int(90 * scale))
  por_str = item.get("por", "0,00")
  c.drawCentredString(page_w / 2, y_atual, por_str)
  y_atual -= int(25 * scale)

  c.setFont("Arial-Black", int(18 * scale))
  un_str = item.get("un", "1 UN")
  c.drawCentredString(page_w / 2, y_atual, un_str)
  y_atual -= int(40 * scale)

  # --- 4. AVISO DE VENCIMENTO ---
  c.setFont("Arial-Black", int(22 * scale))
  c.drawCentredString(page_w / 2, y_atual, "PRODUTO PRÓXIMO A")
  y_atual -= int(26 * scale)
  c.drawCentredString(page_w / 2, y_atual, "DATA DE VENCIMENTO")
  y_atual -= int(35 * scale)

  # --- 5. BLOCO DE VALIDADE COM FUNDO CINZA ---
  val_str = item.get("val", "")
  if val_str:
    texto_validade = f"VALIDADE: {val_str}"

    largura_faixa = page_w - (2 * margem_lateral)
    altura_faixa = int(35 * scale)
    x_faixa = margem_lateral
    y_faixa = y_atual - 5

    c.setFillColor(lightgrey)
    c.rect(x_faixa, y_faixa, largura_faixa, altura_faixa, stroke=0, fill=1)

    c.setFillColor(black)
    c.setFont("Arial-Black", int(22 * scale))
    c.drawCentredString(page_w / 2, y_atual + int(6 * scale), texto_validade)
