# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import urllib.parse
import unicodedata
import io
from PIL import Image, ImageDraw, ImageFont

try:
    import pytz
except ImportError:
    pass

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn')

class ListaComprasPro:
    def __init__(self):
        if 'categorias' not in st.session_state:
            raw_data = {
                "MERCEARIA": ["AÇÚCAR", "AMENDOIM", "ARROZ", "AZEITE", "AZEITONA", "BATATA FRITA", "BISCOITOS", "BOLACHAS", "CAFÉ", "CALDO GALINHA", "CHÁ", "COCO RALADO", "CREME DE LEITE", "ERVILHA", "ESSÊNCIA", "EXTRATO TOMATE", "FARINHA DE MILHO", "FARINHA DE TRIGO", "FARINHA MANDIOCA", "FARINHA ROSCA", "FARINHA TEMPERADA", "FEIJÃO", "FERMENTO", "FILTRO CAFÉ", "FLOCÃO DE MILHO", "FÓSFORO", "FUBÁ", "GELATINA", "KETCHUP", "LASANHA", "LEITE", "LEITE CONDENSADO", "LEITE DE COCO", "LENTILHA", "MACARRÃO", "MAIONESE", "MAISENA", "MASSA PIZZA", "MILHO VERDE", "MISTURA P/ BOLO", "MOLHO INGLÊS", "MOLHO TOMATE", "MOSTARDA", "ÓLEO", "OVOS", "PALMITO", "PÓ ROYAL", "TAPIOCA", "TEMPERO", "TODDY"],
                "LIMPEZA": ["ÁGUA SANITÁRIA", "ÁLCOOL", "AMACIANTE", "BICARBONATO", "BOMBRIL", "BUCHA BANHO", "BUCHA COZINHA", "CÊRA", "DESINFETANTE", "DETERGENTE", "LÂMPADA", "LISOFORME", "LUSTRA MÓVEIS", "PAPEL ALUMÍNIO", "PASTA PINHO", "PEDRA SANITÁRIA", "PEROBA", "RODO", "SABÃO BARRA", "SABÃO EM PÓ", "SACO DE LIXO", "VASSOURA", "VEJA", "VELA"],
                "HIGIENE": ["ACETONA", "ALGODÃO", "CONDICIONADOR", "DESODORANTE", "ESCOVA DE DENTE", "FIO DENTAL", "GUARDANAPO", "PAPEL HIGIÊNICO", "PASTA DE DENTE", "PRESTO-BARBA", "SABONETE", "SABONETE LÍQUIDO", "SHAMPOO"],
                "FRIOS": ["CHEDDAR", "EMPANADO", "GORGONZOLA", "HAMBURGUER", "IOGURTE", "MANTEIGA", "MARGARINA", "MORTADELA", "MUSSARELA", "PASTEL (MASSA)", "PRESUNTO", "QUEIJO", "REQUEIJÃO", "SALSICHA"],
                "FRUTAS / VERDURAS": ["ABÓBORA", "ALFACE", "ALHO", "BANANA", "BATATA", "BETERRABA", "CEBOLA", "CENOURA", "CHUCHU", "LARANJA", "LIMÃO", "MAÇÃ", "MAMÃO", "MELANCIA", "MELÃO", "PÊRA", "TOMATE"],
                "AÇOUGUE": ["ALCATRA", "ASINHA", "BACON", "BIFE", "CALABRESA", "CARNE MOÍDA", "COSTELÃO", "COSTELINHA", "COXINHA", "CUPIM", "FÍGADO", "FILÉ", "FILÉ DE PEITO", "FRALDINHA", "FRANGO", "LINGUA", "LINGUIÇA", "LOMBO", "MÚSCULO", "PICANHA"],
                "TEMPEROS": ["AÇÚCAR MASCAVO", "ALHO EM PÓ", "CEBOLA EM PÓ", "OREGANO", "PÁPRICA DEFUMADA", "PÁPRICA PICANTE", "PIMENTA DO REINO"],
                "BEBIDAS": ["ÁGUA MINERAL", "CERVEJA", "ENERGÉTICO", "REFRIGERANTE", "SUCO", "VINHO"],
                "OUTROS": []
            }
            st.session_state.categorias = {k: sorted(v, key=remover_acentos) for k, v in raw_data.items()}
        
        # Inicializa o controle de reset se não existir
        if 'reset_trigger' not in st.session_state:
            st.session_state.reset_trigger = 0

    def adicionar_item(self, nome):
        nome_upper = nome.upper()
        if nome_upper and nome_upper not in st.session_state.categorias["OUTROS"]:
            st.session_state.categorias["OUTROS"].append(nome_upper)
            st.session_state.categorias["OUTROS"].sort(key=remover_acentos)
            st.rerun()

    def limpar_tudo(self):
        # Desmarca os itens
        for chave in list(st.session_state.keys()):
            if chave.startswith("check_"):
                st.session_state[chave] = False
        
        # Altera o trigger para forçar o campo de texto a "nascer" de novo vazio
        st.session_state.reset_trigger += 1
        st.rerun()

    def gerar_imagem(self, itens, motivo):
        largura = 550
        espaco_item = 35
        altura_total = 180 + (len(itens) * espaco_item) + 80
        img = Image.new('RGB', (largura, altura_total), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        d.text((20, 20), "LISTA DE COMPRAS", fill=(0, 0, 0))
        d.text((20, 45), f"DATA: {data_br}", fill=(100, 100, 100))
        y_linha = 100
        if motivo:
            d.text((20, 85), f"MOTIVO: {motivo.upper()}", fill=(0, 50, 150))
            y_linha = 120
        d.line((20, y_linha, 530, y_linha), fill=(0, 0, 0), width=2)
        y = y_linha + 20
        for item in itens:
            d.text((30, y), f"[X] {item}", fill=(0, 0, 0))
            y += espaco_item
        d.text((20, y + 20), "by rvrs", fill=(150, 150, 150))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def gerar_whatsapp_texto(self, lista_final, motivo):
        lista_final.sort(key=remover_acentos)
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        cabecalho = f"*--- LISTA DE COMPRAS ({data_br}) ---*\n"
        if motivo:
            cabecalho += f"\n*MOTIVO:* {motivo.upper()}\n"
        corpo = "\n" + "\n".join([f"[X] {item}" for item in lista_final])
        assinatura = "\n\nby ®rvrs"
        return f"https://wa.me/?text={urllib.parse.quote(cabecalho + corpo + assinatura)}"

# --- Interface ---
st.set_page_config(page_title="Lista Pro rvrs", layout="wide")

st.markdown("""
    <style>
    .main-title { font-family: 'Arial Black', sans-serif; text-align: center; border-bottom: 3px solid #000; text-transform: uppercase; font-size: 30px; }
    .stMarkdown h3 { background-color: #000; color: #fff !important; padding: 5px 15px; text-transform: uppercase; font-size: 16px !important; }
    .stCheckbox { margin-bottom: -15px; }
    </style>
    """, unsafe_allow_html=True)

app = ListaComprasPro()
st.markdown('<h1 class="main-title">Lista de Compras</h1>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("📋 CONFIGURAÇÃO")
    
    # O SEGREDO: A key muda toda vez que clicamos em limpar, forçando o widget a resetar
    motivo_compra = st.text_input(
        "Motivo da Compra:", 
        placeholder="Ex: Festa na Fazenda", 
        key=f"motivo_ti_{st.session_state.reset_trigger}"
    )
    
    st.divider()
    if st.button("🗑️ LIMPAR TUDO", use_container_width=True):
        app.limpar_tudo()
    
    st.divider()
    with st.form("add_item_form", clear_on_submit=True):
        novo = st.text_input("➕ Adicionar Item (Outros):")
        submitted = st.form_submit_button("ADICIONAR ITEM", use_container_width=True)
        if submitted and novo:
            app.adicionar_item(novo)
    
    st.divider()
    selecionados = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]

    if selecionados:
        url_wa = app.gerar_whatsapp_texto(selecionados, motivo_compra)
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:8px;text-align:center;font-weight:bold;margin-bottom:10px;">ENVIAR TEXTO</div></a>', unsafe_allow_html=True)
        img_bytes = app.gerar_imagem(sorted(selecionados, key=remover_acentos), motivo_compra)
        st.download_button(label="🖼️ BAIXAR IMAGEM", data=img_bytes, file_name=f"lista_{motivo_compra or 'compras'}.png", mime="image/png", use_container_width=True)
    else:
        st.info("Selecione itens na lista.")

# --- Colunas ---
col1, col2, col3 = st.columns(3)
todas_cats = list(st.session_state.categorias.items())

for i, (cat, produtos) in enumerate(todas_cats):
    target_col = [col1, col2, col3][i % 3]
    with target_col:
        st.subheader(cat)
        for p in produtos:
            st.checkbox(p, key=f"check_{p}_{cat}")

st.write("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<p style='text-align:center; color:grey;'>2026 Lista de Compras | Desenvolvido por ®rvrs</p>", unsafe_allow_html=True)
