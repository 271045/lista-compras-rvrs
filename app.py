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
st.set_page_config(page_title="🛒 Lista Pro ®rvrs", layout="wide")

# 2. Conexão com Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Erro na conexão com o Google Sheets nos Secrets.")

def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).lower().strip())
                  if unicodedata.category(c) != 'Mn')

# 3. Categorias e Itens (Seu Banco de Dados)
if 'categorias' not in st.session_state:
    raw_data = {
        "MERCEARIA": ["AÇÚCAR", "AMENDOIM", "ARROZ", "AZEITE", "AZEITONA", "BATATA FRITA", "BISCOITOS", "BOLACHAS", "CAFÉ", "CALDO GALINHA", "CHÁ", "COCO RALADO", "CREME DE LEITE", "ERVILHA", "ESSÊNCIA", "EXTRATO TOMATE", "FARINHA DE MILHO", "FARINHA DE TRIGO", "FARINHA MANDIOCA", "FARINHA ROSCA", "FARINHA TEMPERADA", "FEIJÃO", "FERMENTO", "FILTRO CAFÉ", "FLOCÃO DE MILHO", "FÓSFORO", "FUBÁ", "GELATINA", "KETCHUP", "LASANHA", "LEITE", "LEITE CONDENSADO", "LEITE DE COCO", "LENTILHA", "MACARRÃO", "MAIONESE", "MAISENA", "MASSA PIZZA", "MILHO VERDE", "MISTURA P/ BOLO", "MOLHO INGLÊS", "MOLHO TOMATE", "MOSTARDA", "ÓLEO", "OVOS", "PALMITO", "PÓ ROYAL", "TAPIOCA", "TEMPERO", "TODDY"],
        "LIMPEZA": ["ÁGUA SANITÁRIA", "ÁLCOOL", "AMACIANTE", "BICARBONATO", "BOMBRIL", "BUCHA BANHO", "BUCHA COZINHA", "CÊRA", "DESINFETANTE", "DETERGENTE", "LÂMPADA", "LISOFORME", "LUSTRA MÓVEIS", "PAPEL ALUMÍNIO", "PASTA PINHO", "PEDRA SANITÁRIA", "PEROBA", "RODO", "SABÃO BARRA", "SABÃO EM PÓ", "SACO DE LIXO", "VASSOURA", "VEJA", "VELA"],
        "HIGIENE": ["ACETONA", "ALGODÃO", "CONDICIONADOR", "DESODORANTE", "ESCOVA DE DENTE", "FIO DENTAL", "GUARDANAPO", "PAPEL HIGIÊNICO", "PASTA DE DENTE", "PRESTOBARBA", "SABONETE", "SABONETE LÍQUIDO", "SHAMPOO"],
        "FRIOS": ["CHEDDAR", "EMPANADO", "GORGONZOLA", "HAMBURGUER", "IOGURTE", "MANTEIGA", "MARGARINA", "MORTADELA", "MUSSARELA", "PASTEL (MASSA)", "PRESUNTO", "QUEIJO", "REQUEIJÃO", "SALSICHA"],
        "FRUTAS / VERDURAS": ["ABÓBORA", "ALFACE", "ALHO", "BANANA", "BATATA", "BETERRABA", "CEBOLA", "CENOURA", "CHUCHU", "LARANJA", "LIMÃO", "MAÇÃ", "MAMÃO", "MELANCIA", "MELÃO", "PÊRA", "TOMATE"],
        "AÇOUGUE": ["ALCATRA", "ASINHA", "BACON", "BIFE", "CALABRESA", "CARNE MOÍDA", "COSTELÃO", "COSTELINHA", "COXINHA", "CUPIM", "FÍGADO", "FILÉ", "FILÉ DE PEITO", "FRALDINHA", "FRANGO", "LINGUA", "LINGUIÇA", "LOMBO", "MÚSCULO", "PICANHA"],
        "TEMPEROS": ["AÇÚCAR MASCAVO", "ALHO EM PÓ", "CEBOLA EM PÓ", "OREGANO", "PÁPRICA DEFUMADA", "PÁPRICA PICANTE", "PIMENTA DO REINO"],
        "BEBIDAS": ["ÁGUA MINERAL", "CERVEJA", "ENERGÉTICO", "REFRIGERANTE", "SUCO", "VINHO"]
    }
    st.session_state.categorias = {k: sorted(v, key=remover_acentos) for k, v in raw_data.items()}

if 'selecionados' not in st.session_state: st.session_state.selecionados = []

