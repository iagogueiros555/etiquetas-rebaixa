import base64
import importlib
import io
import os
from datetime import date, timedelta
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# --- IMPORTAÇÃO E RELOAD DOS MÓDULOS DE LAYOUT ---
from layouts.a4 import fardo_caixa, promocional, promocional_validade, unitario, unitario_validade

# Importando os módulos A5 com "apelidos" para não dar conflito com os da A4
from layouts.a5 import (
    promo as promo_a5,
    promo_validade as promo_validade_a5,
    unitario as unitario_a5,
    unitario_validade as unitario_validade_a5
)

# Importando os módulos A4 HORIZONTAL com "apelidos"
from layouts.a4h import (
    fardo_caixa as fardo_caixa_a4h,
    promocional as promocional_a4h,
    promo_validade as promo_validade_a4h,
    unitario as unitario_a4h,
    unitario_validade as unitario_validade_a4h,
)

# Importando os módulos A6 (agora separados, igual ao A5) com "apelidos"
from layouts.a6 import (
    promo as promo_a6,
    promo_validade as promo_validade_a6,
    unitario as unitario_a6,
    unitario_validade as unitario_validade_a6
)

# Reloads A4
importlib.reload(promocional)
importlib.reload(promocional_validade)
importlib.reload(unitario)
importlib.reload(unitario_validade)
importlib.reload(fardo_caixa)
# Reloads A5
importlib.reload(promo_a5)
importlib.reload(promo_validade_a5)
importlib.reload(unitario_a5)
importlib.reload(unitario_validade_a5)
# Reloads A4 Horizontal
importlib.reload(fardo_caixa_a4h)
importlib.reload(promocional_a4h)
importlib.reload(promo_validade_a4h)
importlib.reload(unitario_a4h)
importlib.reload(unitario_validade_a4h)
# Reloads A6
importlib.reload(promo_a6)
importlib.reload(promo_validade_a6)
importlib.reload(unitario_a6)
importlib.reload(unitario_validade_a6)


# --- REGISTRO DA FONTE CUSTOMIZADA ---
pdfmetrics.registerFont(TTFont("Arial-Black", "arialblack.ttf"))

# Ícone da aba: usa o arquivo se ele existir, senão cai no emoji.
# Assim o app não quebra se a pasta de ícones não estiver no lugar.
CAMINHO_ICONE = "docs/icons/favicon-32.png"
icone_aba = CAMINHO_ICONE if os.path.exists(CAMINHO_ICONE) else "🏷️"

st.set_page_config(
    page_title="Cartazeiro - Novo Atacarejo",
    page_icon=icone_aba,
    layout="wide",
)

# --- MAPEAMENTO DE LAYOUTS E DIMENSÕES ---
LAYOUTS = {
    "A6 Vertical (6 por A4)": {
        "size": A4,
        "cols": 2,
        "rows": 3,
        "scale": 1.0,
        "tipo_pasta": "a6",
    },
    "A5 Vertical (2 por A4)": {
        "size": A4,
        "cols": 1,
        "rows": 2,
        "scale": 1.0,
        "tipo_pasta": "a5",
    },
    "A4 / A3 Vertical (1 por folha)": {
        "size": A4,
        "cols": 1,
        "rows": 1,
        "scale": 1.5,
        "tipo_pasta": "a4",
    },
    "A4 / A3 Horizontal (1 por folha)": {
        "size": landscape(A4),
        "cols": 1,
        "rows": 1,
        "scale": 1.5,
        "tipo_pasta": "a4h",
    },
}


# Nome curto de cada formato, para caber na coluna da lista
APELIDO_FORMATO = {
    "A6 Vertical (6 por A4)": "A6",
    "A5 Vertical (2 por A4)": "A5",
    "A4 / A3 Vertical (1 por folha)": "A4 ↕",
    "A4 / A3 Horizontal (1 por folha)": "A4 ↔",
}


