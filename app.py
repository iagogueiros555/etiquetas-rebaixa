import base64
import importlib
import io
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# --- IMPORTAÇÃO E RELOAD DOS MÓDULOS DE LAYOUT ---
from layouts import a5, a6
from layouts.a4 import fardo_caixa, promocional, promocional_validade, unitario, unitario_validade

importlib.reload(a6)
importlib.reload(a5)
importlib.reload(promocional)
importlib.reload(promocional_validade)
importlib.reload(unitario)
importlib.reload(unitario_validade)
importlib.reload(fardo_caixa)

# --- REGISTRO DA FONTE CUSTOMIZADA ---
pdfmetrics.registerFont(TTFont("Arial-Black", "arialblack.ttf"))

st.set_page_config(
    page_title="Gerador de Etiquetas - Novo Atacarejo", layout="centered"
)

st.title("🏷️ Gerador de Etiquetas")
st.caption("Ajuste Fino - Modelos A6, A5 e A4/A3")

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
}


def selecionar_funcao_desenho(modelo_chave, item):
    cfg = LAYOUTS[modelo_chave]
    pasta = cfg["tipo_pasta"]

    if item.get("e_fardo"):
        return fardo_caixa.desenhar_etiqueta_a4

    tem_de = bool(item.get("de"))
    tem_rebaixa = item.get("e_rebaixa")

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
        return a5.desenhar_etiqueta_a5
    else:
        return a6.desenhar_etiqueta_a6


def gerar_pdf_etiquetas(itens, modelo_chave):
    cfg = LAYOUTS[modelo_chave]
    page_w, page_h = cfg["size"]
    cols, rows = cfg["cols"], cfg["rows"]
    scale = cfg["scale"]

    cap_pagina = cols * rows
    col_w = page_w / cols
    row_h = page_h / rows

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=cfg["size"])

    for idx, item in enumerate(itens):
        if idx > 0 and idx % cap_pagina == 0:
            c.showPage()

        pos_na_pagina = idx % cap_pagina
        col = pos_na_pagina % cols
        row = pos_na_pagina // cols

        x_base = col * col_w
        y_base = page_h - ((row + 1) * row_h)

        draw_func = selecionar_funcao_desenho(modelo_chave, item)
        draw_func(c, item, x_base, y_base, col_w, row_h, scale)

    c.save()
    buffer.seek(0)
    return buffer


# --- INTERFACE DE USUÁRIO (STREAMLIT) ---

if "lista_itens" not in st.session_state:
    st.session_state.lista_itens = []

modelo_selecionado = st.selectbox(
    "Selecione o Formato da Folha:", list(LAYOUTS.keys())
)

st.divider()
st.markdown("### 📝 Dados do Produto")

# Verificação restrita: a opção de Caixa/Fardo SÓ aparece se o formato A4/A3 estiver selecionado
e_fardo_caixa = False
if modelo_selecionado == "A4 / A3 Vertical (1 por folha)":
    e_fardo_caixa = st.checkbox("📦 Preço de Caixa / Fardo (Atacado)")

if e_fardo_caixa:
    # --- MODO CAIXA / FARDO ---
    with st.form("form_fardo", clear_on_submit=True):
        desc = st.text_input("Descrição do Produto:", placeholder="Ex: SHAMPOO SEDA 325ML").upper()
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            qtd_fardo = st.number_input("Qtd. na Caixa/Fardo:", min_value=1, value=12, step=1)
        with col_f2:
            unidade = st.text_input("Unidade (Ex: UN, PCT):", value="UN").upper()

        # Checkbox para alternar entre manual e automático
        modo_manual = st.checkbox("✏️ Digitar preço total da caixa manualmente", value=False, on_change=st.rerun)

        if modo_manual:
            preco_manual_input = st.text_input("Preço Total da Caixa (R$):", placeholder="Ex: 47,00")
            preco_calculado = 0.0
        else:
            preco_unitario_base = st.number_input("Preço Unitário Base (R$):", min_value=0.01, value=5.00, format="%.2f")
            preco_calculado = preco_unitario_base * qtd_fardo
            preco_manual_input = ""

        qtd_copias = st.number_input("Qtd. de Etiquetas de Fardo:", min_value=1, value=1, step=1)
        btn_adicionar_fardo = st.form_submit_button("➕ Adicionar Caixa à Lista")

        if btn_adicionar_fardo:
            if desc:
                if modo_manual:
                    if preco_manual_input:
                        valor_final_str = preco_manual_input.replace(".", ",").strip()
                    else:
                        st.warning("Informe o preço manual da caixa!")
                        st.stop()
                else:
                    valor_final_str = f"{preco_calculado:.2f}".replace(".", ",")

                item_dados = {
                    "desc": desc,
                    "de": "",
                    "por": valor_final_str,
                    "un": unidade,
                    "val": "",
                    "e_rebaixa": False,
                    "e_fardo": True,
                    "qtd_fardo": qtd_fardo,
                }
                for _ in range(int(qtd_copias)):
                    st.session_state.lista_itens.append(item_dados)
                st.success(f"{qtd_copias} etiqueta(s) de caixa adicionada(s)!")
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

        col_bottom1, col_bottom2 = st.columns([2, 1])
        with col_bottom1:
            if e_rebaixa:
                validade = st.text_input("Data de Validade:", placeholder="Ex: 01/08/2026")
            else:
                validade = ""
        with col_bottom2:
            qtd_copias = st.number_input("Qtd. de Cópias:", min_value=1, value=1, step=1)

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
                }
                for _ in range(int(qtd_copias)):
                    st.session_state.lista_itens.append(item_dados)

                st.success(f"{qtd_copias} etiqueta(s) do produto '{desc}' adicionada(s)!")
                st.rerun()
            else:
                st.warning("Preencha ao menos a Descrição e o Preço POR!")

# --- TABELA E AÇÃO DE IMPRESSÃO ---
if st.session_state.lista_itens:
    st.divider()
    st.markdown("### 📋 Lista para Impressão")
    st.table(st.session_state.lista_itens)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Limpar Lista"):
            st.session_state.lista_itens = []
            st.rerun()

    with c2:
        pdf_buffer = gerar_pdf_etiquetas(
            st.session_state.lista_itens, modelo_selecionado
        )
        base64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")

        components.html(
            f"""
            <button onclick="openPDF()" style=
                "background-color: #FF4B4B; color: white; padding: 10px 16px; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; width: 100%; font-family: sans-serif;"
            >
                🖨️ ABRIR PDF EM NOVA ABA
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
            """,
            height=50,
        )
