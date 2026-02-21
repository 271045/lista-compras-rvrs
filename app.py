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
            "HIGIENE": ["ACETONA", "ALGODÃO", "CONDICIONADOR", "DESODORANTE", "ESCOVA DE DENTE", "FIO DENTAL", "GUARDANAPO", "PAPEL HIGIÊNICO", "PASTA DE DENTE", "PRESTO-BARBA", "SABONETE", "SABONETE LÍQUIDO", "SHAMPOO"],
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

    def gerar_imagem(self, itens, motivo_texto):
        # ESCALA SUPER HD (3x mais densidade de pixels)
        escala = 3
        largura = 700 * escala
        item_h = 50 * escala
        margem = 60 * escala
        topo = 240 * escala if motivo_texto else 180 * escala
        altura_total = topo + (len(itens) * item_h) + margem
        
        img = Image.new('RGB', (largura, altura_total), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        try:
            # Fontes em tamanhos grandes para preservar bordas nítidas
            f_titulo = ImageFont.truetype("arialbd.ttf", 45 * escala)
            f_data = ImageFont.truetype("arial.ttf", 28 * escala)
            f_motivo = ImageFont.truetype("arialbd.ttf", 34 * escala)
            f_itens = ImageFont.truetype("arial.ttf", 32 * escala)
        except:
            f_titulo = f_data = f_motivo = f_itens = ImageFont.load_default()
        
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        
        # Desenho dos elementos com contraste máximo (Preto 0,0,0)
        d.text((margem, 50 * escala), "LISTA DE COMPRAS", fill=(0, 0, 0), font=f_titulo)
        d.text((margem, 110 * escala), f"DATA: {data_br}", fill=(80, 80, 80), font=f_data)
        
        y_atual = 160 * escala
        if motivo_texto:
            d.text((margem, y_atual), f"MOTIVO: {str(motivo_texto).upper()}", fill=(0, 51, 153), font=f_motivo)
            y_atual += 60 * escala
            
        d.line((margem, y_atual, largura - margem, y_atual), fill=(0, 0, 0), width=4 * escala)
        
        y_itens = y_atual + 50 * escala
        for item in itens:
            d.text((margem + 10, y_itens), f"[X] {item}", fill=(0, 0, 0), font=f_itens)
            y_itens += item_h
            
        # Borda de segurança para evitar compressão agressiva das bordas
        d.rectangle([0, 0, largura-1, altura_total-1], outline=(220, 220, 220), width=2 * escala)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', optimize=False)
        return img_byte_arr.getvalue()

    def gerar_whatsapp_texto(self, lista_final, motivo_texto):
        fuso_br = pytz.timezone('America/Sao_Paulo')
        data_br = datetime.now(fuso_br).strftime("%d/%m/%Y")
        texto_msg = f"*--- LISTA DE COMPRAS ---*\n"
        texto_msg += f"*{data_br}*\n\n"
        if motivo_texto:
            texto_msg += f"*MOTIVO:* {str(motivo_texto).upper()}\n\n"
        texto_msg += "\n".join([f"[X] {item}" for item in sorted(lista_final, key=remover_acentos)])
        texto_msg += "\n\n_by ®rvrs_"
        return f"https://wa.me/?text={urllib.parse.quote(texto_msg)}"

# --- Interface ---
st.set_page_config(page_title="Lista Compras ®rvrs", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    .main-title { font-family: 'Arial Black'; text-align: center; border-bottom: 3px solid #000; text-transform: uppercase; font-size: 30px; }
    .stMarkdown h3 { background-color: #000; color: #fff !important; padding: 10px; border-radius: 5px; }
    </style>""", unsafe_allow_html=True)

app = ListaComprasPro()
st.markdown('<h1 class="main-title">Lista de Compras</h1>', unsafe_allow_html=True)

total_estimado = 0.0
itens_marcados_nomes = []

with st.sidebar:
    st.header("📋 CONFIGURAÇÃO")
    motivo_input = st.text_input("Motivo da Compra:", placeholder="Ex: Churrasco", key=f"mot_{st.session_state.reset_trigger}")
    st.divider()
    modo_mercado = st.toggle("MODO MERCADO")
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
for k, v in st.session_state.items():
    if k.startswith("check_") and v:
        partes = k.split("_")
        if len(partes) >= 2:
            nome_item = "_".join(partes[1:-1])
            if nome_item not in itens_marcados_nomes:
                itens_marcados_nomes.append(nome_item)

if modo_mercado:
    st.markdown("## MODO MERCADO")
    if itens_marcados_nomes:
        for item in sorted(itens_marcados_nomes, key=remover_acentos):
            st.write(f"### [X] {item}")
    else:
        st.info("Nenhum item selecionado.")
else:
    col1, col2, col3 = st.columns(3)
    categorias_validas = [(k, v) for k, v in st.session_state.categorias.items() if v or k == "OUTROS"]
    
    for i, (cat_nome, produtos) in enumerate(categorias_validas):
        col_atual = [col1, col2, col3][i % 3]
        with col_atual:
            st.subheader(str(cat_nome))
            for p in produtos:
                c1, c2, c3 = st.columns([2, 0.8, 1])
                with c1:
                    marcado = st.checkbox(p, key=f"check_{p}_{cat_nome}")
                if marcado:
                    with c2:
                        q = st.number_input("Q", 1, 100, 1, key=f"q_{p}_{cat_nome}", label_visibility="collapsed")
                    with c3:
                        pr = st.number_input("R", 0.0, 1000.0, 0.0, 0.5, key=f"p_{p}_{cat_nome}", label_visibility="collapsed")
                    total_estimado += (q * pr)

with st.sidebar:
    st.divider()
    st.metric("💰 TOTAL ESTIMADO", f"R$ {total_estimado:.2f}")
    if itens_marcados_nomes:
        url_wa = app.gerar_whatsapp_texto(itens_marcados_nomes, motivo_input)
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:8px;text-align:center;font-weight:bold;margin-bottom:10px;">📲 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
        img_bytes = app.gerar_imagem(sorted(list(set(itens_marcados_nomes)), key=remover_acentos), motivo_input)
        st.download_button("🖼️ BAIXAR IMAGEM", img_bytes, "lista_compras.png", "image/png", use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:grey;'>2026 Lista de Compras | by ®rvrs</p>", unsafe_allow_html=True)