def selecionar_funcao_desenho(modelo_chave, item):
    cfg = LAYOUTS[modelo_chave]
    pasta = cfg["tipo_pasta"]

    tem_de = bool(item.get("de"))
    tem_rebaixa = item.get("e_rebaixa")

    if pasta == "a4h":
        # O fardo é tratado aqui dentro: se caísse no bloco geral abaixo,
        # chamaria o layout VERTICAL numa folha deitada.
        if item.get("e_fardo"):
            return fardo_caixa_a4h.desenhar_etiqueta_a4h
        if tem_de and tem_rebaixa:
            return promo_validade_a4h.desenhar_etiqueta_a4h
        elif tem_de and not tem_rebaixa:
            return promocional_a4h.desenhar_etiqueta_a4h
        elif not tem_de and tem_rebaixa:
            return unitario_validade_a4h.desenhar_etiqueta_a4h
        else:
            return unitario_a4h.desenhar_etiqueta_a4h

    if item.get("e_fardo"):
        return fardo_caixa.desenhar_etiqueta_a4

    if pasta == "a4":
        if tem_de and tem_rebaixa:
            return promocional_validade.desenhar_etiqueta_a4
        elif tem_de and not tem_rebaixa:
            return promocional.desenhar_etiqueta_a4
        elif not tem_de and tem_rebaixa:
            return unitario_validade.desenhar_etiqueta_a4
        else:
            return unitario.desenhar_etiqueta_a4

    elif pasta == "a5":
        # Nova lógica de roteamento para a pasta A5
        if tem_de and tem_rebaixa:
            return promo_validade_a5.desenhar_etiqueta_a5
        elif tem_de and not tem_rebaixa:
            return promo_a5.desenhar_etiqueta_a5
        elif not tem_de and tem_rebaixa:
            return unitario_validade_a5.desenhar_etiqueta_a5
        else:
            return unitario_a5.desenhar_etiqueta_a5

    else:
        # Roteamento para a pasta A6 (mesma lógica do A4 e A5)
        if tem_de and tem_rebaixa:
            return promo_validade_a6.desenhar_etiqueta_a6
        elif tem_de and not tem_rebaixa:
            return promo_a6.desenhar_etiqueta_a6
        elif not tem_de and tem_rebaixa:
            return unitario_validade_a6.desenhar_etiqueta_a6
        else:
            return unitario_a6.desenhar_etiqueta_a6


def gerar_pdf_etiquetas(itens, modelo_padrao):
    """Gera o PDF respeitando o formato gravado em CADA etiqueta.

    As etiquetas são agrupadas por formato (mantendo a ordem em que os
    formatos apareceram na lista) e cada grupo vira páginas do seu próprio
    tamanho. Um mesmo PDF pode ter páginas A6, A5 e A4 misturadas.
    """
    grupos = {}
    for item in itens:
        chave = item.get("formato", modelo_padrao)
        if chave not in LAYOUTS:          # formato antigo ou removido
            chave = modelo_padrao
        grupos.setdefault(chave, []).append(item)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LAYOUTS[modelo_padrao]["size"])
    pagina_aberta = False

    for modelo_chave, lista in grupos.items():
        cfg = LAYOUTS[modelo_chave]
        page_w, page_h = cfg["size"]
        cols, rows, scale = cfg["cols"], cfg["rows"], cfg["scale"]
        cap_pagina = cols * rows
        col_w, row_h = page_w / cols, page_h / rows

        posicao = 0
        for item in lista:
            qtd = max(1, int(item.get("quantidade", 1)))
            draw_func = selecionar_funcao_desenho(modelo_chave, item)

            for _ in range(qtd):
                if posicao % cap_pagina == 0:
                    if pagina_aberta:
                        c.showPage()
                    c.setPageSize(cfg["size"])   # cada grupo tem seu tamanho
                    pagina_aberta = True

                pos_na_pagina = posicao % cap_pagina
                col = pos_na_pagina % cols
                row = pos_na_pagina // cols

                x_base = col * col_w
                y_base = page_h - ((row + 1) * row_h)

                draw_func(c, item, x_base, y_base, col_w, row_h, scale)
                posicao += 1

    c.save()
    buffer.seek(0)
    return buffer


# --- INTERFACE DE USUÁRIO (STREAMLIT) ---

if "lista_itens" not in st.session_state:
    st.session_state.lista_itens = []

col_titulo, col_formato = st.columns([3, 2])
with col_titulo:
    st.markdown("## 🏷️ Cartazeiro")
with col_formato:
    modelo_selecionado = st.selectbox(
        "Formato da Folha:", list(LAYOUTS.keys())
    )

# Altura fixa da caixa de etiquetas geradas — ajustada pra bater com a
# altura natural do formulário "Dados do Produto" ao lado.
ALTURA_CAIXA_LISTA = 320

col_lista, col_menu = st.columns([3, 2], gap="medium")

