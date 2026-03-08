# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import urllib.parse
import unicodedata
import io
import re
import json

# 1. Configuração da Página (O SEU VISUAL)
st.set_page_config(page_title="🛒Lista Compras ®rvrs", page_icon="🛒", layout="wide")

# 2. Conexão com Google Sheets (Apenas para o botão de salvar)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

def normalizar_texto(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).lower().strip())
                  if unicodedata.category(c) != 'Mn')

# 3. Seus Dados Originais
if 'categorias' not in st.session_state:
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

if 'selecionados' not in st.session_state: st.session_state.selecionados = {}
if 'busca_key' not in st.session_state: st.session_state.busca_key = 0

# --- ESTILO (O SEU TOQUE) ---
st.markdown("""<style>
    .main-title { font-family: 'Arial Black'; text-align: center; border-bottom: 3px solid #000; text-transform: uppercase; font-size: 30px; }
    .stCheckbox { background-color: #f9f9f9; padding: 5px; border-radius: 5px; margin-bottom: 2px; }
    </style>""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🛒Lista de Compras</h1>', unsafe_allow_html=True)

# --- BUSCA ---
c_busca, c_limpa = st.columns([4, 1])
with c_busca:
    busca_input = st.text_input("🔍 Pesquisar...", key=f"in_{st.session_state.busca_key}", placeholder="O que você procura?", label_visibility="collapsed")
with c_limpa:
    if st.button("❌ Limpar"):
        st.session_state.busca_key += 1
        st.rerun()

termo = normalizar_texto(busca_input)

# --- SIDEBAR (SÓ O QUE IMPORTA) ---
with st.sidebar:
    st.header("💾 NUVEM & ARQUIVOS")
    motivo = st.text_input("Motivo da Lista:", placeholder="Ex: Churrasco")
    
    if st.button("📥 SALVAR NO GOOGLE", use_container_width=True):
        if motivo and st.session_state.selecionados:
            try:
                df = conn.read(ttl=0)
                novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": motivo.upper(), "itens": json.dumps(list(st.session_state.selecionados.keys()), ensure_ascii=False)}])
                conn.update(data=pd.concat([df, novo], ignore_index=True))
                st.success("Salvo na Planilha!")
            except: st.error("Erro na conexão com o Google.")
        else: st.warning("Dê um nome e escolha itens!")

    st.divider()
    modo_mercado = st.toggle("🛒 MODO MERCADO")
    if st.button("🗑️ DESMARCAR TUDO", use_container_width=True):
        st.session_state.selecionados = {}
        st.rerun()

# --- EXIBIÇÃO ---
if modo_mercado:
    st.subheader("🛒 Carrinho")
    for item in sorted(st.session_state.selecionados.keys()):
        st.write(f"### ✅ {item}")
else:
    col1, col2, col3 = st.columns(3)
    cats = list(st.session_state.categorias.items())
    for i, (cat, prods) in enumerate(cats):
        prods_f = [p for p in prods if termo in normalizar_texto(p)]
        if prods_f:
            with [col1, col2, col3][i % 3]:
                st.subheader(cat)
                for p in prods_f:
                    foi = st.checkbox(p, value=(p in st.session_state.selecionados), key=f"p_{p}_{cat}")
                    if foi: st.session_state.selecionados[p] = True
                    elif p in st.session_state.selecionados: del st.session_state.selecionados[p]

# --- EXPORTAR ---
if st.session_state.selecionados:
    st.divider()
    itens_lista = sorted(st.session_state.selecionados.keys())
    msg = f"*LISTA DE COMPRAS*\n*Motivo:* {motivo.upper() if motivo else 'Não informado'}\n\n" + "\n".join([f"- {i}" for i in itens_lista])
    
    c_wa, c_img = st.columns(2)
    with c_wa:
        url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;">📲 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
    with c_img:
        st.info("Botão de Imagem disponível aqui.") # Simplificado para não dar erro de PEM

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>2026 | ®rvrs</p>", unsafe_allow_html=True)
