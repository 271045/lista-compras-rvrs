# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
from datetime import datetime
import urllib.parse
import unicodedata
import io
from PIL import Image, ImageDraw, ImageFont

# 1. Configuração da Página
st.set_page_config(page_title="🛒 Lista Pro Nuvem ®rvrs", layout="wide", initial_sidebar_state="expanded")

# 2. Conexão com Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Erro de conexão. Verifique os Secrets no Streamlit Cloud.")

def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn')

# 3. Categorias e Itens
if 'categorias' not in st.session_state:
    raw_data = {
        "MERCEARIA": ["AÇÚCAR", "AMENDOIM", "ARROZ", "AZEITE", "AZEITONA", "BATATA FRITA", "BISCOITOS", "BOLACHAS", "CAFÉ", "CALDO GALINHA", "CHÁ", "COCO RALADO", "CREME DE LEITE", "ERVILHA", "ESSÊNCIA", "EXTRATO TOMATE", "FARINHA DE MILHO", "FARINHA DE TRIGO", "FARINHA MANDIOCA", "FARINHA ROSCA", "FARINHA TEMPERADA", "FEIJÃO", "FERMENTO", "FILTRO CAFÉ", "FLOCÃO DE MILHO", "FÓSFORO", "FUBÁ", "GELATINA", "KETCHUP", "LASANHA", "LEITE", "LEITE CONDENSADO", "LEITE DE COCO", "LENTILHA", "MACARRÃO", "MAIONESE", "MAISENA", "MASSA PIZZA", "MILHO VERDE", "MISTURA P/ BOLO", "MOLHO INGLÊS", "MOLHO TOMATE", "MOSTARDA", "ÓLEO", "OVOS", "PALMITO", "PÓ ROYAL", "TAPIOCA", "TEMPERO", "TODDY"],
        "LIMPEZA": ["ÁGUA SANITÁRIA", "ÁLCOOL", "AMACIANTE", "BICARBONATO", "BOMBRIL", "BUCHA BANHO", "BUCHA COZINHA", "CÊRA", "DESINFETANTE", "DETERGENTE", "LÂMPADA", "LISOFORME", "LUSTRA MÓVEIS", "PAPEL ALUMÍNIO", "PASTA PINHO", "PEDRA SANITÁRIA", "PEROBA", "RODO", "SABÃO BARRA", "SABÃO EM PÓ", "SACO DE LIXO", "VASSOURA", "VEJA", "VELA"],
        "HIGIENE": ["ACETONA", "ALGODÃO", "CONDICIONADOR", "DESODORANTE", "ESCOVA DE DENTE", "FIO DENTAL", "GUARDANAPO", "PAPEL HIGIÊNICO", "PASTA DE DENTE", "PRESTO-BARBA", "SABONETE", "SABONETE LÍQUIDO", "SHAMPOO"],
        "FRIOS": ["CHEDDAR", "EMPANADO", "GORGONZOLA", "HAMBURGUER", "IOGURTE", "MANTEIGA", "MARGARINA", "MORTADELA", "MUSSARELA", "PASTEL (MASSA)", "PRESUNTO", "QUEIJO", "REQUEIJÃO", "SALSICHA"],
        "FRUTAS / VERDURAS": ["ABÓBORA", "ALFACE", "ALHO", "BANANA", "BATATA", "BETERRABA", "CEBOLA", "CENOURA", "CHUCHU", "LARANJA", "LIMÃO", "MAÇÃ", "MAMÃO", "MELANCIA", "MELÃO", "PÊRA", "TOMATE"],
        "AÇOUGUE": ["ALCATRA", "ASINHA", "BACON", "BIFE", "CALABRESA", "CARNE MOÍDA", "COSTELÃO", "COSTELINHA", "COXINHA", "CUPIM", "FÍGADO", "FILÉ", "FILÉ DE PEITO", "FRALDINHA", "FRANGO", "LINGUA", "LINGUIÇA", "LOMBO", "MÚSCULO", "PICANHA"],
        "TEMPEROS": ["AÇÚCAR MASCAVO", "ALHO EM PÓ", "CEBOLA EM PÓ", "OREGANO", "PÁPRICA DEFUMADA", "PÁPRICA PICANTE", "PIMENTA DO REINO"],
        "BEBIDAS": ["ÁGUA MINERAL", "CERVEJA", "ENERGÉTICO", "REFRIGERANTE", "SUCO", "VINHO"]
    }
    st.session_state.categorias = {k: sorted(v, key=remover_acentos) for k, v in raw_data.items()}

if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0