# ===================== COLUNA ESQUERDA: ETIQUETAS GERADAS =====================
with col_lista:
    st.markdown("**📋 Etiquetas Geradas**")

    with st.container(height=ALTURA_CAIXA_LISTA, border=True):
        if st.session_state.lista_itens:
            h_num, h_desc, h_preco, h_extra, h_fmt, h_qtd, h_del = st.columns(
                [0.4, 2.5, 1.9, 1.2, 0.8, 0.9, 0.6]
            )
            h_num.markdown("**#**")
            h_desc.markdown("**Descrição**")
            h_preco.markdown("**Preço**")
            h_extra.markdown("**Validade**")
            h_fmt.markdown("**Folha**")
            h_qtd.markdown("**Qtd.**")

            for idx, item in enumerate(st.session_state.lista_itens):
                col_num, col_desc, col_preco, col_extra, col_fmt, col_qtd, col_del = st.columns(
                    [0.4, 2.5, 1.9, 1.2, 0.8, 0.9, 0.6]
                )

                col_num.write(idx + 1)
                col_desc.write(item.get("desc", ""))

                if item.get("e_fardo"):
                    col_preco.write(f"R$ {item.get('por', '')} (fardo)")
                    col_extra.write(
                        f"{item.get('qtd_fardo', '')}x R$ {item.get('preco_unit', '')}"
                    )
                elif item.get("de"):
                    # o preço antigo aparece riscado e em itálico, igual na etiqueta
                    col_preco.write(
                        f"~~*{item.get('de', '')}*~~ → **{item.get('por', '')}**"
                    )
                    col_extra.write(item.get("val", ""))
                else:
                    col_preco.write(f"R$ {item.get('por', '')}")
                    col_extra.write(item.get("val", ""))

                # Formato gravado quando a etiqueta foi criada
                fmt = item.get("formato", modelo_selecionado)
                col_fmt.write(APELIDO_FORMATO.get(fmt, fmt))

                # Caixa de quantidade: quantas vezes essa etiqueta vai repetir no PDF
                nova_qtd = col_qtd.number_input(
                    "Qtd.", min_value=1, value=int(item.get("quantidade", 1)), step=1,
                    key=f"qtd_item_{idx}", label_visibility="collapsed"
                )
                item["quantidade"] = int(nova_qtd)

                if col_del.button("🗑️", key=f"del_item_{idx}", help="Remover apenas esta etiqueta"):
                    st.session_state.lista_itens.pop(idx)
                    st.rerun()
        else:
            st.caption("Nenhuma etiqueta adicionada ainda. Preencha o formulário ao lado ➡️")

    # Total e botões de ação ficam FORA da caixa com scroll, sempre visíveis
    if st.session_state.lista_itens:
        total_etiquetas = sum(int(i.get("quantidade", 1)) for i in st.session_state.lista_itens)
        st.caption(f"🏷️ Total de etiquetas a imprimir: **{total_etiquetas}**")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🗑️ Limpar Lista"):
                st.session_state.lista_itens = []
                st.rerun()

        with b2:
            pdf_buffer = gerar_pdf_etiquetas(
                st.session_state.lista_itens, modelo_selecionado
            )
            base64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")

            botao_html = f"""
                <style>
                  html, body {{ margin: 0; padding: 0; overflow: hidden; }}
                </style>
                <button onclick="openPDF()" style=
                    "background-color: #FF4B4B; color: white; padding: 10px 16px; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; width: 100%; font-family: sans-serif;"
                >
                    🖨️ IMPRIMIR ETIQUETAS
                </button>
                <script>
                function openPDF() {{
                    const base64Data = "{base64_pdf}";
                    const byteCharacters = atob(base64Data);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {{ type: 'application/pdf' }});
                    const blobUrl = URL.createObjectURL(blob);
                    window.open(blobUrl, '_blank');
                }}
                </script>
                """

            # st.components.v1.html foi descontinuado (a data de remoção já
            # passou). st.iframe é a substituição e existe a partir da 1.56.
            # O fallback mantém o botão funcionando em versões mais antigas.
            # 58 e não 50: o st.iframe conta as margens de forma diferente do
            # components.html antigo, e com 50 sobrava uma barra de rolagem.
            if hasattr(st, "iframe"):
                st.iframe(botao_html, height=58)
            else:
                components.html(botao_html, height=58)

