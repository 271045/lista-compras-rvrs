# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
from datetime import datetime
import urllib.parse
import unicodedata

# 1. Configuração da Página
st.set_page_config(page_title="🛒 Lista Blindada ®rvrs", layout="wide")

# 2. Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def normalizar_texto(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).lower().strip())
                  if unicodedata.category(c) != 'Mn')

# --- Lógica de Salvar na Planilha ---
def salvar_na_planilha(nome_lista, selecionados):
    # Lê os dados atuais
    df_existente = conn.read(ttl=0) # ttl=0 garante que lê o dado mais novo
    
    novo_dado = pd.DataFrame([{
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "nome_lista": nome_lista.upper(),
        "itens_json": json.dumps(selecionados, ensure_ascii=False)
    }])
    
    # Junta o novo com o antigo e salva
    df_final = pd.concat([df_existente, novo_dado], ignore_index=True)
    conn.update(data=df_final)
    st.success(f"✅ Lista '{nome_lista}' salva no Google Sheets!")

# --- Interface ---
st.title("🛒 Lista de Compras (Nuvem)")

with st.sidebar:
    st.header("💾 NUVEM GOOGLE")
    nome_da_lista = st.text_input("Nome para salvar:", placeholder="Ex: Mensal")
    
    if st.button("📥 SALVAR NA PLANILHA", use_container_width=True):
        if nome_da_lista and st.session_state.get('selecionados'):
            salvar_na_planilha(nome_da_lista, st.session_state.selecionados)
        else:
            st.warning("Selecione itens e dê um nome!")

    st.divider()
    
    # Carregar dados da planilha
    try:
        df_listas = conn.read(ttl=0)
        if not df_listas.empty:
            lista_para_abrir = st.selectbox("Carregar da Nuvem:", df_listas['nome_lista'].unique())
            if st.button("📂 ABRIR LISTA"):
                linha = df_listas[df_listas['nome_lista'] == lista_para_abrir].iloc[-1]
                st.session_state.selecionados = json.loads(linha['itens_json'])
                st.rerun()
    except:
        st.info("Planilha vazia ou não conectada.")
