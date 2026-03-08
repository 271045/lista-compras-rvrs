# --- Trecho atualizado da Sidebar ---
# Localize a parte de CARREGAR / EXCLUIR e substitua por esta:

    # CARREGAR / EXCLUIR COM CONFIRMAÇÃO
    arquivos_salvos = sorted([f for f in os.listdir(DIRETORIO_LISTAS) if f.endswith('.json')])
    if arquivos_salvos:
        lista_escolhida = st.selectbox("Listas guardadas:", ["Selecionar..."] + arquivos_salvos)
        
        if lista_escolhida != "Selecionar...":
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📂 CARREGAR", use_container_width=True):
                    caminho = os.path.join(DIRETORIO_LISTAS, lista_escolhida)
                    with open(caminho, 'r', encoding='utf-8') as f:
                        st.session_state.selecionados = json.load(f)
                    st.session_state.reset_trigger += 1
                    st.success("Lista carregada!")
                    st.rerun()
            
            with c2:
                # Lógica de Confirmação de Exclusão
                if f"confirma_excluir_{lista_escolhida}" not in st.session_state:
                    st.session_state[f"confirma_excluir_{lista_escolhida}"] = False

                if not st.session_state[f"confirma_excluir_{lista_escolhida}"]:
                    if st.button("🗑️ EXCLUIR", use_container_width=True, type="secondary"):
                        st.session_state[f"confirma_excluir_{lista_escolhida}"] = True
                        st.rerun()
                else:
                    st.warning("Tem certeza?")
                    col_sim, col_nao = st.columns(2)
                    with col_sim:
                        if st.button("✅ SIM", use_container_width=True, type="primary"):
                            os.remove(os.path.join(DIRETORIO_LISTAS, lista_escolhida))
                            st.session_state[f"confirma_excluir_{lista_escolhida}"] = False
                            st.success("Apagada!")
                            st.rerun()
                    with col_nao:
                        if st.button("❌ NÃO", use_container_width=True):
                            st.session_state[f"confirma_excluir_{lista_escolhida}"] = False
                            st.rerun()