# ===================== COLUNA DIREITA: MENU DE CRIAÇÃO =====================
with col_menu:
    st.markdown("**📝 Dados do Produto**")

    e_fardo_caixa = False
    if modelo_selecionado in ("A4 / A3 Vertical (1 por folha)",
                              "A4 / A3 Horizontal (1 por folha)"):
        e_fardo_caixa = st.checkbox("📦 Preço de Caixa / Fardo (Atacado)")

    if e_fardo_caixa:
        # Checkbox fora do form para atualizar instantaneamente
        modo_manual = st.checkbox(
            "✏️ Digitar preço total da caixa manualmente (Desativar cálculo automático)", value=False
        )

        with st.form("form_fardo", clear_on_submit=True):
            desc = st.text_input("Descrição do Produto:", placeholder="Ex: SHAMPOO SEDA 325ML").upper()

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                qtd_fardo = st.number_input("Qtd. na Caixa/Fardo:", min_value=1, value=12, step=1)
            with col_f2:
                unidade = st.text_input("Unidade (Ex: UN, PCT):", value="UN").upper()

            # O preço unitário base aparece SEMPRE
            preco_unitario_base = st.number_input(
                "Preço Unitário Base (R$):", min_value=0.01, value=5.00, format="%.2f"
            )

            if modo_manual:
                # Se marcado, exibe a caixa para digitar o total da caixa manualmente
                preco_manual_input = st.text_input("Preço Total da Caixa (R$):", placeholder="Ex: 47,00")
                valor_caixa_str = ""
            else:
                # Se desmarcado, calcula automaticamente
                preco_calculado = preco_unitario_base * qtd_fardo
                valor_caixa_str = f"{preco_calculado:.2f}".replace(".", ",")
                preco_manual_input = ""

            btn_adicionar_fardo = st.form_submit_button("➕ Adicionar Caixa à Lista")

            if btn_adicionar_fardo:
                if desc:
                    if modo_manual:
                        if preco_manual_input:
                            valor_caixa_str = preco_manual_input.replace(".", ",").strip()
                        else:
                            st.warning("Informe o preço manual da caixa!")
                            st.stop()

                    valor_unit_str = f"{preco_unitario_base:.2f}".replace(".", ",")

                    item_dados = {
                        "desc": desc,
                        "de": "",
                        "por": valor_caixa_str,          # Preço principal da caixa
                        "preco_unit": valor_unit_str,    # Preço unitário base
                        "un": unidade,
                        "val": "",
                        "e_rebaixa": False,
                        "e_fardo": True,
                        "qtd_fardo": qtd_fardo,
                        "quantidade": 1,
                        "formato": modelo_selecionado,
                    }
                    st.session_state.lista_itens.append(item_dados)
                    st.success("Etiqueta de caixa adicionada! Ajuste a quantidade na lista ao lado.")
                    st.rerun()
                else:
                    st.warning("Preencha a Descrição do Produto!")
    else:
        # --- MODOS NORMAIS (PROMOCIONAL OU UNITÁRIO) ---
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tem_desconto = st.checkbox("Promocional com Desconto (De / Por)", value=True)
        with col_t2:
            e_rebaixa = st.checkbox("Etiqueta de Rebaixa (Próximo à Validade)", value=True)


        with st.form("form_produto", clear_on_submit=True):
            desc = st.text_input(
                "Descrição do Produto:", placeholder="Ex: BISC MAIZENA CAPRICCHE 312G LEITE"
            ).upper()

            if tem_desconto:
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    de = st.text_input("Preço DE (R$):", placeholder="Ex: 5,58")
                with col_p2:
                    por = st.text_input("Preço POR (R$):", placeholder="Ex: 1,97")
                with col_p3:
                    unidade = st.text_input("Unidade:", value="1 UN").upper()
            else:
                col_p1, col_p2 = st.columns([2, 1])
                with col_p1:
                    por = st.text_input("Preço Único (R$):", placeholder="Ex: 1,97")
                    de = ""
                with col_p2:
                    unidade = st.text_input("Unidade:", value="1 UN").upper()

            if e_rebaixa:
                data_validade = st.date_input(
                    "Data de Validade:",
                    value=None,
                    format="DD/MM/YYYY",
                    min_value=date.today(),
                    max_value=date.today() + timedelta(days=365 * 3),
                )
                validade = data_validade.strftime("%d/%m/%Y") if data_validade else ""
            else:
                validade = ""

            btn_adicionar = st.form_submit_button("➕ Adicionar à Lista")

            if btn_adicionar:
                if desc and por:
                    item_dados = {
                        "desc": desc,
                        "de": de.replace(".", ",").strip(),
                        "por": por.replace(".", ",").strip(),
                        "un": unidade,
                        "val": validade,
                        "e_rebaixa": e_rebaixa,
                        "e_fardo": False,
                        "quantidade": 1,
                        "formato": modelo_selecionado,
                    }
                    st.session_state.lista_itens.append(item_dados)

                    st.success(f"Etiqueta do produto '{desc}' adicionada! Ajuste a quantidade na lista ao lado.")
                    st.rerun()
                else:
                    st.warning("Preencha ao menos a Descrição e o Preço POR!")
