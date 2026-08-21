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

# --- Rodapé de validade (igual ao do unitário com validade) ---
COR_TARJA = HexColor("#DCDCDC")
TARJA_ALTURA = 22.1 * mm     # altura da tarja cinza
TARJA_DIST_BASE = 6 * mm     # distância da tarja até o pé da folha
GAP_AVISO_TARJA = 1.5 * mm   # entre a frase de aviso e a tarja
FONTE_VALIDADE = 56          # tamanho inicial do "VALIDADE: ..." (reduz p/ caber)
FONTE_AVISO = 34             # tamanho inicial da frase (reduz até caber em 1 linha)
PADDING_TARJA = 3 * mm       # respiro do texto dentro da tarja
FOLGA_PRECO = 7 * mm         # respiro mínimo do preço até a descrição e o aviso

TEXTO_AVISO = "PRODUTO PRÓXIMO A DATA DE VENCIMENTO"

# --- Bloco De / Por ---
FONTE_POR_INICIAL = 280      # ponto de partida do "Por" (reduz até caber)
ESPACO_ENTRE_BLOCOS = 20 * mm
GAP_ROTULO_POR = 8 * mm
GAP_ROTULO_DE = 1.5 * mm
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
  """Separa reais e centavos aceitando 7,58 / 1.548,00 / 1548 / 1548.00."""
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


def tabela_do_de(de_int):
  """Tamanho do bloco "De" por quantidade de dígitos.

  É a MESMA tabela do promocional sem validade, e de propósito NÃO depende
  do tamanho do "Por": aqui o "Por" encolhe para caber junto com o rodapé,
  e se o "De" acompanhasse essa redução ele sairia bem menor que o do outro
  cartaz - foi exatamente o que apareceu na impressão.
  """
  n = len(de_int)
  if n <= 2:
    return 103, 52, 25, 25
  if n == 3:
    return 88, 44, 21, 21
  return 75, 37, 18, 18


def fontes_do_grupo(f_por, fontes_de):
  """O 'Por' e seus derivados; o 'De' vem pronto da tabela."""
  f_por_cent = max(8, round(f_por * 0.50))
  f_por_rot = max(8, round(f_por * 0.168))
  f_por_un = max(8, round(f_por * 0.121))

  f_de, f_de_cent, f_de_rot, f_de_un = fontes_de
  # trava: o valor riscado nunca pode ficar maior que o preço principal
  teto = max(8, round(f_por * 0.60))
  if f_de > teto:
    fator = teto / f_de
    f_de = teto
    f_de_cent = max(8, round(f_de_cent * fator))
    f_de_rot = max(8, round(f_de_rot * fator))
    f_de_un = max(8, round(f_de_un * fator))

  return (f_por, f_por_cent, f_por_rot, f_por_un,
          f_de, f_de_cent, f_de_rot, f_de_un)


def geometria_grupo(f):
  """Posições relativas à linha de base do 'Por' e extremos do conjunto."""
  (f_por, f_por_cent, f_por_rot, f_por_un,
   f_de, f_de_cent, f_de_rot, f_de_un) = f

  rel_rot_por = f_por * 0.52
  rel_rs_por = f_por * 0.325
  rel_cent_por = f_por - f_por_cent - (f_por * 0.12)
  rel_un_por = rel_cent_por - f_por_un - (8 * mm)

  desloc_de = f_por * 0.29
  rel_rot_de = f_de * 0.44
  rel_rs_de = f_de * 0.14
  rel_cent_de = f_de - f_de_cent - (f_de * 0.12)
  rel_un_de = -(altura_digitos("Arial-Black", f_de_un) + 1 * mm)

  topo = max(
      altura_digitos("Arial-Black", f_por),
      rel_rot_por + altura_digitos("Arial-Black", f_por_rot),
      rel_cent_por + altura_digitos("Arial-Black", f_por_cent),
      desloc_de + altura_digitos("Arial-Black", f_de),
      desloc_de + rel_rot_de + altura_digitos("Arial-Black", f_de_rot),
      desloc_de + rel_cent_de + altura_digitos("Arial-Black", f_de_cent),
  )
  base = min(0.0, rel_un_por, desloc_de + rel_un_de)

  return {
      "rel_rot_por": rel_rot_por, "rel_rs_por": rel_rs_por,
      "rel_cent_por": rel_cent_por, "rel_un_por": rel_un_por,
      "desloc_de": desloc_de, "rel_rot_de": rel_rot_de,
      "rel_rs_de": rel_rs_de, "rel_cent_de": rel_cent_de,
      "rel_un_de": rel_un_de, "topo": topo, "base": base,
  }


