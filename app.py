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
    topo_etiqueta = y_base + row_h  # Borda superior de cada etiqueta (0 a 99mm)

    # -------------------------------------------------------------------
    # 1. DESCRIÇÃO DO PRODUTO (Arial-Black 16pt | Distância de 40.8mm do topo)
    # -------------------------------------------------------------------
    tam_fonte_desc = int(16 * scale)
    c.setFont("Arial-Black", tam_fonte_desc)

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

        espacamento_linhas = (tam_fonte_desc * 0.35 + 1.8) * mm
        y_segunda_linha = y_primeira_linha - espacamento_linhas

        c.drawCentredString(x_center, y_primeira_linha, linha1)
        c.drawCentredString(x_center, y_segunda_linha, linha2)

    # -------------------------------------------------------------------
    # 2. BLOCO DE PREÇOS ("DE" E "POR")
    # -------------------------------------------------------------------
    if item["de"]:
        # --- A) Rótulo "De" e "R$" (Fonte tam 12) ---
        tam_fonte_de = int(12 * scale)
        c.setFont("Arial-Black", tam_fonte_de)

        x_de = x_base + (9.2 * mm * scale)
        y_de = topo_etiqueta - (62.2 * mm * scale)
        y_rs_de = topo_etiqueta - (66.5 * mm * scale)

        c.drawString(x_de, y_de, "De")
        c.drawString(x_de, y_rs_de, "R$")

        # --- B) Separação de Reais e Centavos (DE) ---
        val_de_raw = item["de"].replace(".", ",")
        if "," in val_de_raw:
            partes_de = val_de_raw.split(",")
            reais_de_str = partes_de[0]
            centavos_de_str = f",{partes_de[1]}"
        else:
            reais_de_str = val_de_raw
            centavos_de_str = ",00"

        # --- C) Reais DE (Fonte 26 | Topo 66.8mm | Lateral 14.5mm) ---
        tam_fonte_reais_de = int(26 * scale)
        c.setFont("Arial-Black", tam_fonte_reais_de)

        x_reais_de = x_base + (14.5 * mm * scale)
        y_reais_de = topo_etiqueta - (66.8 * mm * scale)
        c.drawString(x_reais_de, y_reais_de, reais_de_str)

        largura_reais_de = c.stringWidth(reais_de_str, "Arial-Black", tam_fonte_reais_de)

        # --- D) Centavos DE (Fonte 17 | Topo 64mm | +0.3mm dos Reais) ---
        tam_fonte_centavos_de = int(17 * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_de)

        x_centavos_de = x_reais_de + largura_reais_de + (0.3 * mm * scale)
        y_centavos_de = topo_etiqueta - (64.0 * mm * scale)
        c.drawString(x_centavos_de, y_centavos_de, centavos_de_str)

        largura_centavos_de = c.stringWidth(centavos_de_str, "Arial-Black", tam_fonte_centavos_de)

        # --- E) Unidade "De" (Fonte tam 8 | 3mm Abaixo | +4mm a Direita) ---
        tam_fonte_un_de = int(8 * scale)
        c.setFont("Arial-Black", tam_fonte_un_de)
        x_un_de = x_centavos_de + (largura_centavos_de / 2.0) + (4.0 * mm * scale)
        y_un_de = y_centavos_de - (3.0 * mm * scale)
        c.drawCentredString(x_un_de, y_un_de, item["un"])

        # --- F) Risco Diagonal (Linha de 2pt com sobra de 0.5mm) ---
        x_inicio_risco = x_reais_de - (0.5 * mm * scale)
        x_fim_risco = x_centavos_de + largura_centavos_de + (0.5 * mm * scale)

        y_inicio_risco = y_reais_de - (0.5 * mm * scale)
        y_fim_risco = y_centavos_de + (3.8 * mm * scale)

        c.setLineWidth(2.0 * scale)
        c.line(x_inicio_risco, y_inicio_risco, x_fim_risco, y_fim_risco)

        # --- G) Rótulos "Por" e "R$" (Fonte tam 18) ---
        tam_fonte_por_rotulo = int(18 * scale)
        c.setFont("Arial-Black", tam_fonte_por_rotulo)

        x_por = x_base + (46.3 * mm * scale)
        y_por = topo_etiqueta - (60.0 * mm * scale)

        x_rs_por = x_base + (48.4 * mm * scale)
        y_rs_por = topo_etiqueta - (67.1 * mm * scale)

        c.drawString(x_por, y_por, "Por")
        c.drawString(x_rs_por, y_rs_por, "R$")

        # --- H) Preço POR (Reais tam 58 | Centavos tam 32) ---
        val_por_raw = item["por"].replace(".", ",")
        if "," in val_por_raw:
            partes_por = val_por_raw.split(",")
            reais_por_str = partes_por[0]
            centavos_por_str = f",{partes_por[1]}"
        else:
            reais_por_str = val_por_raw
            centavos_por_str = ",00"

        # Reais POR (X=56.6mm | Y=70.5mm do topo - Ajustado para não invadir o rodapé)
        tam_fonte_reais_por = int(58 * scale)
        c.setFont("Arial-Black", tam_fonte_reais_por)

        x_reais_por = x_base + (56.6 * mm * scale)
        y_reais_por = topo_etiqueta - (70.5 * mm * scale)
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

        # Centavos POR (Y=65.5mm do topo | +0.3mm dos Reais)
        tam_fonte_centavos_por = int(32 * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_por)

        x_centavos_por = x_reais_por + largura_reais_por + (0.3 * mm * scale)
        y_centavos_por = topo_etiqueta - (65.5 * mm * scale)
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        # --- I) Unidade "Por" (Fonte tam 12 | 6mm Abaixo | +4mm a Direita) ---
        tam_fonte_un_por = int(12 * scale)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0) + (4.0 * mm * scale)
        y_un_por = y_centavos_por - (6.0 * mm * scale)
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    else:
        # --- MODO PREÇO ÚNICO ---
        val_por_raw = item["por"].replace(".", ",")
        if "," in val_por_raw:
            partes_por = val_por_raw.split(",")
            reais_por_str = partes_por[0]
            centavos_por_str = f",{partes_por[1]}"
        else:
            reais_por_str = val_por_raw
            centavos_por_str = ",00"

        tam_fonte_reais_por = int(58 * scale)
        c.setFont("Arial-Black", tam_fonte_reais_por)
        x_reais_por = x_base + (56.6 * mm * scale)
        y_reais_por = topo_etiqueta - (70.5 * mm * scale)
        c.drawString(x_reais_por, y_reais_por, reais_por_str)

        largura_reais_por = c.stringWidth(reais_por_str, "Arial-Black", tam_fonte_reais_por)

        tam_fonte_centavos_por = int(32 * scale)
        c.setFont("Arial-Black", tam_fonte_centavos_por)
        x_centavos_por = x_reais_por + largura_reais_por + (0.3 * mm * scale)
        y_centavos_por = topo_etiqueta - (65.5 * mm * scale)
        c.drawString(x_centavos_por, y_centavos_por, centavos_por_str)

        largura_centavos_por = c.stringWidth(centavos_por_str, "Arial-Black", tam_fonte_centavos_por)

        tam_fonte_un_por = int(12 * scale)
        c.setFont("Arial-Black", tam_fonte_un_por)
        x_un_por = x_centavos_por + (largura_centavos_por / 2.0) + (4.0 * mm * scale)
        y_un_por = y_centavos_por - (6.0 * mm * scale)
        c.drawCentredString(x_un_por, y_un_por, item["un"])

    # -------------------------------------------------------------------
    # 3. TARJA / AVISO DE REBAIXA (VALIDADE NO RODAPÉ - 83mm a 94mm DO TOPO)
    # -------------------------------------------------------------------
    if item["e_rebaixa"]:
        c.setFont("Arial-Black", int(9.5 * scale))
        y_aviso1 = topo_etiqueta - (83.0 * mm * scale)
        y_aviso2 = topo_etiqueta - (87.5 * mm * scale)
        
        c.drawCentredString(x_center, y_aviso1, "PRODUTO PRÓXIMO")
        c.drawCentredString(x_center, y_aviso2, "A DATA DE VENCIMENTO")

        c.setFont("Arial-Black", int(13 * scale))
        y_val = topo_etiqueta - (93.5 * mm * scale)
        c.drawCentredString(x_center, y_val, f"VALIDADE: {item['val']}")


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
