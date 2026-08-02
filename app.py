import base64
import importlib
import io
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A3, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# --- IMPORTS DOS LAYOUTS COM RELOAD (Evita cache antigo do Streamlit) ---
import layouts.a5 as a5
import layouts.a6 as a6

importlib.reload(a6)
importlib.reload(a5)

from layouts.a5 import desenhar_etiqueta_a5
from layouts.a6 import desenhar_etiqueta_a6

# --- REGISTRO DA FONTE CUSTOMIZADA ---
pdfmetrics.registerFont(TTFont("Arial-Black", "arialblack.ttf"))

st.set_page_config(
    page_title="Gerador de Etiquetas - Novo Atacarejo", layout="centered"
)

st.title("🏷️ Gerador de Etiquetas")
st.caption("Ajuste Fino - Modelos A6 e A5 Vertical")

# --- MAPEAMENTO DE LAYOUTS ---
LAYOUTS = {
    "A6 Vertical (6 por A4)": {
        "size": A4,
        "cols": 2,
        "rows": 3,
        "scale": 1.0,
        "draw_func": desenhar_etiqueta_a6,
    },
    "A5 Vertical (2 por A4)": {
        "size": A4,
        "cols": 1,
        "rows": 2,
        "scale": 1.0,
        "draw_func": desenhar_etiqueta_a5,
    },
}


def gerar_pdf_etiquetas(itens, modelo_chave):
    cfg = LAYOUTS[modelo_chave]
    page_w, page_h = cfg["size"]
    cols, rows = cfg["cols"], cfg["rows"]
    scale = cfg["scale"]
    draw_func = cfg["draw_func"]

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

        # Chama a função de desenho específica do modelo selecionado (A6 ou A5)
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

col_t1, col_t2 = st.columns(2)
with col_t1:
    tem_desconto = st.checkbox("Promocional com Desconto (De / Por)", value=True)
with col_t2:
    e_rebaixa = st.checkbox(
        "Etiqueta de Rebaixa (Próximo à Validade)", value=True
    )

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

    # Linha para Validade (se for rebaixa) e Quantidade de Cópias
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
            }

            # Adiciona o produto na lista a quantidade de vezes solicitada
            for _ in range(int(qtd_copias)):
                st.session_state.lista_itens.append(item_dados)

            st.success(f"{qtd_copias} etiqueta(s) do produto '{desc}' adicionada(s)!")
            st.rerun()
        else:
            st.warning("Preencha ao menos a Descrição e o Preço POR!")

# Tabela e Ação de Impressão
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
            <button onclick="openPDF()" style="
                background-color: #FF4B4B;
                color: white;
                padding: 10px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                cursor: pointer;
                width: 100%;
                font-family: sans-serif;
            ">
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