def larguras_grupo(c, f, de_int, de_cent, por_int, por_cent, escala):
  """Largura de cada parte e do conjunto inteiro."""
  (f_por, f_por_cent, f_por_rot, _,
   f_de, f_de_cent, f_de_rot, _) = f

  gap_de = GAP_ROTULO_DE * escala
  gap_por = GAP_ROTULO_POR * escala
  espaco = ESPACO_ENTRE_BLOCOS * escala

  w_rot_de = max(c.stringWidth("De", "Arial-Black", f_de_rot),
                 c.stringWidth("R$", "Arial-Black", f_de_rot))
  w_val_de = (calcular_largura_inteiro_forcado(c, de_int, "Arial-Black", f_de)
              + c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent))
  w_rot_por = max(c.stringWidth("Por", "Arial-Black", f_por_rot),
                  c.stringWidth("R$", "Arial-Black", f_por_rot))
  w_val_por = (calcular_largura_inteiro_forcado(c, por_int, "Arial-Black", f_por)
               + c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent))

  bloco_de = w_rot_de + gap_de + w_val_de
  bloco_por = w_rot_por + gap_por + w_val_por
  return {
      "w_rot_de": w_rot_de, "w_val_de": w_val_de,
      "w_rot_por": w_rot_por, "w_val_por": w_val_por,
      "gap_de": gap_de, "gap_por": gap_por, "espaco": espaco,
      "bloco_de": bloco_de, "bloco_por": bloco_por,
      "total": bloco_de + espaco + bloco_por,
  }


def ajustar_grupo(c, de_int, de_cent, por_int, por_cent, max_w, max_h, minimo=60):
  """Reduz o 'Por' de 1 em 1 ponto até o conjunto caber na largura E na altura."""
  fontes_de = tabela_do_de(de_int)
  f_por = FONTE_POR_INICIAL
  while f_por > minimo:
    f = fontes_do_grupo(f_por, fontes_de)
    escala = f_por / FONTE_POR_INICIAL
    larg = larguras_grupo(c, f, de_int, de_cent, por_int, por_cent, escala)
    geo = geometria_grupo(f)
    if larg["total"] <= max_w and (geo["topo"] - geo["base"]) <= max_h:
      return f, larg, geo
    f_por -= 1

  # Só chega aqui em casos extremos (dois valores enormes). Aí o conjunto
  # inteiro, "De" incluído, encolhe proporcionalmente para não furar a margem.
  if larg["total"] > max_w:
    fator = max_w / larg["total"]
    fontes_de = tuple(max(8, round(v * fator)) for v in fontes_de)
    f = fontes_do_grupo(max(8, round(f_por * fator)), fontes_de)
    escala = (f[0] / FONTE_POR_INICIAL)
    larg = larguras_grupo(c, f, de_int, de_cent, por_int, por_cent, escala)
    geo = geometria_grupo(f)
  return f, larg, geo


def ajustar_aviso_uma_linha(c, texto, f_inicial, max_w, minimo=16):
  """Reduz a frase de aviso até ela caber em UMA linha."""
  f = f_inicial
  while f > minimo and c.stringWidth(texto, "Arial-Black", f) > max_w:
    f -= 1
  return f


def ajustar_validade(c, texto, f_inicial, max_w, max_h, minimo=20):
  """Reduz o texto da validade até caber na largura e na altura da tarja."""
  f = f_inicial
  while f > minimo:
    if (c.stringWidth(texto, "Arial-Black", f) <= max_w
        and altura_digitos("Arial-Black", f) <= max_h):
      break
    f -= 1
  return f


