# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import urllib.parse
import unicodedata
import io
import re

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
def normalizar_texto(texto):
    if not texto: return ""
    texto = str(texto).strip().lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn')

def formatar_nome_arquivo(texto):
    if not texto: return "lista-compras"
    texto = normalizar_texto(texto)
    return re.sub(r'[^a-z0-9]', '-', texto)

class ListaComprasPro:
    def __init__(self):
        if 'categorias' not in st.session_state:
            self.resetar_estoque_padrao()
        if 'reset_trigger' not in st.session_state:
            st.session_state.reset_trigger = 0
        if 'busca_key' not in st.session_state:
            st.session_state.busca_key = 0
        if 'selecionados' not in st.session_state:
            st.session_state.selecionados = {}

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
        st.session_state.categorias = {k: sorted(v, key=normalizar_texto) for k, v in raw_data.items()}

    def adicionar_item(self, nome):
        nome_upper = str(nome).upper()
        if nome_upper and nome_upper not in st.session_state.categorias["OUTROS"]:
            st.session_state.categorias["OUTROS"].append(nome_upper)
            st.session_state.categorias["OUTROS"].sort(key=normalizar_texto)
            st.rerun()

    def limpar_tudo(self):
        st.session_state.selecionados = {}
        st.session_state.reset_trigger += 1
        st.session_state.busca_key += 1
        st.rerun()

    def criar_minha_lista(self):
        st.session_state.selecionados = {}
        for cat in list(st.session_state.categorias.keys()):
            if cat != "OUTROS":
                st.session_state.categorias[cat] = []
        st.session_state.reset_trigger += 1
        st.rerun()
        
    def gerar_imagem(self, itens_lista, motivo_texto):
        # Aumentamos a largura para a imagem ficar mais imponente
        largura = 600
        espaco_item = 45
        y_cabecalho = 180 if motivo_texto else 130
        altura_total = max(450, y_cabecalho + (len(itens_lista) * espaco_item) + 120)
        img = Image.new('RGB', (largura, altura_total), color=(255, 255, 255))
        d = ImageDraw.Draw(img)

        # Caminhos de fontes comuns no Linux (GitHub Codespaces / Streamlit Cloud)
        caminhos_bold = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        caminhos_norm = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

        # Busca a melhor fonte disponível ou usa a padrão do sistema em tamanho grande
        font_bold = None
        for f in caminhos_bold:
            if os.path.exists(f):
                font_bold = ImageFont.truetype(f, 32)
                break
        if not font_bold: font_bold = ImageFont.load_default(size=32)

        font_norm = None
        for f in caminhos_norm:
            if os.path.exists(f):
                font_norm = ImageFont.truetype(f, 24)
                break
        if not font_norm: font_norm = ImageFont.load_default(size=24)
        
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        
        # Desenho
        d.text((40, 40), "LISTA DE COMPRAS", fill=(0, 0, 0), font=font_bold)
        d.text((40, 85), f"Data: {data_br}", fill=(100, 100, 100), font=font_norm)
        
        y_linha = 130
        if motivo_texto:
            d.text((40, 125), f"MOTIVO: {str(motivo_texto).upper()}", fill=(0, 51, 153), font=font_bold)
            y_linha = 175
            
        d.line((40, y_linha, largura-40, y_linha), fill=(0, 0, 0), width=3)
        y = y_linha + 30
        for item in itens_lista:
            d.text((50, y), f"[x] {item}", fill=(0, 0, 0), font=font_norm)
            y += espaco_item
        
        d.text((40, y + 30), "by ®rvrs", fill=(170, 170, 170), font=font_norm)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def gerar_whatsapp_texto(self, lista_final, motivo_texto):
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        texto_msg = f"*LISTA DE COMPRAS*\n*{data_br}*\n\n"
        if motivo_texto:
            texto_msg += f"*MOTIVO:* {str(motivo_texto).upper()}\n\n"
        texto_msg += "\n".join([f"[x] {item}" for item in sorted(lista_final, key=normalizar_texto)])
        texto_msg += "\n\n_by ®rvrs_"
        return f"https://wa.me/?text={urllib.parse.quote(texto_msg)}"

# --- Interface ---
st.markdown("""<style>
    .main-title { font-family: 'Arial Black'; text-align: center; border-bottom: 3px solid #000; text-transform: uppercase; font-size: 30px; }
    .stMarkdown h3 { background-color: #000; color: #fff !important; padding: 10px; border-radius: 5px; margin-top: 10px; }
    </style>""", unsafe_allow_html=True)

app = ListaComprasPro()
st.markdown('<h1 class="main-title">🛒Lista de Compras</h1>', unsafe_allow_html=True)

# --- BUSCA ---
c_busca, c_limpa = st.columns([4, 1])
with c_busca:
    busca_input = st.text_input("🔍 Pesquisar...", placeholder="Digite para filtrar...", key=f"input_busca_{st.session_state.busca_key}", label_visibility="collapsed")
with c_limpa:
    if st.button("❌ Limpar", use_container_width=True):
        st.session_state.busca_key += 1
        st.rerun()

busca_termo = normalizar_texto(busca_input)

# --- Sidebar ---
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

# --- Processamento ---
itens_para_exportar = [f"{nome} ({dados['qtd']})" for nome, dados in st.session_state.selecionados.items()]

# --- Exibição ---
if modo_mercado:
    st.markdown("## 🛒 MODO MERCADO")
    if itens_para_exportar:
        filtrados = [i for i in itens_para_exportar if busca_termo in normalizar_texto(i)]
        for item in sorted(filtrados, key=normalizar_texto):
            st.write(f"### [x] {item}")
    else: st.info("Nenhum item selecionado.")
else:
    col1, col2, col3 = st.columns(3)
    for i, (cat_nome, produtos) in enumerate(st.session_state.categorias.items()):
        produtos_f = [p for p in produtos if busca_termo in normalizar_texto(p)]
        if produtos_f:
            with [col1, col2, col3][i % 3]:
                st.subheader(str(cat_nome))
                for p in produtos_f:
                    c1, c2 = st.columns([3, 1])
                    foi_sel = p in st.session_state.selecionados
                    qtd_ini = st.session_state.selecionados[p]['qtd'] if foi_sel else 1
                    with c1:
                        # Chave única baseada no produto, categoria e reset_trigger para resetar visualmente
                        marcado = st.checkbox(p, value=foi_sel, key=f"chk_{p}_{cat_nome}_{st.session_state.reset_trigger}")
                    if marcado:
                        with c2:
                            qtd = st.number_input("Q", 1, 100, qtd_ini, key=f"q_{p}_{cat_nome}_{st.session_state.reset_trigger}", label_visibility="collapsed")
                        st.session_state.selecionados[p] = {'qtd': qtd}
                    else:
                        if p in st.session_state.selecionados: del st.session_state.selecionados[p]

# --- Exportação ---
with st.sidebar:
    st.divider()
    if itens_para_exportar:
        url_wa = app.gerar_whatsapp_texto(itens_para_exportar, motivo_input)
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:8px;text-align:center;font-weight:bold;margin-bottom:10px;">📲 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
        nome_f = formatar_nome_arquivo(motivo_input)
        img_bytes = app.gerar_imagem(sorted(itens_para_exportar, key=normalizar_texto), motivo_input)
        st.download_button("🖼️ BAIXAR IMAGEM", img_bytes, f"{nome_f}.png", "image/png", use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:grey;'>2026 🛒Lista de Compras | by ®rvrs</p>", unsafe_allow_html=True)
