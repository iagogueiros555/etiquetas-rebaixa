import io
import base64
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A3, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Gerador de Etiquetas - Novo Atacarejo", layout="centered")

st.title("🏷️ Gerador de Etiquetas")
st.caption("Modelos Verticais (Retrato)")

# --- CONFIGURAÇÕES DE LAYOUTS VERTICAIS ---
LAYOUTS = {
    "A6 Vertical (6 por A4)": {"size": A4, "cols": 2, "rows": 3, "scale": 1.0},
    "A5 Vertical (2 por A4)": {"size": A4, "cols": 1, "rows": 2, "scale": 1.55},
    "A4 Vertical (1 por A4)": {"size": A4, "cols": 1, "rows": 1, "scale": 2.2},
    "A3 Vertical (1 por A3)": {"size": A3, "cols": 1, "rows": 1, "scale": 3.1},
}

def desenhar_etiqueta(c, item, x_base, y_base, col_w, row_h, scale):
    """Desenha os textos centralizados e organizados dentro do bloco de cada etiqueta"""
    
    # Centro horizontal da etiqueta atual
    x_center = x_base + (col_w / 2.0)

    # 1. DESCRIÇÃO DO PRODUTO (Centralizada e com quebra de linha se for longa)
    c.setFont("Helvetica-Bold", int(11 * scale))
    desc = item["desc"]
    palavras = desc.split()

    if len(desc) > 22 and len(palavras) > 1:
        meio = len(palavras) // 2
        linha1 = " ".join(palavras[:meio])
        linha2 = " ".join(palavras[meio:])
        c.drawCentredString(x_center, y_base + (row_h * 0.84), linha1)
        c.drawCentredString(x_center, y_base + (row_h * 0.76), linha2)
    else:
        c.drawCentredString(x_center, y_base + (row_h * 0.80), desc)

    # 2. BLOCO DE PREÇO
    if item["de"]:
        # --- MODO DE / POR ---
        # Preço DE (Menor, centralizado e riscado)
        c.setFont("Helvetica-Bold", int(10 * scale))
        p_de_str = f"De R$ {item['de']}"
        y_de = y_base + (row_h * 0.62)
        c.drawCentredString(x_center, y_de, p_de_str)
        
        # Risco exato sobre a largura do texto "De R$ XX,XX"
        largura_texto = c.stringWidth(p_de_str, "Helvetica-Bold", int(10 * scale))
        c.setLineWidth(1.5 * scale)
        c.line(x_center - (largura_texto / 2) - 2, y_de - 1, x_center + (largura_texto / 2) + 2, y_de + (8 * scale))

        # Preço POR (Grande e em destaque)
        c.setFont("Helvetica-Bold", int(26 * scale))
        y_por = y_base + (row_h * 0.45)
        c.drawCentredString(x_center, y_por, f"Por R$ {item['por']}")
        
        # Unidade (Logo abaixo do preço Por)
        c.setFont("Helvetica-Bold", int(9 * scale))
        c.drawCentredString(x_center, y_por - (12 * scale), item["un"])
    else:
        # --- MODO PREÇO ÚNICO ---
        c.setFont("Helvetica-Bold", int(32 * scale))
        y_por = y_base + (row_h * 0.50)
        c.drawCentredString(x_center, y_por, f"R$ {item['por']}")
        
        # Unidade
        c.setFont("Helvetica-Bold", int(10 * scale))
        c.drawCentredString(x_center, y_por - (14 * scale), item["un"])

    # 3. TARJA / AVISO DE REBAIXA (VALIDADE)
    if item["e_rebaixa"]:
        c.setFont("Helvetica-Bold", int(8 * scale))
        c.drawCentredString(x_center, y_base + (row_h * 0.25), "PRODUTO PRÓXIMO")
        c.drawCentredString(x_center, y_base + (row_h * 0.19), "A DATA DE VENCIMENTO")
        
        c.setFont("Helvetica-Bold", int(12 * scale))
        c.drawCentredString(x_center, y_base + (row_h * 0.09), f"VALIDADE: {item['val']}")


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

        desenhar_etiqueta(c, item, x_base, y_base, col_w, row_h, scale)

    c.save()
    buffer.seek(0)
    return buffer


# --- INTERFACE DE USUÁRIO (STREAMLIT) ---

if "lista_itens" not in st.session_state:
    st.session_state.lista_itens = []

modelo_selecionado = st.selectbox("Selecione o Formato da Folha:", list(LAYOUTS.keys()))

st.divider()

st.markdown("### 📝 Dados do Produto")

col_t1, col_t2 = st.columns(2)
with col_t1:
    tem_desconto = st.checkbox("Promocional com Desconto (De / Por)", value=True)
with col_t2:
    e_rebaixa = st.checkbox("Etiqueta de Rebaixa (Próximo à Validade)", value=True)

with st.form("form_produto", clear_on_submit=True):
    desc = st.text_input("Descrição do Produto:", placeholder="Ex: BISC MAIZENA CAPRICCHE 312G LEITE").upper()

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
        validade = st.text_input("Data de Validade:", placeholder="Ex: 01/08/2026")
    else:
        validade = ""

    btn_adicionar = st.form_submit_button("➕ Adicionar à Lista")

    if btn_adicionar:
        if desc and por:
            st.session_state.lista_itens.append({
                "desc": desc,
                "de": de.replace(".", ",").strip(),
                "por": por.replace(".", ",").strip(),
                "un": unidade,
                "val": validade,
                "e_rebaixa": e_rebaixa
            })
            st.success(f"Produto '{desc}' adicionado!")
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
        pdf_buffer = gerar_pdf_etiquetas(st.session_state.lista_itens, modelo_selecionado)
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