# 4. Funções de Imagem e Limpeza
def limpar_tudo():
    for k in list(st.session_state.keys()):
        if k.startswith("check_"): st.session_state[k] = False
    st.session_state.reset_trigger += 1
    st.rerun()

def criar_imagem(lista_itens, motivo_str):
    largura = 500
    altura = 180 + (len(lista_itens) * 35) + 60
    img = Image.new('RGB', (largura, altura), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        f_titulo = ImageFont.load_default(size=24)
        f_texto = ImageFont.load_default(size=18)
    except:
        f_titulo = f_texto = ImageFont.load_default()
    
    draw.text((30, 30), "🛒 LISTA DE COMPRAS", fill=(0,0,0), font=f_titulo)
    draw.text((30, 65), f"DATA: {datetime.now().strftime('%d/%m/%Y')}", fill=(80,80,80), font=f_texto)
    if motivo_str:
        draw.text((30, 95), f"MOTIVO: {motivo_str.upper()}", fill=(0,51,153), font=f_titulo)
    
    y_pos = 145
    for item in lista_itens:
        draw.text((40, y_pos), f"[X] {item}", fill=(0,0,0), font=f_texto)
        y_pos += 35
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

# --- INTERFACE PRINCIPAL ---
st.title("🛒 Lista de Compras ®rvrs")

# 5. Barra Lateral (Sidebar) - SALVAR E CARREGAR
with st.sidebar:
    st.header("💾 NUVEM & OPÇÕES")
    motivo_compra = st.text_input("Motivo da Compra:", placeholder="Ex: Churrasco", key=f"mot_{st.session_state.reset_trigger}")
    modo_mercado = st.toggle("🛒 MODO MERCADO")
    
    if st.button("🗑️ LIMPAR TELA", use_container_width=True): limpar_tudo()
    
    st.divider()
    
    # Salvar na Planilha
    if st.button("📥 SALVAR NO GOOGLE", use_container_width=True):
        marcados = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]
        if motivo_compra and marcados:
            df_atual = conn.read(ttl=0)
            nova_linha = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": motivo_compra.upper(), "itens_json": json.dumps(marcados)}])
            df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            conn.update(data=df_final)
            st.success("Salvo com sucesso!")
        else: st.warning("Defina o motivo e escolha itens.")

    # Abrir Listas Salvas
    try:
        df_lido = conn.read(ttl=0)
        if not df_lido.empty:
            opcoes = ["Selecionar..."] + list(df_lido['nome_lista'].unique())
            escolha = st.selectbox("Abrir Lista Antiga:", opcoes)
            if escolha != "Selecionar..." and st.button("📂 CARREGAR"):
                itens_recuperados = json.loads(df_lido[df_lido['nome_lista'] == escolha].iloc[-1]['itens_json'])
                for k in st.session_state.keys():
                    if k.startswith("check_"): st.session_state[k] = False
                for it in itens_recuperados:
                    for cat in st.session_state.categorias.keys():
                        if f"check_{it}_{cat}" in st.session_state: st.session_state[f"check_{it}_{cat}"] = True
                st.rerun()
    except: pass

# 6. Exibição da Grade de Produtos
selecionados = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]

if modo_mercado:
    st.subheader(f"🛒 Itens Selecionados ({len(selecionados)})")
    if selecionados:
        for s in sorted(selecionados):
            st.markdown(f"✅ **{s}**")
    else: st.info("Marque itens na tela normal primeiro.")
else:
    c1, c2, c3 = st.columns(3)
    for i, (cat, prods) in enumerate(st.session_state.categorias.items()):
        with [c1, c2, c3][i % 3]:
            st.subheader(cat)
            for p in prods:
                st.checkbox(p, key=f"check_{p}_{cat}")

# 7. Botões de Enviar (WhatsApp e Imagem)
if selecionados:
    st.divider()
    col_img, col_wa = st.columns(2)
    
    with col_img:
        img_data = criar_imagem(sorted(selecionados), motivo_compra)
        st.download_button("🖼️ BAIXAR IMAGEM DA LISTA", img_data, "lista_compras.png", use_container_width=True)
        
    with col_wa:
        msg_texto = f"*LISTA DE COMPRAS ({motivo_compra})*\n*Data: {datetime.now().strftime('%d/%m/%Y')}*\n\n" + "\n".join([f"- {i}" for i in sorted(selecionados)])
        wa_url = f"https://wa.me/?text={urllib.parse.quote(msg_texto)}"
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;font-size:18px;">📲 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<br><hr><p style='text-align:center;'>2026 | Oliveira-MG | ®rvrs</p>", unsafe_allow_html=True)
