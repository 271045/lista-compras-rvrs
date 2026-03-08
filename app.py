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
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro nos Secrets! Verifique a chave do Google: {e}")

def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).upper().strip())
                  if unicodedata.category(c) != 'Mn')

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
    st.session_state.categorias = {k: sorted(v, key=remover_acentos) for k, v in raw_data.items()}

# 4. Função para Gerar Imagem (Restaurada)
def gerar_imagem(lista_itens, motivo_str):
    largura = 500
    altura = 180 + (len(lista_itens) * 35)
    img = Image.new('RGB', (largura, altura), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        f_bold = ImageFont.load_default()
    except:
        f_bold = None
    draw.text((30, 30), "🛒 LISTA DE COMPRAS", fill=(0,0,0))
    draw.text((30, 60), f"DATA: {datetime.now().strftime('%d/%m/%Y')}", fill=(100,100,100))
    if motivo_str:
        draw.text((30, 90), f"MOTIVO: {motivo_str.upper()}", fill=(0,51,153))
    y_pos = 135
    for item in lista_itens:
        draw.text((40, y_pos), f"[X] {item}", fill=(0,0,0))
        y_pos += 35
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("💾 NUVEM & OPÇÕES")
    nome_salvar = st.text_input("Nome da Lista:", placeholder="Ex: Mensal", key="motivo_input")
    modo_mercado = st.toggle("🛒 MODO MERCADO")
    
    # Botão Salvar
    if st.button("📥 SALVAR NO GOOGLE", use_container_width=True):
        if conn:
            marcados = [k.split("check_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]
            if nome_salvar and marcados:
                try:
                    df_nuvem = conn.read(ttl=0)
                    nova_lista = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "nome_lista": nome_salvar.upper(), "itens_json": json.dumps(marcados, ensure_ascii=False)}])
                    conn.update(data=pd.concat([df_nuvem, nova_lista], ignore_index=True))
                    st.success("Lista salva!")
                except Exception as e:
                    st.error(f"Erro na planilha: {e}")
            else: st.warning("Dê um nome e marque itens.")
        else:
            st.error("Sem conexão com Google Sheets.")

    # Botão Carregar
    if conn:
        try:
            df_lido = conn.read(ttl=0)
            if not df_lido.empty:
                st.divider()
                escolha = st.selectbox("📂 Abrir Lista Salva:", ["Selecionar..."] + list(df_lido['nome_lista'].unique()))
                if escolha != "Selecionar..." and st.button("ABRIR ESTA LISTA"):
                    dados = json.loads(df_lido[df_lido['nome_lista'] == escolha].iloc[-1]['itens_json'])
                    for k in list(st.session_state.keys()):
                        if k.startswith("check_"): st.session_state[k] = False
                    for it in dados:
                        st.session_state[f"check_{it}"] = True
                    st.rerun()
        except:
            pass

# --- ÁREA PRINCIPAL ---
st.markdown("<h1 style='text-align:center;'>🛒 Lista de Compras ®rvrs</h1>", unsafe_allow_html=True)
selecionados = [k.split("check_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]

if modo_mercado:
    st.subheader(f"🛒 Carrinho ({len(selecionados)} itens)")
    for s in sorted(selecionados):
        st.markdown(f"✅ **{s}**")
else:
    col1, col2, col3 = st.columns(3)
    for i, (cat, prods) in enumerate(st.session_state.categorias.items()):
        with [col1, col2, col3][i % 3]:
            st.subheader(cat)
            for p in prods:
                st.checkbox(p, key=f"check_{p}")

# --- BOTÕES DE WHATSAPP E IMAGEM (Restaurados) ---
if selecionados:
    st.divider()
    col_img, col_wa = st.columns(2)
    
    with col_img:
        img_bytes = gerar_imagem(sorted(selecionados), nome_salvar)
        st.download_button("🖼️ BAIXAR IMAGEM", img_bytes, "lista.png", use_container_width=True)
        
    with col_wa:
        msg_wa = f"*LISTA DE COMPRAS*\n*Motivo:* {nome_salvar.upper() if nome_salvar else 'Geral'}\n\n" + "\n".join([f"- {it}" for it in sorted(selecionados)])
        url_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa + '\n\n_by ®rvrs_')}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;font-size:18px;">📲 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<br><hr><p style='text-align:center;'>2026 | Oliveira-MG | by ®rvrs</p>", unsafe_allow_html=True)
