from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import mm


def desenhar_etiqueta_a4(c, item, x_base, y_base, col_w, row_h, scale):
  # Dimensões da página A4 base
  page_w = col_w
  page_h = row_h

  # --- 1. MARGEM SUPERIOR DE 69 MM ATÉ A DESCRIÇÃO ---
  # Margem de cima fixa em 69 mm convertida para pontos
  margem_topo_pts = 69 * mm
  y_atual = page_h - margem_topo_pts

  # --- 2. DESCRIÇÃO DO PRODUTO ---
  c.setFont("Arial-Black", int(26 * scale))
  desc = item.get("desc", "")

  # Quebra o texto da descrição caso seja muito longo para caber na largura da página
  from reportlab.lib.utils import simpleSplit

  linhas_desc = simpleSplit(desc, "Arial-Black", int(26 * scale), page_w - 40)

  for linha in linhas_desc:
    c.drawCentredString(page_w / 2, y_atual, linha)
    y_atual -= int(32 * scale)  # Espaçamento entre as linhas da descrição

  # Espaço extra após a descrição
  y_atual -= int(15 * scale)

  # --- 3. PREÇO (R$ e Valor Principal) ---
  # R$ menorzinho logo acima ou ao lado
  c.setFont("Arial-Black", int(20 * scale))
  c.drawCentredString(page_w / 2, y_atual, "R$")
  y_atual -= int(25 * scale)

  # Valor grande (POR)
  c.setFont("Arial-Black", int(90 * scale))
  por_str = item.get("por", "0,00")
  c.drawCentredString(page_w / 2, y_atual, por_str)
  y_atual -= int(25 * scale)

  # Unidade (EX: 1 UN)
  c.setFont("Arial-Black", int(18 * scale))
  un_str = item.get("un", "1 UN")
  c.drawCentredString(page_w / 2, y_atual, un_str)
  y_atual -= int(40 * scale)

  # --- 4. AVISO DE VENCIMENTO ---
  c.setFont("Arial-Black", int(22 * scale))
  c.drawCentredString(
      page_w / 2, y_atual, "PRODUTO PRÓXIMO A"
  )  # Corrigido string solta
  y_atual -= int(26 * scale)
  c.drawCentredString(page_w / 2, y_atual, "DATA DE VENCIMENTO")
  y_atual -= int(35 * scale)

  # --- 5. BLOCO DE VALIDADE COM FUNDO CINZA ---
  val_str = item.get("val", "")
  if val_str:
    texto_validade = f"VALIDADE: {val_str}"

    # Desenha a faixa cinza de fundo
    largura_faixa = page_w - 60
    altura_faixa = int(35 * scale)
    x_faixa = 30
    y_faixa = y_atual - 5

    c.setFillColor(lightgrey)
    c.rect(
        x_faixa, y_faixa, largura_faixa, altura_faixa, stroke=0, fill=1
    )  # Corrigido preenchimento do rect

    # Texto da validade em cima da faixa
    c.setFillColor(black)
    c.setFont("Arial-Black", int(22 * scale))
    c.drawCentredString(
        page_w / 2, y_atual + int(6 * scale), texto_validade
    )  # Corrigido string solta

  # Opcional: Rodapé com código de barras/sistema pode vir abaixo se houver espaço
