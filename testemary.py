import streamlit as st
import pandas as pd
import plotly.express as px






# Configuração deve ser a primeira linha
st.set_page_config(page_title="Análise Comparativa", layout="wide")

# Inicializa o estado da sessão para controle de autenticação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Tela de login
if not st.session_state["autenticado"]:
    st.title("Sistema de Autenticação")
    st.write("Insira suas credenciais para acessar as análise de dados.")
    
    # Adicionando keys únicas para evitar erro de ID duplicado
    usuario = st.text_input("Usuário", key="usuario_input")
    senha = st.text_input("Senha", type="password", key="senha_input")
    
    if st.button("Entrar"):
        if usuario == "admin" and senha == "1234":  # Substitua pela lógica real de autenticação
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
else:
    # Se autenticado, exibe a dashboard
    st.write("Bem-vindo ao painel da campanha de verão!")

    # Botão para sair
    if st.button("Sair"):
        st.session_state["autenticado"] = False
        st.rerun()  # Retorna à tela de login



    # Classificação fixa conforme solicitado
    CLASSIFICACAO = {
        "1. Recém-admitidos (Até 3 meses)": {"range": (0, 90), "color": "#1f77b4"},
        "2. Em adaptação (De 3 a 6 meses)": {"range": (91, 180), "color": "#9467bd"},
        "3. Quase 1 ano de casa (De 6 meses a 1 ano)": {"range": (181, 365), "color": "#e377c2"},
        "4. 1 ano completo (Entre 1 e 1,5 anos)": {"range": (366, 545), "color": "#f781bf"},
        "5. Avançando na empresa (Entre 1,5 e 2 anos)": {"range": (546, 730), "color": "#ff7f0e"},
        "6. Consolidados (Entre 2 e 3 anos)": {"range": (731, 1095), "color": "#2ca02c"},
        "7. Seniors (Entre 3 e 4 anos)": {"range": (1096, 1460), "color": "#d62728"},
        "8. Muito experientes (Mais de 4 anos)": {"range": (1461, float('inf')), "color": "#8c564b"}
    }

    # Mapeamento de cores para os gráficos
    COLOR_MAP = {k: v["color"] for k, v in CLASSIFICACAO.items()}

    # Função para classificar por dias
    def classificar_dias(dias):
        for classe, info in CLASSIFICACAO.items():
            min_d, max_d = info["range"]
            if min_d <= dias <= max_d:
                return classe
        return "Não classificado"

    # Estado da sessão para controle de navegação
    if 'study_selected' not in st.session_state:
        st.session_state.study_selected = False
        st.session_state.selected_study = None

    # Tela de seleção de estudos
    if not st.session_state.study_selected:
        st.title("Análise Campanha: Verão de Prêmios🏖️")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.title("Pronto para Análise.")
            if st.button("Pods (Análise Completa)"):
                st.session_state.study_selected = True
                st.session_state.selected_study = "pods"
                st.rerun()
        
        with col2:
            st.title("Pronto para Análise.")
            if st.button("Inbound"):
                st.session_state.study_selected = True
                st.session_state.selected_study = "Inbound"
                st.rerun()
        
        with col3:
            st.title("Em construção.")
            if st.button("Franquias"):
                st.session_state.study_selected = True
                st.session_state.selected_study = "Franquias"
                st.rerun()

    # Tela de análise (após seleção)
    else:
        # Criando abas
        tab1, tab2 = st.tabs(["📊 Dashboard", "🔍 Metodologia"])

        with tab1:
            if st.session_state.selected_study in ["pods", "Inbound"]:
                st.title(f"📊 - Análise de {st.session_state.selected_study.capitalize()}")
                
                # Upload
                file = st.file_uploader("Carregue seu Excel", type=["xlsx"], key="file_upload")
                if file:
                    # Dados
                    meses_pre = ["Agosto", "Setembro", "Outubro"]
                    meses_camp = ["Novembro", "Dezembro", "Janeiro"]
                    
                    # Seletores
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        mes_pre = st.selectbox("Mês pré-campanha", meses_pre)
                    with col2:
                        mes_camp = st.selectbox("Mês de campanha", meses_camp)
                    with col3:
                        semana = st.selectbox("Selecione a semana", ["S-1", "S-2", "S-3", "S-4", "S-5", "Final mês"])
                    
                    # Processamento
                    df_pre = pd.read_excel(file, sheet_name=mes_pre)
                    df_camp = pd.read_excel(file, sheet_name=mes_camp)
                    
                    # Padroniza colunas
                    df_pre.columns = df_pre.columns.str.strip().str.lower()
                    df_camp.columns = df_camp.columns.str.strip().str.lower()
                    
                    # Aplica classificação fixa
                    if 'dias' in df_pre.columns:
                        df_pre['class'] = df_pre['dias'].apply(classificar_dias)
                    if 'dias' in df_camp.columns:
                        df_camp['class'] = df_camp['dias'].apply(classificar_dias)

                                    # Métricas
                    def calc_metrics(df, mes, semana):
                        col_semana = f"{mes.lower()} {semana.lower()}"
                        if col_semana not in df.columns:
                            col_semana = semana.lower()
                        # Retorna: total, % acima da meta, média (já em porcentagem)
                        return len(df), (df[col_semana] >= 0.2).mean()*100, df[col_semana].mean()*100  # Multiplicado por 100 aqui

                    tot_pre, perc_pre, media_pre = calc_metrics(df_pre, mes_pre, semana)
                    tot_camp, perc_camp, media_camp = calc_metrics(df_camp, mes_camp, semana)

                    # Exibição
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total", f"{tot_pre} → {tot_camp}")
                    col2.metric("% Acima Meta", f"{perc_pre:.1f}% → {perc_camp:.1f}%", f"{(perc_camp-perc_pre):.1f}%")
                    col3.metric(
                        f"Média {semana}", 
                        f"{media_pre:.1f}% → {media_camp:.1f}%",  # Adicionado % aqui
                        f"{(media_camp-media_pre):.1f}%"  # Adicionado % aqui
    )

                    # Gráficos lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        col_semana_pre = f"{mes_pre.lower()} {semana.lower()}" if f"{mes_pre.lower()} {semana.lower()}" in df_pre.columns else semana.lower()
                        fig_pre = px.scatter(
                            df_pre, 
                            x='dias', 
                            y=col_semana_pre, 
                            color='class',
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_pre} {semana} (Pré-Campanha)",
                            hover_data={
                                'dias': True,
                                col_semana_pre: True,
                                'ev' if st.session_state.selected_study == "pods" else 'sdr': True,
                                'class': True
                            },
                        )
                        fig_pre.add_hline(y=0.2, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_pre, use_container_width=True)
                    
                    with col2:
                        col_semana_camp = f"{mes_camp.lower()} {semana.lower()}" if f"{mes_camp.lower()} {semana.lower()}" in df_camp.columns else semana.lower()
                        fig_camp = px.scatter(
                            df_camp, 
                            x='dias', 
                            y=col_semana_camp, 
                            color='class',
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_camp} {semana} (Campanha)",
                            hover_data={
                                'dias': True,
                                col_semana_camp: True,
                                'ev' if st.session_state.selected_study == "pods" else 'sdr': True,
                                'class': True
                            }
                        )
                        fig_camp.add_hline(y=0.2, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_camp, use_container_width=True)

                    # Insights
                    st.subheader("💡 Insights")
                    if perc_camp > perc_pre:
                        st.success(f"✅ Melhoria de {perc_camp-perc_pre:.1f}% na {semana} durante a campanha")
                    else:
                        st.warning(f"⚠️ Queda de {perc_pre-perc_camp:.1f}% na {semana} durante a campanha")

        with tab2:
            st.title("🔍 Mecânica da Análise")
            
            # Container principal com tabs
            metodologia_tab, interpretacao_tab, glossario_tab = st.tabs(["📋 Metodologia", "📊 Guia de Interpretação", "📚 Glossário"])
            
            with metodologia_tab:
                st.header("Fluxo da Análise", divider="blue")
                
                with st.expander("🔎 Coleta de Dados", expanded=True):
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown("""
                        **Fontes de dados:**
                        - Para os meses da Campanha(Novembro, Dezembro, Janeiro), os dados são os mesmos que foram publicados. 
                        - Para os meses referente ao periodo pré Campanha (Agosto, Setembro, Outubro), os dados são referente ao Dash CI - Vendas.
                        """)
                    
                    with cols[1]:
                        st.markdown("""
                        **Períodos analisados:**
                        - Pré-campanha: Agosto a Outubro
                        - Campanha: Novembro a Janeiro
                        """)
                
                with st.expander("⚙️ Processamento", expanded=True):       
                        st.markdown("""
                        **Critérios técnicos:**
                        - Meta de performance: ≥ 0.20
                        - Classificação por tempo de experiência:
                        """)
                        
                        # Tabela de classificação
                        classif_df = pd.DataFrame([
                            {"Classificação": k, "Faixa (dias)": f"{v['range'][0]}-{v['range'][1]}", "Cor": f"■"} 
                            for k, v in CLASSIFICACAO.items()
                            ])
            
            with interpretacao_tab:
                st.header("Como Ler os Gráficos", divider="green")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **📈 Elementos do Gráfico:**
                    - Cada ponto = 1 colaborador
                    - Eixo X: Tempo de casa (dias)
                    - Eixo Y: Performance na semana
                    - Cores: Categorias de experiência fixas
                    - Linha vermelha: Meta (0.20)
                    """)
                
                with col2:
                    st.markdown("""
                    **🔍 Dicas de Análise:**
                    1. Compare a distribuição dos pontos
                    2. Observe agrupamentos por categoria
                    3. Verifique quantos estão acima da linha
                    4. Analise a relação tempo×performance
                    5. Foque nas categorias com maior variação
                    """)
                
            
            with glossario_tab:
                st.header("Termos Técnicos", divider="orange")
                
                st.markdown("""
                | Termo | Definição | Exemplo |
                |-------|-----------|---------|
                | **Class** | Categorização fixa por tempo de experiência | 1. Recém-admitidos |
                | **Dias** | Tempo de casa do colaborador | 180 dias = 2. Em adaptação |
                | **S-1** | Performance na primeira semana do mês | Score de 0.15 a 0.25 |
                """)
                
                st.markdown("""
                **Legenda de Cores (Class):**
                """)
                
                # Legenda interativa com cores
                for classe, info in CLASSIFICACAO.items():
                    st.markdown(f"<span style='color:{info['color']}'>■</span> {classe} ({info['range'][0]}-{info['range'][1]} dias)", unsafe_allow_html=True)
