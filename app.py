# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import urllib.parse
import unicodedata
import io
from PIL import Image, ImageDraw

# Função essencial para a imagem não sair com códigos estranhos
def limpar_texto(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').upper()

# 1. Configuração da Página (Título que aparece no navegador)
st.set_page_config(page_title="Lista rvrs", layout="wide")

# 2. Inicialização dos Dados (Só acontece uma vez)
if 'categorias' not in st.session_state:
    raw_data = {
        "MERCEARIA": ["AÇÚCAR", "AMENDOIM", "ARROZ", "AZEITE", "AZEITONA", "BATATA FRITA", "BISCOITOS", "BOLACHAS", "CAFÉ", "CALDO GALINHA", "CHÁ", "COCO RALADO", "CREME DE LEITE", "ERVILHA", "ESSÊNCIA", "EXTRATO TOMATE", "FARINHA DE MILHO", "FARINHA DE TRIGO", "FARINHA MANDIOCA", "FARINHA ROSCA", "FARINHA TEMPERADA", "FEIJÃO", "FERMENTO", "FILTRO CAFÉ", "FLOCÃO DE MILHO", "FÓSFORO", "FUBÁ", "GELATINA", "KETCHUP", "LASANHA", "LEITE", "LEITE CONDENSADO", "LEITE DE COCO", "LENTILHA", "MACARRÃO", "MAIONESE", "MAISENA", "MASSA PIZZA", "MILHO VERDE", "MISTURA P/ BOLO", "MOLHO INGLÊS", "MOLHO TOMATE", "MOSTARDA", "ÓLEO", "OVOS", "PALMITO", "PÓ ROYAL", "TAPIOCA", "TEMPERO", "TODDY"],
        "LIMPEZA": ["ÁGUA SANITÁRIA", "ÁLCOOL", "AMACIANTE", "BICARBONATO", "BOMBRIL", "BUCHA BANHO", "BUCHA COZINHA", "CÊRA", "DESINFETANTE", "DETERGENTE", "LÂMPADA", "LISOFORME", "LUSTRA MÓVEIS", "PAPEL ALUMÍNIO", "PASTA PINHO", "PEDRA SANITÁRIA", "PEROBA", "RODO", "SABÃO BARRA", "SABÃO EM PÓ", "SACO DE LIXO", "VASSOURA", "VEJA", "VELA"],
        "HIGIENE": ["ACETONA", "ALGODÃO", "CONDICIONADOR", "DESODORANTE", "ESCOVA DE DENTE", "FIO DENTAL", "GUARDANAPO", "PAPEL HIGIÊNICO", "PASTA DE DENTE", "PRESTO-BARBA", "SABONETE", "SABONETE LÍQUIDO", "SHAMPOO"],
        "FRIOS": ["CHEDDAR", "EMPANADO", "GORGONZOLA", "HAMBURGUER", "IOGURTE", "MANTEIGA", "MARGARINA", "MORTADELA", "MUSSARELA", "PASTEL (MASSA)", "PRESUNTO", "QUEIJO", "REQUEIJÃO", "SALSICHA"],
        "FRUTAS / VERDURAS": ["ABÓBORA", "ALFACE", "ALHO", "BANANA", "BATATA", "BETERRABA", "CEBOLA", "CENOURA", "CHUCHU", "LARANJA", "LIMÃO", "MAÇÃ", "MAMÃO", "MELANCIA", "MELÃO", "PÊRA", "TOMATE"],
        "AÇOUGUE": ["ALCATRA", "ASINHA", "BACON", "BIFE", "CALABRESA", "CARNE MOÍDA", "COSTELÃO", "COSTELINHA", "COXINHA", "CUPIM", "FÍGADO", "FILÉ", "FILÉ DE PEITO", "FRALDINHA", "FRANGO", "LÍNGUA", "LINGUIÇA", "LOMBO", "MÚSCULO", "PICANHA"],
        "TEMPEROS": ["AÇÚCAR MASCAVO", "ALHO EM PÓ", "CEBOLA EM PÓ", "ORÉGANO", "PÁPRICA DEFUMADA", "PÁPRICA PICANTE", "PIMENTA DO REINO"],
        "BEBIDAS": ["ÁGUA MINERAL", "CERVEJA", "ENERGÉTICO", "REFRIGERANTE", "SUCO", "VINHO"],
        "OUTROS": []
    }
    st.session_state.categorias = {k: sorted(v, key=limpar_texto) for k, v in raw_data.items()}

# 3. Título Principal
st.markdown("<h1 style='text-align:center;'>🛒 MINHA LISTA</h1><hr>", unsafe_allow_html=True)

# 4. Barra Lateral (Sidebar)
with st.sidebar:
    st.header("CONFIGURAÇÕES")
    
    # Campo do Motivo (Simples, sem chaves dinâmicas para evitar erro)
    motivo = st.text_input("📍 Motivo/Local:", placeholder="Ex: Churrasco")
    
    if st.button("🗑️ LIMPAR TUDO"):
        for key in st.session_state.keys():
            if key.startswith("check_"):
                st.session_state[key] = False
        st.rerun()
    
    st.divider()
    
    # Adicionar item novo
    novo_item = st.text_input("➕ Novo Item:")
    if st.button("ADICIONAR"):
        if novo_item:
            st.session_state.categorias["OUTROS"].append(novo_item.upper())
            st.session_state.categorias["OUTROS"].sort(key=limpar_texto)
            st.rerun()

# 5. Organização da Lista na Tela
col1, col2, col3 = st.columns(3)
selecionados = []

for i, (cat, itens) in enumerate(st.session_state.categorias.items()):
    with [col1, col2, col3][i % 3]:
        st.markdown(f"### {cat}")
        for item in itens:
            # Se marcado, adiciona à lista final
            if st.checkbox(item, key=f"check_{item}_{cat}"):
                selecionados.append(item)

# 6. Ações Finais (WhatsApp e Imagem)
if selecionados:
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        # Gerar Link WhatsApp
        data_atual = datetime.now().strftime("%d/%m/%Y")
        msg = f"*--- LISTA ({data_atual}) ---*\n"
        if motivo: msg += f"*MOTIVO:* {motivo.upper()}\n"
        msg += "\n".join([f"[X] {i}" for i in selecionados])
        url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        st.markdown(f'''<a href="{url}" target="_blank"><button style="width:100%; height:50px; background-color:#25D366; color:white; border:none; border-radius:10px; font-weight:bold;">📲 ENVIAR WHATSAPP</button></a>''', unsafe_allow_html=True)

    with c2:
        # Gerar Imagem (Lógica Simplificada)
        largura = 500
        altura = 150 + (len(selecionados) * 30)
        img = Image.new('RGB', (largura, altura), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # Cabeçalho da Imagem
        d.text((20, 20), f"LISTA DE COMPRAS - {datetime.now().strftime('%d/%m/%Y')}", fill=(0, 0, 0))
        if motivo:
            d.text((20, 50), f"MOTIVO: {limpar_texto(motivo)}", fill=(0, 51, 153))
        
        d.line((20, 80, 480, 80), fill=(0, 0, 0), width=2)
        
        y = 100
        for item in selecionados:
            d.text((30, y), f"[X] {limpar_texto(item)}", fill=(0, 0, 0))
            y += 30
            
        # Converter imagem para botão de download
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        st.download_button("🖼️ BAIXAR IMAGEM", buf.getvalue(), "lista.png", "image/png", use_container_width=True)

st.markdown("<br><br><center><small>Desenvolvido por ®rvrs</small></center>", unsafe_allow_html=True)
