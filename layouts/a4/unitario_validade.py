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
    largura_total_preco = w_real + w_cent

    if largura_total_preco > largura_util:
      fator_red = largura_util / largura_total_preco
      f_real, f_cent, f_rs, f_un = (
          int(f_real * fator_red),
          int(f_cent * fator_red),
          int(f_rs * fator_red),
          int(f_un * fator_red),
      )
      w_real = c.stringWidth(inteiro_str, "Arial-Black", f_real)
      w_cent = c.stringWidth(f",{centavos_str}", "Arial-Black", f_cent)
      largura_total_preco = largura_util

    x_inicio_real = (page_w - largura_total_preco) / 2
    y_linha_base_preco = y_atual - f_real + 50

    # A) R$: Colado logo acima do número inteiro (baixado de +f_real-10 para +f_real-45)
    c.setFont("Arial-Black", f_rs)
    c.drawString(x_inicio_real, y_linha_base_preco + f_real - 45, "R$")

    # B) VALOR REAL (Inteiro)
    c.setFont("Arial-Black", f_real)
    c.drawString(x_inicio_real, y_linha_base_preco, inteiro_str)

    # C) CENTAVOS (,XX): Alinhados no topo do número principal (baixados para coincidir o topo)
    x_centavos = x_inicio_real + w_real
    y_centavos = y_linha_base_preco + (f_real - f_cent) - 35
    c.setFont("Arial-Black", f_cent)
    c.drawString(x_centavos, y_centavos, f",{centavos_str}")

    # D) UNIDADE: Subiu para encaixar certinho logo abaixo dos centavos
    x_unidade = x_centavos + (w_cent / 2)
    y_unidade = y_centavos - 25
    c.setFont("Arial-Black", f_un)
    un_str = item.get("un", "1 UN")
    c.drawCentredString(x_unidade, y_unidade, un_str)

    # Recuo proporcional para o aviso de vencimento não encostar na unidade
    y_atual = y_linha_base_preco - 20
