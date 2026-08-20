from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics

# =====================================================================
# AJUSTES RÁPIDOS - mexa aqui para afinar depois dos testes de impressão
# =====================================================================
MARGEM_TOPO = 83 * mm       # do topo até a 1ª linha da descrição
                            # (a faixa vermelha termina a 64mm)
MARGEM_LATERAL = 8 * mm     # respiro nas laterais
FONTE_DESC = 56             # tamanho inicial da descrição (reduz se precisar)
MAX_LINHAS_DESC = 2         # nome nunca passa disso: reduz a fonte até caber

ESPACO_ENTRE_BLOCOS = 20 * mm   # vão entre o bloco "De" e o bloco "Por"
GAP_ROTULO_POR = 8 * mm         # entre os rótulos "Por/R$" e o valor grande
GAP_ROTULO_DE = 1.5 * mm        # entre os rótulos "De/R$" e o valor riscado
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
  bruto = (bruto or "0,00").strip().replace(".", ",")
  if "," in bruto:
    partes = bruto.split(",")
    return partes[0], partes[1][:2]
  return bruto, "00"


def desenhar_etiqueta_a4h(c, item, x_base, y_base, col_w, row_h, scale):
  """Etiqueta A4 HORIZONTAL - Promocional (De / Por), sem validade."""
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

  linhas_desc = linhas_desc[:MAX_LINHAS_DESC]  # trava: nunca desenha uma 3ª linha
  c.setFont("Arial-Black", tam_fonte_desc)

  espacamento_desc = tam_fonte_desc + 2
  y_linha = y_base + page_h - MARGEM_TOPO
  for linha in linhas_desc:
    c.drawCentredString(x_centro, y_linha, linha)
    y_linha -= espacamento_desc

  limite_superior_preco = y_linha + espacamento_desc  # linha de base da última linha
  limite_inferior_preco = y_base                      # sem tarja embaixo

  # --- 2. TAMANHOS DOS DOIS BLOCOS ---
  de_int, de_cent = separar_valor(item.get("de"))
  por_int, por_cent = separar_valor(item.get("por"))

  n_por = len(por_int)
  if n_por <= 2:
    f_por, f_por_cent, f_por_rot, f_por_un = 280, 140, 47, 34
  elif n_por == 3:
    f_por, f_por_cent, f_por_rot, f_por_un = 230, 115, 42, 30
  else:
    f_por, f_por_cent, f_por_rot, f_por_un = 190, 95, 38, 26

  n_de = len(de_int)
  if n_de <= 2:
    f_de, f_de_cent, f_de_rot, f_de_un = 100, 50, 24, 24
  elif n_de == 3:
    f_de, f_de_cent, f_de_rot, f_de_un = 85, 42, 22, 22
  else:
    f_de, f_de_cent, f_de_rot, f_de_un = 72, 36, 20, 20

  esp_blocos = ESPACO_ENTRE_BLOCOS
  gap_por = GAP_ROTULO_POR
  gap_de = GAP_ROTULO_DE
  folga_cent_por = -15
  folga_cent_de = -6

  def medir():
    w_rot_de = max(c.stringWidth("De", "Arial-Black", f_de_rot),
                   c.stringWidth("R$", "Arial-Black", f_de_rot))
    w_val_de = (calcular_largura_inteiro_forcado(c, de_int, "Arial-Black", f_de)
                + folga_cent_de
                + c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent))
    w_rot_por = max(c.stringWidth("Por", "Arial-Black", f_por_rot),
                    c.stringWidth("R$", "Arial-Black", f_por_rot))
    w_val_por = (calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
                 + folga_cent_por
                 + c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent))
    bloco_de = w_rot_de + gap_de + w_val_de
    bloco_por = w_rot_por + gap_por + w_val_por
    return w_rot_de, w_val_de, w_rot_por, w_val_por, bloco_de, bloco_por, bloco_de + esp_blocos + bloco_por

  w_rot_de, w_val_de, w_rot_por, w_val_por, bloco_de, bloco_por, largura_total = medir()

  # Trava de segurança: com 2 ou 3 dígitos os dois blocos juntos passam da
  # margem, então tudo encolhe junto até caber.
  if largura_total > largura_util:
    fator = largura_util / largura_total
    f_por = int(f_por * fator); f_por_cent = int(f_por_cent * fator)
    f_por_rot = int(f_por_rot * fator); f_por_un = int(f_por_un * fator)
    f_de = int(f_de * fator); f_de_cent = int(f_de_cent * fator)
    f_de_rot = int(f_de_rot * fator); f_de_un = int(f_de_un * fator)
    esp_blocos *= fator; gap_por *= fator; gap_de *= fator
    folga_cent_por = int(folga_cent_por * fator); folga_cent_de = int(folga_cent_de * fator)
    w_rot_de, w_val_de, w_rot_por, w_val_por, bloco_de, bloco_por, largura_total = medir()

  # --- 3. POSIÇÕES VERTICAIS (relativas à linha de base do valor "Por") ---
  # Proporções tiradas do cartaz oficial da loja.
  rel_rot_por = f_por * 0.52          # rótulo "Por"
  rel_rs_por = f_por * 0.325          # rótulo "R$" logo abaixo
  rel_cent_por = f_por - f_por_cent - (f_por * 0.12)
  rel_un_por = rel_cent_por - f_por_un - (8 * mm)

  desloc_de = f_por * 0.29            # o "De" fica acima da linha do "Por"
  rel_rot_de = f_de * 0.44
  rel_rs_de = f_de * 0.14
  rel_cent_de = f_de - f_de_cent - (f_de * 0.12)
  rel_un_de = -(altura_digitos("Arial-Black", f_de_un) + 1 * mm)  # "1 UN" abaixo

  topo_rel = max(
      altura_digitos("Arial-Black", f_por),
      rel_rot_por + altura_digitos("Arial-Black", f_por_rot),
      rel_cent_por + altura_digitos("Arial-Black", f_por_cent),
      desloc_de + altura_digitos("Arial-Black", f_de),
      desloc_de + rel_rot_de + altura_digitos("Arial-Black", f_de_rot),
      desloc_de + rel_cent_de + altura_digitos("Arial-Black", f_de_cent),
  )
  base_rel = min(0.0, rel_un_por, desloc_de + rel_un_de)

  centro_area = (limite_superior_preco + limite_inferior_preco) / 2
  y_por = centro_area - ((topo_rel + base_rel) / 2)
  y_de = y_por + desloc_de

  # --- 4. POSIÇÕES HORIZONTAIS (conjunto centralizado na folha) ---
  x_ini = x_base + (page_w - largura_total) / 2
  x_rot_de = x_ini
  x_val_de = x_rot_de + w_rot_de + gap_de
  x_rot_por = x_val_de + w_val_de + esp_blocos
  x_val_por = x_rot_por + w_rot_por + gap_por

  # --- 5. BLOCO "DE" (com risco por cima) ---
  c.setFont("Arial-Black", f_de_rot)
  c.drawString(x_rot_de, y_de + rel_rot_de, "De")
  c.drawString(x_rot_de, y_de + rel_rs_de, "R$")

  x_fim_de = desenhar_inteiro_forcado(
      c, de_int, x_val_de, y_de, "Arial-Black", f_de
  )
  x_cent_de = x_fim_de + folga_cent_de
  c.setFont("Arial-Black", f_de_cent)
  c.drawString(x_cent_de, y_de + rel_cent_de, f",{de_cent}")
  w_cent_de = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)

  c.setFont("Arial-Black", f_de_un)
  c.drawCentredString(x_cent_de + (w_cent_de / 2), y_de + rel_un_de, item.get("un", "1 UN"))

  # risco diagonal por cima do valor antigo
  c.setLineWidth(4.5)
  c.line(
      x_val_de - (2 * mm), y_de,
      x_cent_de + w_cent_de + (2 * mm), y_de + (f_de * 0.75),
  )
  c.setLineWidth(1)

  # --- 6. BLOCO "POR" ---
  c.setFont("Arial-Black", f_por_rot)
  c.drawString(x_rot_por, y_por + rel_rot_por, "Por")
  c.drawString(x_rot_por, y_por + rel_rs_por, "R$")

  x_fim_por = desenhar_inteiro_forcado(
      c, por_int, x_val_por, y_por, "Arial-Black", f_por
  )
  x_cent_por = x_fim_por + folga_cent_por
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_cent_por, y_por + rel_cent_por, f",{por_cent}")
  w_cent_por = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)

  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(x_cent_por + (w_cent_por / 2), y_por + rel_un_por, item.get("un", "1 UN"))
