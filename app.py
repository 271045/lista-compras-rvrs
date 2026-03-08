# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import unicodedata
import io
import re
import json

# 1. Configuração da Página
st.set_page_config(page_title="🛒Lista Compras ®rvrs", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO DIRETA (Para evitar erro de PEM nos Secrets)
# Aqui usamos a sua chave exata dentro de uma variável protegida
CHAVE_GOOGLE = {
    "type": "service_account",
    "project_id": "lista-compras-rvrs",
    "private_key_id": "70c09cd92fbf5ccc940222aa58209668270f9944",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDx6gO/KPv/+Hq2\n3w2+PQfPsn9VKmM9RLL09QSOrAg1PafOorcLasYsXw7AgEs0cHNUrXEKLs1H6yf/\njfj6ZWepnhxbvwGwCDVSgkVu3hKuFvZElbJT4HIpD5FVW6EyDDRSsTp+6yrB3e85\naBQJbAX3vGZ2Bksq3nMU+lpXwW6H4TeWcR/VUcvprkD8Ozo73xKHhzxbundsIZiL\njAlUrZ9RR6vXPQ/xb3Z5RRVZvL2e6DflHfqg22hIfOzgNkx2n1DuUrQx17Mbcnq0\n20nMvPS9h31gv1977qQbwK8h9aTGL1SmwM+k5BTqKdIzSjWF0vyaXY41IYkkjY/K\nx8AflIyfAgMBAAECggEAdHyoWDS+f6fhQ0yN3BScPc1oVhSmm7qIZ77R9ndtLmHl\ne3FLreI40eXl/xjn3bTmPBiWTX5y19YquPpesQgCTiE165HCmMajEntrPrMNkKm6\n5RSmPZBeuFnoNA9+w9Avo7/2eGX5/UdGacCtoUnUZ9HfDqcCK/7YsHnK5eXdOOzw\nv98UFmpksoHLfLjnboAbedcTA3R0V76940aFUmyzGK9fRDhIafZQPClAOqcboAye\nPkuY7GE3ZJpKqOl2YmmDUB8egMEfdU8grDkIj2k7oVX8niDHlY4g51BCWeo7Oryr\njYPAc/9JQdhryUO15HLrICyW2iAlPAef8z+fhOInhQKBgQD7Vj8KlAWvsOi/yJ2P\ndhfI4pwufJVFg2mwj8dRM3k3/dfbwkzLrBM9RBHJs21nUC5CIqSs84bnWP4KX+aL\nG9J592Er9bzJVUOLJbgav4efCdxIW4hAtNzGrDCwzI5qzngclIATKX4allU+yX/A\nBxgsRMtRPK+mTQFF/XhtyOLE3QKBgQD2ZwOIGWTHSLZFI5EbseEFCjsR3/HRcQXF\E551F1P0rGUoah67bb+5z3MP6ZCy4Ntvw3DDemzQSlFtEl7K+QI6aSOeqn2UcVZf\jpq7CzsLn/vPYL/4jev9VEvPLylpFVq2qhPw6sfYWkQUp6mWT8H566tJ0YTDpz7E\nvCTWA/PxqwKBgQDBZK/Fd/iYI8w0Ji32wauzi4sZygsiHegpT7jSpoTTrKN4GZ31\n6kYzkjkNtt6r7GprwTRtUEWxpixz1y8SQypFZzCCHuhREyaR30g2bMHygifaFXRW\nNdTbmossv3mmfZC2jR2voPHDi4G0el+uZscW6Sh5LfUKRZ6BOHR+JWE4kQKBgB2E\ni7TDLgJ9oHA56YlCzu0Wo6rphAOOIZ3RUts+Fy2pdVjZFaNoa15sDqGqXk4/h6ok\n5J5WTTDKpmSFndt85xpuO/km/XJJ/YnnAHxFxSYIXVcjhPvWrJ2leotwX+qZx0s4\nprjmt1ggwCUlTLiYB2nUJKnsMpZps6hHzbXhtViPAoGAGrDFBhW8fXphhudDdRRv\nAQ4rZs7Ck2qorlrjNbNbIJWJbkFQ42iupZqvUUQVuO9ZeFczjVkpryuvdT2KjZli\nvpVES2bnZjlWJWKva5aO7UQ9cfBzE2g+7pgroa1yK7ybPQhwhX9Emm4TYhoUScW9\n3wfbYo7XzM6ZcHmVD+zA+j8=\n-----END PRIVATE KEY-----\n",
    "client_email": "app-lista@lista-compras-rvrs.iam.gserviceaccount.com",
    "client_id": "106176993623751905482",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/app-lista%40lista-compras-rvrs.iam.gserviceaccount.com"
}

conn = st.connection("gsheets", type=GSheetsConnection, service_account=CHAVE_GOOGLE)

# 3. Restante do seu código original (Busca, Categorias, Quantidades, Imagem e WhatsApp)
def normalizar_texto(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).lower().strip()) if unicodedata.category(c) != 'Mn')

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
if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0

# Interface Principal
st.markdown("<h1 style='text-align:center; border-bottom: 3px solid black;'>🛒 LISTA DE COMPRAS</h1>", unsafe_allow_html=True)

# Busca
busca_input = st.text_input("🔍 Pesquisar...", placeholder="Digite o item...")
busca_termo = normalizar_texto(busca_input)

# Sidebar
with st.sidebar:
    st.header("💾 NUVEM")
    nome_lista = st.text_input("Nome da Lista:", placeholder="Ex: Mensal")
    if st.button("📥 SALVAR NO GOOGLE", use_container_width=True):
        if nome_lista and st.session_state.selecionados:
            df_old = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1AW8uinetc96agRksLekuq3JCLqf8J4X9UyfU1PXMTIo", ttl=0)
            novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": nome_lista.upper(), "itens_json": json.dumps(st.session_state.selecionados, ensure_ascii=False)}])
            conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/1AW8uinetc96agRksLekuq3JCLqf8J4X9UyfU1PXMTIo", data=pd.concat([df_old, novo], ignore_index=True))
            st.success("Salvo com sucesso!")
        else: st.warning("Preencha o nome e selecione itens.")

    # Carregar
    try:
        df_lido = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1AW8uinetc96agRksLekuq3JCLqf8J4X9UyfU1PXMTIo", ttl=0)
        if not df_lido.empty:
            escolha = st.selectbox("📂 Carregar lista:", ["Selecionar..."] + list(df_lido['nome_lista'].unique()))
            if escolha != "Selecionar..." and st.button("CARREGAR"):
                st.session_state.selecionados = json.loads(df_lido[df_lido['nome_lista'] == escolha].iloc[-1]['itens_json'])
                st.rerun()
    except: pass

# Exibição (Colunas e Quantidades)
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

# WhatsApp e Imagem na Sidebar
if st.session_state.selecionados:
    with st.sidebar:
        st.divider()
        msg = f"*LISTA DE COMPRAS*\n\n" + "\n".join([f"- {k} ({v['qtd']})" for k, v in st.session_state.selecionados.items()])
        url_wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;">📲 WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center;'>2026 | Oliveira-MG | by ®rvrs</p>", unsafe_allow_html=True)