# 4. Função para Imagem (Gera a foto da lista)
def gerar_foto(itens, mot):
    largura = 500
    altura = 150 + (len(itens) * 35) + 50
    img = Image.new('RGB', (largura, altura), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try: f_bold = ImageFont.load_default(size=22); f_norm = ImageFont.load_default(size=18)
    except: f_bold = f_norm = ImageFont.load_default()
    
    draw.text((30, 30), "🛒 LISTA DE COMPRAS", fill=(0,0,0), font=f_bold)
    draw.text((30, 60), f"DATA: {datetime.now().strftime('%d/%m/%Y')}", fill=(100,100,100), font=f_norm)
    if mot: draw.text((30, 90), f"MOTIVO: {mot.upper()}", fill=(0,51,153), font=f_bold)
    
    y = 130
    for it in itens:
        draw.text((40, y), f"[X] {it}", fill=(0,0,0), font=f_norm)
        y += 35
    buf = io.BytesIO(); img.save(buf, format='PNG')
    return buf.getvalue()

# --- SIDEBAR (CONFIGURAÇÕES E LISTAS SALVAS) ---
with st.sidebar:
    st.title("💾 NUVEM ®rvrs")
    motivo = st.text_input("Motivo da Compra:", placeholder="Ex: Mensal Março")
    
    # SALVAR
    if st.button("📥 SALVAR NA NUVEM", use_container_width=True):
        if motivo and st.session_state.selecionados:
            df = conn.read(ttl=0)
            nova = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": motivo.upper(), "itens_json": json.dumps(st.session_state.selecionados, ensure_ascii=False)}])
            conn.update(data=pd.concat([df, nova], ignore_index=True))
            st.success("Salvo!")
        else: st.warning("Dê um nome e marque itens.")

    # ABRIR LISTAS SALVAS
    st.divider()
    try:
        df_lido = conn.read(ttl=0)
        if not df_lido.empty:
            listas_db = ["Selecionar..."] + list(df_lido['nome_lista'].unique())
            escolha = st.selectbox("📂 Abrir Lista Antiga:", listas_db)
            if escolha != "Selecionar..." and st.button("CARREGAR LISTA"):
                itens_db = json.loads(df_lido[df_lido['nome_lista'] == escolha].iloc[-1]['itens_json'])
                st.session_state.selecionados = itens_db
                st.rerun()
    except: pass

    st.divider()
    modo_mercado = st.toggle("🛒 MODO MERCADO")
    if st.button("🗑️ LIMPAR TUDO", use_container_width=True):
        st.session_state.selecionados = []
        st.rerun()

# --- ÁREA PRINCIPAL ---
st.markdown("<h1 style='text-align:center;'>🛒 Lista de Compras</h1>", unsafe_allow_html=True)

if modo_mercado:
    st.subheader(f"🛒 Carrinho: {len(st.session_state.selecionados)} itens")
    for s in sorted(st.session_state.selecionados):
        st.markdown(f"✅ **{s}**")
else:
    col1, col2, col3 = st.columns(3)
    for i, (cat, prods) in enumerate(st.session_state.categorias.items()):
        with [col1, col2, col3][i % 3]:
            st.subheader(cat)
            for p in prods:
                checado = st.checkbox(p, value=(p in st.session_state.selecionados), key=f"ch_{p}_{cat}")
                if checado and p not in st.session_state.selecionados:
                    st.session_state.selecionados.append(p)
                elif not checado and p in st.session_state.selecionados:
                    st.session_state.selecionados.remove(p)

# --- BOTÕES DE WHATSAPP E IMAGEM (EXPORTAÇÃO) ---
if st.session_state.selecionados:
    st.divider()
    c_img, c_wa = st.columns(2)
    
    with c_img:
        img_bytes = gerar_foto(sorted(st.session_state.selecionados), motivo)
        st.download_button("🖼️ BAIXAR IMAGEM DA LISTA", img_bytes, "lista.png", use_container_width=True)
        
    with c_wa:
        txt_wa = f"*LISTA DE COMPRAS*\n*Motivo:* {motivo.upper() if motivo else 'Geral'}\n\n" + "\n".join([f"- {it}" for it in sorted(st.session_state.selecionados)])
        url_wa = f"https://wa.me/?text={urllib.parse.quote(txt_wa + '\n\n_by ®rvrs_')}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;font-size:18px;">📲 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center;color:grey;'>Oliveira-MG | ®rvrs</p>", unsafe_allow_html=True)
