# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import urllib.parse
import unicodedata
import io

try:
    import pytz
except ImportError:
    pass

# 1. Configuração da Página e Ícone
try:
    caminho_icone = os.path.join(os.getcwd(), "favicon.png")
    img_favicon = Image.open(caminho_icone)
except:
    img_favicon = "🛒"

st.set_page_config(
    page_title="🛒Lista Compras ®rvrs",
    page_icon=img_favicon, 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Funções de Suporte
def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn')

class ListaComprasPro:
    def __init__(self):
        if 'categorias' not in st.session_state:
            self.resetar_estoque_padrao()
        if 'reset_trigger' not in st.session_state:
            st.session_state.reset_trigger = 0

    def resetar_estoque_padrao(self):
        raw_data = {
            "MERCEARIA": ["AÇÚCAR", "AMENDOIM", "ARROZ", "AZEITE", "AZEITONA", "BATATA FRITA", "BISCOITOS", "BOLACHAS", "CAFÉ", "CALDO GALINHA", "CHÁ", "COCO RALADO", "CREME DE LEITE", "ERVILHA", "ESSÊNCIA", "EXTRATO TOMATE", "FARINHA DE MILHO", "FARINHA DE TRIGO", "FARINHA MANDIOCA", "FARINHA ROSCA", "FARINHA TEMPERADA", "FEIJÃO", "FERMENTO", "FILTRO CAFÉ", "FLOCÃO DE MILHO", "FÓSFORO", "FUBÁ", "GELATINA", "KETCHUP", "LASANHA", "LEITE", "LEITE CONDENSADO", "LEITE DE COCO", "LENTILHA", "MACARRÃO", "MAIONESE", "MAISENA", "MASSA PIZZA", "MILHO VERDE", "MISTURA P/ BOLO", "MOLHO INGLÊS", "MOLHO TOMATE", "MOSTARDA", "ÓLEO", "OVOS", "PALMITO", "PÓ ROYAL", "TAPIOCA", "TEMPERO", "TODDY"],
            "LIMPEZA": ["ÁGUA SANITÁRIA", "ÁLCOOL", "AMACIANTE", "BICARBONATO", "BOMBRIL", "BUCHA BANHO", "BUCHA COZINHA", "CÊRA", "DESINFETANTE", "DETERGENTE", "LÂMPADA", "LISOFORME", "LUSTRA MÓVEIS", "PAPEL ALUMÍNIO", "PASTA PINHO", "PEDRA SANITÁRIA", "PEROBA", "RODO", "SABÃO BARRA", "SABÃO EM PÓ", "SACO DE LIXO", "VASSOURA", "VEJA", "VELA"],
            "HIGIENE": ["ACETONA", "ALGODÃO", "CONDICIONADOR", "DESODORANTE", "ESCOVA DE DENTE", "FIO DENTAL", "GUARDANAPO", "PAPEL HIGIÊNICO", "PASTA DE DENTE", "PRESTOBARBA", "SABONETE", "SABONETE LÍQUIDO", "SHAMPOO"],
            "FRIOS": ["CHEDDAR", "EMPANADO", "GORGONZOLA", "HAMBURGUER", "IOGURTE", "MANTEIGA", "MARGARINA", "MORTADELA", "MUSSARELA", "PASTEL (MASSA)", "PRESUNTO", "QUEIJO", "REQUEIJÃO", "SALSICHA"],
            "FRUTAS / VERDURAS": ["ABÓBORA", "ALFACE", "ALHO", "BANANA", "BATATA", "BETERRABA", "CEBOLA", "CENOURA", "CHUCHU", "LARANJA", "LIMÃO", "MAÇÃ", "MAMÃO", "MELANCIA", "MELÃO", "PÊRA", "TOMATE"],
            "AÇOUGUE": ["ALCATRA", "ASINHA", "BACON", "BIFE", "CALABRESA", "CARNE MOÍDA", "COSTELÃO", "COSTELINHA", "COXINHA", "CUPIM", "FÍGADO", "FILÉ", "FILÉ DE PEITO", "FRALDINHA", "FRANGO", "LINGUA", "LINGUIÇA", "LOMBO", "MÚSCULO", "PICANHA"],
            "TEMPEROS": ["AÇÚCAR MASCAVO", "ALHO EM PÓ", "CEBOLA EM PÓ", "OREGANO", "PÁPRICA DEFUMADA", "PÁPRICA PICANTE", "PIMENTA DO REINO"],
            "BEBIDAS": ["ÁGUA MINERAL", "CERVEJA", "ENERGÉTICO", "REFRIGERANTE", "SUCO", "VINHO"],
            "OUTROS": []
        }
        st.session_state.categorias = {k: sorted(v, key=remover_acentos) for k, v in raw_data.items()}

    def adicionar_item(self, nome):
        nome_upper = str(nome).upper()
        if nome_upper and nome_upper not in st.session_state.categorias["OUTROS"]:
            st.session_state.categorias["OUTROS"].append(nome_upper)
            st.session_state.categorias["OUTROS"].sort(key=remover_acentos)
            st.rerun()

    def limpar_tudo(self):
        for chave in list(st.session_state.keys()):
            if chave.startswith("check_"):
                st.session_state[chave] = False
        st.session_state.reset_trigger += 1
        st.rerun()

    def criar_minha_lista(self):
        for chave in list(st.session_state.keys()):
            if chave.startswith("check_"):
                st.session_state[chave] = False
        for cat in list(st.session_state.categorias.keys()):
            if cat != "OUTROS":
                st.session_state.categorias[cat] = []
        st.session_state.reset_trigger += 1
        st.rerun()
        
    def gerar_imagem(self, itens_lista, motivo_texto):
        largura = 600
        espaco_item = 40
        y_cabecalho = 180 if motivo_texto else 130
        altura_total = y_cabecalho + (len(itens_lista) * espaco_item) + 100
        img = Image.new('RGB', (largura, altura_total), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 26)
            font_norm = ImageFont.truetype("arial.ttf", 20)
        except:
            font_bold = ImageFont.load_default()
            font_norm = ImageFont.load_default()
        
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        
        d.text((40, 35), "Lista de Compras", fill=(0, 0, 0), font=font_bold)
        d.text((40, 75), f"{data_br}", fill=(100, 100, 100), font=font_norm)
        
        y_linha = 120
        if motivo_texto:
            d.text((40, 115), f"MOTIVO: {str(motivo_texto).upper()}", fill=(0, 51, 153), font=font_bold)
            y_linha = 155
            
        d.line((40, y_linha, largura-40, y_linha), fill=(0, 0, 0), width=3)
        y = y_linha + 30
        for item in itens_lista:
            # Imprime [x] Item (Qtd)
            d.text((45, y), f"[x] {item}", fill=(0, 0, 0), font=font_norm)
            y += espaco_item
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
   
    def gerar_whatsapp_texto(self, lista_final, motivo_texto):
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        texto_msg = f"*LISTA DE COMPRAS*\n"
        texto_msg += f"*{data_br}*\n\n"
        if motivo_texto:
            texto_msg += f"*MOTIVO:* {str(motivo_texto).upper()}\n\n"
        # Imprime [x] Item (Qtd) no texto do zap
        texto_msg += "\n".join([f"[x] {item}" for item in sorted(lista_final, key=remover_acentos)])
        texto_msg += "\n\n_by ®rvrs_"
        return f"https://wa.me/?text={urllib.parse.quote(texto_msg)}"

# --- Interface Estilo CSS ---
st.markdown("""<style>
    .main-title { font-family: 'Arial Black'; text-align: center; border-bottom: 3px solid #000; text-transform: uppercase; font-size: 30px; }
    .stMarkdown h3 { background-color: #000; color: #fff !important; padding: 10px; border-radius: 5px; margin-top: 10px; }
    </style>""", unsafe_allow_html=True)

app = ListaComprasPro()
st.markdown('<h1 class="main-title">🛒Lista de Compras</h1>', unsafe_allow_html=True)

itens_para_exportar = []

# --- Barra Lateral ---
with st.sidebar:
    st.header("📋 CONFIGURAÇÃO")
    motivo_input = st.text_input("Motivo da Compra:", placeholder="Ex: Churrasco", key=f"mot_{st.session_state.reset_trigger}")
    st.divider()
    modo_mercado = st.toggle("## 🛒 MODO MERCADO ATIVO")
    if st.button("✨ CRIAR MINHA LISTA", use_container_width=True): app.criar_minha_lista()
    if st.button("🔄 RESTAURAR PADRÃO", use_container_width=True): 
        app.resetar_estoque_padrao()
        st.rerun()
    if st.button("🗑️ DESMARCAR TUDO", use_container_width=True): app.limpar_tudo()
    st.divider()
    with st.form("add_item", clear_on_submit=True):
        novo = st.text_input("➕ Adicionar Item:")
        if st.form_submit_button("ADICIONAR") and novo: app.adicionar_item(novo)

# --- Lógica de Processamento ---
for k, v in st.session_state.items():
    if k.startswith("check_") and v:
        partes = k.split("_")
        if len(partes) >= 2:
            nome_item = "_".join(partes[1:-1])
            cat_item = partes[-1]
            
            # Pega a quantidade do session_state
            qtd = st.session_state.get(f"q_{nome_item}_{cat_item}", 1)
            
            # AGORA SEMPRE IMPRIME: Item (Quantidade)
            texto_final = f"{nome_item} ({qtd})"
            
            if texto_final not in itens_para_exportar:
                itens_para_exportar.append(texto_final)

# --- Exibição Principal ---
if modo_mercado:
    st.markdown("## 🛒 MODO MERCADO")
    if itens_para_exportar:
        for item in sorted(itens_para_exportar, key=remover_acentos):
            st.write(f"### [x] {item}")
    else:
        st.info("Nenhum item selecionado.")
else:
    col1, col2, col3 = st.columns(3)
    categorias_ativas = [(k, v) for k, v in st.session_state.categorias.items() if v or k == "OUTROS"]
    
    for i, (cat_nome, produtos) in enumerate(categorias_ativas):
        col_atual = [col1, col2, col3][i % 3]
        with col_atual:
            st.subheader(str(cat_nome))
            for p in produtos:
                c_check, c_qtd = st.columns([3, 1])
                with c_check:
                    marcado = st.checkbox(p, key=f"check_{p}_{cat_nome}")
                if marcado:
                    with c_qtd:
                        st.number_input("Q", 1, 100, 1, key=f"q_{p}_{cat_nome}", label_visibility="collapsed")

# --- Exportação na Sidebar ---
with st.sidebar:
    st.divider()
    if itens_para_exportar:
        url_wa = app.gerar_whatsapp_texto(itens_para_exportar, motivo_input)
        st.markdown(f'''
            <a href="{url_wa}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366;color:white;padding:15px;border-radius:8px;text-align:center;font-weight:bold;margin-bottom:10px;">
                    📲 ENVIAR WHATSAPP
                </div>
            </a>''', unsafe_allow_html=True)
        
        img_bytes = app.gerar_imagem(sorted(itens_para_exportar, key=remover_acentos), motivo_input)
        st.download_button("🖼️ BAIXAR IMAGEM", img_bytes, "lista_compras.png", "image/png", use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:grey;'>2026 🛒Lista de Compras | by ®rvrs</p>", unsafe_allow_html=True)
