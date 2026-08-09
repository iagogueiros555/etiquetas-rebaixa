from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit


def desenhar_etiqueta_a4(c, item, x_base, y_base, col_w, row_h, scale):
  page_w = col_w
  page_h = row_h

  margem_lateral = 8 * mm
  largura_util = page_w - (2 * margem_lateral)

  # --- 1. MARGEM SUPERIOR DE 69 MM ATÉ A DESCRIÇÃO ---
  y_atual = page_h - (69 * mm)

  # --- 2. DESCRIÇÃO DO PRODUTO (Fonte 56pt) ---
  tamanho_fonte_desc = 56
  c.setFont("Arial-Black", tamanho_fonte_desc)
  desc = item.get("desc", "")

  linhas_desc = simpleSplit(desc, "Arial-Black", tamanho_fonte_desc, largura_util)
  for linha in linhas_desc:
    c.drawCentredString(page_w / 2, y_atual, linha)
    y_atual -= tamanho_fonte_desc + 2

  y_atual -= 15  # Recuo de segurança antes do bloco do preço

  # --- 3. BLOCO DO PREÇO DINÂMICO ---
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
    f_real, f_cent, f_rs, f_un = 208, 92, 42, 21
  elif num_digitos == 3:
    f_real, f_cent, f_rs, f_un = 160, 72, 36, 18
  else:
    f_real, f_cent, f_rs, f_un = 120, 54, 28, 16

  w_real = c.stringWidth(inteiro_str, "Arial-Black", f_real)
  w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)

  # Ajuste na largura total considerando a aproximação dos centavos (-8pts)
  largura_total_preco = (w_real - 8) + w_cent

  if largura_total_preco > largura_util:
    fator_red = largura_util / largura_total_preco
    f_real = int(f_real * fator_red)
    f_cent = int(f_cent * fator_red)
    f_rs = int(f_rs * fator_red)
    f_un = int(f_un * fator_red)
    w_real = c.stringWidth(inteiro_str, "Arial-Black", f_real)
    w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)
    largura_total_preco = (w_real - 8) + w_cent

  x_inicio_real = (page_w - largura_total_preco) / 2
  y_linha_base_preco = y_atual - f_real + 50

  # A) R$: Subiu 2mm (~5.6 pts) em relação à posição anterior
  c.setFont("Arial-Black", f_rs)
  c.drawString(x_inicio_real, y_linha_base_preco + f_real - 39, "R$")

  # B) VALOR REAL (Inteiro)
  c.setFont("Arial-Black", f_real)
  c.drawString(x_inicio_real, y_linha_base_preco, inteiro_str)

  # C) CENTAVOS (,XX): Puxados 8px para a esquerda (mais próximos do número real)
  x_centavos = x_inicio_real + w_real - 8
  y_centavos = y_linha_base_preco + (f_real - f_cent) - 35
  c.setFont("Arial-Black", f_cent)
  c.drawString(x_centavos, y_centavos, f",{centavos_str}")

  # D) UNIDADE: Afastada mais 4mm (~11.3 pts) para baixo dos centavos
  x_unidade = x_centavos + (w_cent / 2)
  y_unidade = y_centavos - 36
  c.setFont("Arial-Black", f_un)
  un_str = item.get("un", "1 UN")
  c.drawCentredString(x_unidade, y_unidade, un_str)

  # Ponteiro Y ajustado para o aviso de vencimento
  y_atual = y_linha_base_preco - 20

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