def desenhar_etiqueta_a4h(c, item, x_base, y_base, col_w, row_h, scale):
  """Etiqueta A4 HORIZONTAL - Promocional (De / Por), com validade."""
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
  y_texto_validade = (y_tarja + (TARJA_ALTURA / 2)
                      - (altura_digitos("Arial-Black", f_validade) / 2))
  c.setFont("Arial-Black", f_validade)
  c.drawCentredString(x_centro, y_texto_validade, texto_validade)

  f_aviso = ajustar_aviso_uma_linha(c, TEXTO_AVISO, FONTE_AVISO, largura_util)
  y_aviso = y_tarja + TARJA_ALTURA + GAP_AVISO_TARJA
  c.setFont("Arial-Black", f_aviso)
  c.drawCentredString(x_centro, y_aviso, TEXTO_AVISO)

  limite_inferior = y_aviso + altura_digitos("Arial-Black", f_aviso)

  # --- 3. BLOCO DE / POR (encolhe até caber entre a descrição e o rodapé) ---
  de_int, de_cent = separar_valor(item.get("de"))
  por_int, por_cent = separar_valor(item.get("por"))

  altura_livre = (limite_superior - limite_inferior) - (2 * FOLGA_PRECO)
  f, larg, geo = ajustar_grupo(
      c, de_int, de_cent, por_int, por_cent, largura_util, altura_livre
  )
  (f_por, f_por_cent, f_por_rot, f_por_un,
   f_de, f_de_cent, f_de_rot, f_de_un) = f

  centro_area = (limite_superior + limite_inferior) / 2
  y_por = centro_area - ((geo["topo"] + geo["base"]) / 2)
  y_de = y_por + geo["desloc_de"]

  # --- 4. POSIÇÕES HORIZONTAIS (conjunto centralizado na folha) ---
  x_ini = x_base + (page_w - larg["total"]) / 2
  x_rot_de = x_ini
  x_val_de = x_rot_de + larg["w_rot_de"] + larg["gap_de"]
  x_rot_por = x_val_de + larg["w_val_de"] + larg["espaco"]
  x_val_por = x_rot_por + larg["w_rot_por"] + larg["gap_por"]

  # --- 5. BLOCO "DE" (com risco por cima) ---
  c.setFont("Arial-Black", f_de_rot)
  c.drawString(x_rot_de, y_de + geo["rel_rot_de"], "De")
  c.drawString(x_rot_de, y_de + geo["rel_rs_de"], "R$")

  x_fim_de = desenhar_inteiro_forcado(
      c, de_int, x_val_de, y_de, "Arial-Black", f_de
  )
  c.setFont("Arial-Black", f_de_cent)
  c.drawString(x_fim_de, y_de + geo["rel_cent_de"], f",{de_cent}")
  w_cent_de = c.stringWidth(f",{de_cent}", "Arial-Black", f_de_cent)

  c.setFont("Arial-Black", f_de_un)
  c.drawCentredString(x_fim_de + (w_cent_de / 2), y_de + geo["rel_un_de"],
                      item.get("un", "1 UN"))

  c.setLineWidth(4.5)
  c.line(
      x_val_de - (2 * mm), y_de,
      x_fim_de + w_cent_de + (2 * mm), y_de + (f_de * 0.75),
  )
  c.setLineWidth(1)

  # --- 6. BLOCO "POR" ---
  c.setFont("Arial-Black", f_por_rot)
  c.drawString(x_rot_por, y_por + geo["rel_rot_por"], "Por")
  c.drawString(x_rot_por, y_por + geo["rel_rs_por"], "R$")

  x_fim_por = desenhar_inteiro_forcado(
      c, por_int, x_val_por, y_por, "Arial-Black", f_por
  )
  c.setFont("Arial-Black", f_por_cent)
  c.drawString(x_fim_por, y_por + geo["rel_cent_por"], f",{por_cent}")
  w_cent_por = c.stringWidth(f",{por_cent}", "Arial-Black", f_por_cent)

  c.setFont("Arial-Black", f_por_un)
  c.drawCentredString(x_fim_por + (w_cent_por / 2), y_por + geo["rel_un_por"],
                      item.get("un", "1 UN"))
