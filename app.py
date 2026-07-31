import io
import streamlit as st
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
    """Desenha apenas os textos essenciais na etiqueta"""
    
    # 1. DESCRIÇÃO DO PRODUTO
    c.setFont("Helvetica-Bold", int(10 * scale))
    c.drawString(x_base + (32 * mm * (scale if scale < 2 else 1.2)), y_base + (row_h * 0.70), item["desc"])

    # 2. BLOCO DE PREÇO (De/Por vs Preço Único)
    if item["de"]:
        # --- MODO DE / POR ---
        c.setFont("Helvetica-Bold", int(8 * scale))
        p_de_x = x_base + (35 * mm * (scale if scale < 2 else 1.2))
        p_de_y = y_base + (row_h * 0.48)
        c.drawString(p_de_x, p_de_y, f"De R$ {item['de']}")
        
        # Risco diagonal sobre o preço antigo
        c.setLineWidth(1.1 * scale)
        c.line(p_de_x - (1 * mm), p_de_y - (1 * mm), p_de_x + (16 * mm * scale), p_de_y + (5 * mm * scale))

        # Preço NOVO
        c.setFont("Helvetica-Bold", int(22 * scale))
        c.drawString(x_base + (58 * mm * (scale if scale < 2 else 1.1)), y_base + (row_h * 0.40), f"Por R$ {item['por']}")
    else:
        # --- MODO PREÇO ÚNICO ---
        c.setFont("Helvetica-Bold", int(24 * scale))
        c.drawString(x_base + (45 * mm * (scale if scale < 2 else 1.1)), y_base + (row_h * 0.43), f"R$ {item['por']}")

    # 3. UNIDADE DE MEDIDA
    c.setFont("Helvetica-Bold", int(8 * scale))
    c.drawString(x_base + (col_w - (18 * mm * scale)), y_base + (row_h * 0.38), item["un"])

    # 4. TARJA / AVISO DE REBAIXA (VALIDADE)
    if item["e_rebaixa"]:
        c.setFont("Helvetica-Bold", int(6 * scale))
        c.drawString(x_base + (32 * mm * (scale if scale < 2 else 1.2)), y_base + (row_h * 0.22), "PRODUTO PRÓXIMO A DATA DE VENCIMENTO")
        
        c.setFont("Helvetica-Bold", int(9 * scale))
        c.drawString(x_base + (32 * mm * (scale if scale < 2 else 1.2)), y_base + (row_h * 0.13), f"VALIDADE: {item['val']}")


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

# Escolha do modelo
modelo_selecionado = st.selectbox("Selecione o Formato da Folha:", list(LAYOUTS.keys()))

st.divider()

st.markdown("### 📝 Dados do Produto")

# Toggles de Configuração Rápida
col_t1, col_t2 = st.columns(2)
with col_t1:
    tem_desconto = st.checkbox("Promocional com Desconto (De / Por)", value=True)
with col_t2:
    e_rebaixa = st.checkbox("Etiqueta de Rebaixa (Próximo à Validade)", value=True)

with st.form("form_produto", clear_on_submit=True):
    desc = st.text_input("Descrição do Produto:", placeholder="Ex: BISC MAIZENA CAPRICCHE 312G LEITE").upper()

    # Preços e Unidade
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

    # Data de Validade (apenas se for rebaixa)
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

# Tabela e Botão de Download
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
        pdf_bytes = gerar_pdf_etiquetas(st.session_state.lista_itens, modelo_selecionado)
        st.download_button(
            label="📄 BAIXAR PDF PRONTO",
            data=pdf_bytes,
            file_name=f"etiquetas_{modelo_selecionado.split()[0].lower()}.pdf",
            mime="application/pdf"
        )
