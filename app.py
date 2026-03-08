# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import json
from datetime import datetime
import urllib.parse
import unicodedata
import io
import re

# 1. Configuração da Página
st.set_page_config(page_title="🛒Lista Compras ®rvrs", layout="wide", initial_sidebar_state="collapsed")

# 2. Conexão com Google Sheets
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")

def normalizar_texto(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).lower().strip()) if unicodedata.category(c) != 'Mn')

# 3. Categorias e Itens
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
    st.session_state.categorias = {k: sorted(v, key=normalizar_texto) for k, v in raw_data.items()}

if 'selecionados' not in st.session_state: st.session_state.selecionados = {}
if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0

# Interface Principal
st.markdown("<h1 style='text-align:center; border-bottom: 3px solid black;'>🛒 LISTA DE COMPRAS ®rvrs</h1>", unsafe_allow_html=True)

# Busca
busca_input = st.text_input("🔍 Pesquisar...", placeholder="O que você precisa?")
busca_termo = normalizar_texto(busca_input)

# Sidebar
with st.sidebar:
    st.header("💾 NUVEM")
    nome_lista = st.text_input("Nome da Lista:", placeholder="Ex: Mensal", key="nome_lista_input")
    
    if st.button("📥 SALVAR NO GOOGLE", use_container_width=True):
        if conn and nome_lista and st.session_state.selecionados:
            try:
                df_old = conn.read(ttl=0)
                novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": nome_lista.upper(), "itens_json": json.dumps(st.session_state.selecionados, ensure_ascii=False)}])
                conn.update(data=pd.concat([df_old, novo], ignore_index=True))
                st.success("Salvo com sucesso!")
            except Exception as e: st.error(f"Erro na planilha: {e}")
        else: st.warning("Dê um nome e marque itens.")

    if conn:
        try:
            df_lido = conn.read(ttl=0)
            if not df_lido.empty:
                st.divider()
                escolha = st.selectbox("📂 Carregar lista:", ["Selecionar..."] + list(df_lido['nome_lista'].unique()))
                if escolha != "Selecionar..." and st.button("ABRIR ESTA LISTA"):
                    st.session_state.selecionados = json.loads(df_lido[df_lido['nome_lista'] == escolha].iloc[-1]['itens_json'])
                    st.rerun()
        except: pass
    
    if st.button("🗑️ DESMARCAR TUDO", use_container_width=True):
        st.session_state.selecionados = {}
        st.session_state.reset_trigger += 1
        st.rerun()

# Exibição
col1, col2, col3 = st.columns(3)
for i, (cat, prods) in enumerate(st.session_state.categorias.items()):
    prods_f = [p for p in prods if busca_termo in normalizar_texto(p)]
    if prods_f:
        with [col1, col2, col3][i % 3]:
            st.subheader(cat)
            for p in prods_f:
                c_item, c_qtd = st.columns([3, 1])
                foi_sel = p in st.session_state.selecionados
                with c_item:
                    marcado = st.checkbox(p, value=foi_sel, key=f"chk_{p}_{st.session_state.reset_trigger}")
                if marcado:
                    with c_qtd:
                        qtd = st.number_input("Q", 1, 100, st.session_state.selecionados.get(p, {'qtd': 1})['qtd'], key=f"q_{p}", label_visibility="collapsed")
                    st.session_state.selecionados[p] = {'qtd': qtd}
                else:
                    if p in st.session_state.selecionados: del st.session_state.selecionados[p]

# WhatsApp na Sidebar
if st.session_state.selecionados:
    with st.sidebar:
        st.divider()
        msg = f"*LISTA DE COMPRAS*\n\n" + "\n".join([f"- {k} ({v['qtd']})" for k, v in st.session_state.selecionados.items()])
        url_wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;">📲 WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center;'>2026 | Oliveira-MG | by ®rvrs</p>", unsafe_allow_html=True)
