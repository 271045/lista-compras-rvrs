# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
from datetime import datetime
import urllib.parse
import unicodedata
import io
import re
from PIL import Image, ImageDraw, ImageFont

# 1. Configuração da Página
st.set_page_config(page_title="🛒 Lista Pro Nuvem ®rvrs", layout="wide", initial_sidebar_state="expanded")

# 2. Conexão com Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro nos Secrets! Verifique a chave privada.")

def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn')

# 3. Inicialização de Dados
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

if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0

# 4. Funções de Apoio
def limpar_tela():
    for k in list(st.session_state.keys()):
        if k.startswith("check_"): st.session_state[k] = False
    st.session_state.reset_trigger += 1
    st.rerun()

def gerar_imagem_lista(itens, motivo_txt):
    largura = 550
    espaco = 35
    altura = 150 + (len(itens) * espaco) + 100
    img = Image.new('RGB', (largura, altura), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        f_bold = ImageFont.load_default(size=22)
        f_norm = ImageFont.load_default(size=18)
    except:
        f_bold = f_norm = ImageFont.load_default()
    d.text((30, 30), "LISTA DE COMPRAS", fill=(0,0,0), font=f_bold)
    d.text((30, 60), f"DATA: {datetime.now().strftime('%d/%m/%Y')}", fill=(100,100,100), font=f_norm)
    if motivo_txt:
        d.text((30, 90), f"MOTIVO: {motivo_txt.upper()}", fill=(0,51,153), font=f_bold)
    y = 130
    for it in itens:
        d.text((40, y), f"[X] {it}", fill=(0,0,0), font=f_norm)
        y += espaco
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

# --- INTERFACE ---
st.markdown("<h1 style='text-align:center;'>🛒 Lista de Compras Nuvem ®rvrs</h1>", unsafe_allow_html=True)

# 5. SIDEBAR (Configurações e Nuvem)
with st.sidebar:
    st.header("💾 NUVEM & OPÇÕES")
    motivo_input = st.text_input("Motivo da Compra:", placeholder="Ex: Churrasco", key=f"mot_{st.session_state.reset_trigger}")
    modo_mercado = st.toggle("🛒 MODO MERCADO")
    
    if st.button("🗑️ LIMPAR TELA", use_container_width=True): limpar_tela()
    
    st.divider()
    # SALVAR
    if st.button("📥 SALVAR NO GOOGLE", use_container_width=True):
        sel = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]
        if motivo_input and sel:
            df_old = conn.read(ttl=0)
            novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": motivo_input.upper(), "itens_json": json.dumps(sel, ensure_ascii=False)}])
            df_new = pd.concat([df_old, novo], ignore_index=True)
            conn.update(data=df_new)
            st.success("Salvo na Planilha!")
        else: st.warning("Dê um nome e marque itens!")

    # CARREGAR
    try:
        df_nuvem = conn.read(ttl=0)
        if not df_nuvem.empty:
            lista_nomes = ["Selecionar..."] + list(df_nuvem['nome_lista'].unique())
            escolha = st.selectbox("Abrir lista antiga:", lista_nomes)
            if escolha != "Selecionar..." and st.button("📂 CARREGAR ESTA"):
                dados = json.loads(df_nuvem[df_nuvem['nome_lista'] == escolha].iloc[-1]['itens_json'])
                for k in st.session_state.keys():
                    if k.startswith("check_"): st.session_state[k] = False
                for item in dados:
                    for cat in st.session_state.categorias.keys():
                        if f"check_{item}_{cat}" in st.session_state: st.session_state[f"check_{item}_{cat}"] = True
                st.rerun()
    except: pass

# 6. EXIBIÇÃO PRINCIPAL
itens_selecionados = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]

if modo_mercado:
    st.markdown(f"### 🛒 Carrinho: {len(itens_selecionados)} itens")
    if itens_selecionados:
        for item in sorted(itens_selecionados):
            st.markdown(f"✅ **{item}**")
    else: st.info("Selecione itens no modo normal primeiro.")
else:
    col1, col2, col3 = st.columns(3)
    for i, (cat, prods) in enumerate(st.session_state.categorias.items()):
        with [col1, col2, col3][i % 3]:
            st.subheader(cat)
            for p in prods:
                st.checkbox(p, key=f"check_{p}_{cat}")

# 7. EXPORTAÇÃO
if itens_selecionados:
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        img_b = gerar_imagem_lista(sorted(itens_selecionados), motivo_input)
        st.download_button("🖼️ BAIXAR IMAGEM", img_b, "lista.png", use_container_width=True)
    with c2:
        msg = f"*LISTA DE COMPRAS ({motivo_input})*\n" + "\n".join([f"[X] {i}" for i in sorted(itens_selecionados)])
        url_wa = f"https://wa.me/?text={urllib.parse.quote(msg + '\n\n_by ®rvrs_')}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;">📲 WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center;'>2026 | Oliveira-MG | by ®rvrs</p>", unsafe_allow_html=True)
