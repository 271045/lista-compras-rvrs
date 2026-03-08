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
st.set_page_config(page_title="🛒 Lista Pro Nuvem ®rvrs", layout="wide", initial_sidebar_state="collapsed")

# 2. Conexão com Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro na conexão! Verifique se configurou os 'Secrets' no Streamlit Cloud.")

def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn')

class ListaComprasPro:
    def __init__(self):
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

    def limpar_tudo(self):
        for chave in list(st.session_state.keys()):
            if chave.startswith("check_"): st.session_state[chave] = False
        st.session_state.reset_trigger += 1
        st.rerun()

    def gerar_imagem(self, itens, motivo):
        largura = 550
        espaco_item = 35
        y_cabecalho = 150 if motivo else 100
        altura_total = y_cabecalho + (len(itens) * espaco_item) + 80
        img = Image.new('RGB', (largura, altura_total), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f_bold = ImageFont.truetype(font_path, 22)
            f_norm = ImageFont.truetype(font_path, 18)
        except:
            f_bold = f_norm = ImageFont.load_default()
        data_br = datetime.now().strftime("%d/%m/%Y")
        d.text((30, 30), "LISTA DE COMPRAS", fill=(0, 0, 0), font=f_bold)
        d.text((30, 65), f"DATA: {data_br}", fill=(100, 100, 100), font=f_norm)
        y_linha = 100
        if motivo:
            d.text((30, 95), f"MOTIVO: {str(motivo).upper()}", fill=(0, 51, 153), font=f_bold)
            y_linha = 135
        d.line((30, y_linha, largura-30, y_linha), fill=(0, 0, 0), width=2)
        y = y_linha + 25
        for item in itens:
            d.text((40, y), f"[X] {item}", fill=(0, 0, 0), font=f_norm)
            y += espaco_item
        d.text((30, y + 20), "by ®rvrs", fill=(150, 150, 150), font=f_norm)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

# --- Interface ---
app = ListaComprasPro()
st.markdown("<h1 style='text-align:center;'>🛒 Lista de Compras (Nuvem)</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("💾 NUVEM GOOGLE")
    nome_lista_nuvem = st.text_input("Nome para salvar:", placeholder="Ex: Mensal", key=f"cloud_name_{st.session_state.reset_trigger}")
    
    if st.button("📥 SALVAR NA PLANILHA", use_container_width=True):
        selecionados_nomes = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]
        if nome_lista_nuvem and selecionados_nomes:
            try:
                df_atual = conn.read(ttl=0)
                novo_dado = pd.DataFrame([{
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "nome_lista": nome_lista_nuvem.upper(),
                    "itens_json": json.dumps(selecionados_nomes, ensure_ascii=False)
                }])
                df_final = pd.concat([df_atual, novo_dado], ignore_index=True)
                conn.update(data=df_final)
                st.success(f"Lista '{nome_lista_nuvem}' salva!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
        else:
            st.warning("Dê um nome e marque itens!")

    st.divider()
    
    # Carregar listas da planilha
    try:
        df_nuvem = conn.read(ttl=0)
        if not df_nuvem.empty:
            opcoes = ["Selecionar..."] + list(df_nuvem['nome_lista'].unique())
            escolha = st.selectbox("Abrir lista salva:", opcoes)
            if escolha != "Selecionar..." and st.button("📂 CARREGAR LISTA"):
                dados_linha = df_nuvem[df_nuvem['nome_lista'] == escolha].iloc[-1]
                itens_recuperados = json.loads(dados_linha['itens_json'])
                
                # Desmarca tudo primeiro
                for chave in list(st.session_state.keys()):
                    if chave.startswith("check_"):
                        st.session_state[chave] = False
                
                # Marca os itens recuperados
                for item in itens_recuperados:
                    for cat_k in st.session_state.categorias.keys():
                        key_final = f"check_{item}_{cat_k}"
                        if key_final in st.session_state:
                            st.session_state[key_final] = True
                st.rerun()
    except:
        pass

    if st.button("🗑️ LIMPAR TELA", use_container_width=True): app.limpar_tudo()

# --- Grid Principal ---
selecionados_atual = [k.split("_")[1] for k, v in st.session_state.items() if k.startswith("check_") and v]

col1, col2, col3 = st.columns(3)
for i, (cat, produtos) in enumerate(st.session_state.categorias.items()):
    with [col1, col2, col3][i % 3]:
        st.subheader(cat)
        for p in produtos:
            st.checkbox(p, key=f"check_{p}_{cat}")

# --- Exportação ---
if selecionados_atual:
    st.divider()
    c_img, c_wa = st.columns(2)
    with c_img:
        img_bytes = app.gerar_imagem(sorted(selecionados_atual, key=remover_acentos), nome_lista_nuvem)
        st.download_button("🖼️ BAIXAR IMAGEM", img_bytes, "lista.png", use_container_width=True)
    with c_wa:
        msg_wa = f"*LISTA DE COMPRAS*\n" + "\n".join([f"[X] {i}" for i in sorted(selecionados_atual, key=remover_acentos)])
        url_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa + '\n\n_by ®rvrs_')}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲 WHATSAPP</div></a>', unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center;'>2026 | Desenvolvido por ®rvrs</p>", unsafe_allow_html=True)
