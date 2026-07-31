import base64
import io
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A3, A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# --- REGISTRO DA FONTE CUSTOMIZADA ---
pdfmetrics.registerFont(TTFont("Arial-Black", "arialblack.ttf"))

st.set_page_config(
    page_title="Gerador de Etiquetas - Novo Atacarejo", layout="centered"
)

st.title("🏷️ Gerador de Etiquetas")
st.caption("Ajuste Fino - Modelo A6 Vertical")

# --- CONFIGURAÇÕES DE LAYOUTS VERTICAIS ---
LAYOUTS = {
    "A6 Vertical (6 por A4)": {"size": A4, "cols": 2, "rows": 3, "scale": 1.0},
    "A5 Vertical (2 por A4)": {"size": A4, "cols": 1, "rows": 2, "scale": 1.55},
    "A4 Vertical (1 por A4)": {"size": A4, "cols": 1, "rows": 1, "scale": 2.2},
    "A3 Vertical (1 por A3)": {"size": A3, "cols": 1, "rows": 1, "scale": 3.1},
}


def desenhar_etiqueta(c, item, x_base, y_base, col_w, row_h, scale):
    """Desenha a etiqueta com precisão milimétrica para o modelo A6"""

    x_center = x_base + (col_w / 2.0)
    topo_etiqueta = y_base + row_h  # Borda superior de cada retângulo de etiqueta

    # -------------------------------------------------------------------
    # 1. DESCRIÇÃO DO PRODUTO (Arial-Black 14pt | Distância de 40.8mm do topo)
    # -------------------------------------------------------------------
    tam_fonte_desc = int(14 * scale)
    c.setFont("Arial-Black", tam_fonte_desc)
    
    # Posição Y inicial: Exatamente 40,8 mm abaixo do topo da etiqueta
    y_primeira_linha = topo_etiqueta - (40.8 * mm * scale)

    desc = item["desc"]

    # Se tiver até 31 caracteres (contando espaços), imprime em 1 linha
    if len(desc) <= 31:
        c.drawCentredString(x_center, y_primeira_linha, desc)
    else:
        # Quebra em 2 linhas respeitando o limite de 31 caracteres por linha
        palavras = desc.split()
        linha1 = ""
        linha2 = ""

        for palavra in palavras:
            teste_linha1 = f"{linha1} {palavra}".strip()
            if len(teste_linha1) <= 31 and not linha2:
                linha1 = teste_linha1
            else:
                linha2 = f"{linha2} {palavra}".strip()

        # Espaçamento entre a 1ª e a 2ª linha do nome do produto
        espacamento_linhas = (tam_fonte_desc * 0.35 + 1.8) * mm
        y_segunda_linha = y_primeira_linha - espacamento_linhas
        
        c.drawCentredString(x_center, y_primeira_linha, linha1)
        c.drawCentredString(x_center, y_segunda_linha, linha2)

    # -------------------------------------------------------------------
    # 2. BLOCO DE PREÇO (MANTIDO PARA OS PRÓXIMOS PASSOS)
    # -------------------------------------------------------------------
    if item["de"]:
        # --- MODO DE / POR ---
        c.setFont("Arial-Black", int(9 * scale))
        p_de_str = f"De R$ {item['de']}"
        y_de = y_base + (row_h * 0.52)
        c.drawCentredString(x_center, y_de, p_de_str)

        # Risco sobre o preço antigo
        largura_texto = c.stringWidth(p_de_str, "Arial-Black", int(9 * scale))
        c.setLineWidth(1.5 * scale)
        c.line(
            x_center - (largura_texto / 2) - 2,
            y_de - 1,
            x_center + (largura_texto / 2) + 2,
            y_de + (7 * scale),
        )

        # Preço POR
        c.setFont("Arial-Black", int(24 * scale))
        y_por = y_base + (row_h * 0.36)
        c.drawCentredString(x_center, y_por, f"Por R$ {item['por']}")

        # Unidade
        c.setFont("Arial-Black", int(8 * scale))
        c.drawCentredString(x_center, y_por - (12 * scale), item["un"])
    else:
        # --- MODO PREÇO ÚNICO ---
        c.setFont("Arial-Black", int(28 * scale))
        y_por = y_base + (row_h * 0.40)
        c.drawCentredString(x_center, y_por, f"R$ {item['por']}")

        # Unidade
        c.setFont("Arial-Black", int(9 * scale))
        c.drawCentredString(x_center, y_por - (14 * scale), item["un"])

    # -------------------------------------------------------------------
    # 3. TARJA / AVISO DE REBAIXA (VALIDADE)
    # -------------------------------------------------------------------
    if item["e_rebaixa"]:
        c.setFont("Arial-Black", int(7.5 * scale))
        c.drawCentredString(x_center, y_base + (row_h * 0.22), "PRODUTO PRÓXIMO")
        c.drawCentredString(
            x_center, y_base + (row_h * 0.16), "A DATA DE VENCIMENTO"
        )

        c.setFont("Arial-Black", int(11 * scale))
        c.drawCentredString(
            x_center, y_base + (row_h * 0.07), f"VALIDADE: {item['val']}"
        )


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
                "e_rebaixa": e_rebaixa,
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
