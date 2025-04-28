import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

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
        if usuario == "mktops" and senha == "7772025":  # Substitua pela lógica real de autenticação
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
        "1. Recém-admitidos (Até 3 meses)": {"range": (0, 90), "color": "#1f77b4"},  # Azul
        "2. Em adaptação (De 3 a 6 meses)": {"range": (91, 180), "color": "#ff7f0e"},  # Laranja
        "3. Quase 1 ano de casa (De 6 meses a 1 ano)": {"range": (181, 365), "color": "#2ca02c"},  # Verde
        "4. 1 ano completo (Entre 1 e 1,5 anos)": {"range": (366, 545), "color": "#d62728"},  # Vermelho
        "5. Avançando na empresa (Entre 1,5 e 2 anos)": {"range": (546, 730), "color": "#9467bd"},  # Roxo
        "6. Consolidados (Entre 2 e 3 anos)": {"range": (731, 1095), "color": "#8c564b"},  # Marrom
        "7. Seniors (Entre 3 e 4 anos)": {"range": (1096, 1460), "color": "#e377c2"},  # Rosa
        "8. Muito experientes (Mais de 4 anos)": {"range": (1461, float('inf')), "color": "#17becf"}  # Ciano
    }

    CLUSTER_COLORS = {
        "0. Ultra": "#1f77b4",       # Azul
        "01. Diamante": "#ff7f0e",   # Laranja
        "02. Platina": "#2ca02c",    # Verde
        "03. Ouro": "#d62728",       # Vermelho
        "04. Prata": "#9467bd",      # Roxo
        "05. Incubadora": "#8c564b", # Marrom
        "06. Bronze": "#e377c2",     # Rosa
        "11. Avança +": "#17becf"    # Ciano
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
            st.title("Pronto para Análise.")
            if st.button("Franquias"):
                st.session_state.study_selected = True
                st.session_state.selected_study = "Franquias"
                st.rerun()

    # Tela de análise (após seleção)
    else:
        if st.session_state.selected_study in ["pods", "Inbound"]:
            # Criando abas para Pods e Inbound
            tab1, tab2 = st.tabs(["📊 Dashboard", "🔍 Metodologia"])

            with tab1:
                st.title(f"📊 - Análise de {st.session_state.selected_study.capitalize()}")
                
                # Upload
                file = st.file_uploader("Carregue seu Excel", type=["xlsx"], key="file_upload")
                if file:
                    # Dados
                    meses_pre = ["Agosto", "Setembro", "Outubro"]
                    meses_camp = ["Novembro", "Dezembro", "Janeiro"]
                    todos_os_meses = meses_pre + meses_camp
                    
                    # DataFrames para consolidação
                    df_geral = pd.DataFrame(columns=["Mês", "Média Final Mês"])
                    df_por_classe = pd.DataFrame(columns=["Mês", "Classe", "Média Final Mês"])

                    for mes in todos_os_meses:
                        try:
                            df_mes = pd.read_excel(file, sheet_name=mes)

                            if "Final mês" in df_mes.columns:
                                # Média geral
                                media_geral = df_mes["Final mês"].mean()
                                df_geral = pd.concat([
                                    df_geral,
                                    pd.DataFrame({"Mês": [mes], "Média Final Mês": [media_geral]})
                                ], ignore_index=True)

                                # Média por classe
                                if "class" in df_mes.columns:
                                    media_por_classe = df_mes.groupby("class")["Final mês"].mean().reset_index()
                                    media_por_classe["Mês"] = mes
                                    media_por_classe.rename(columns={"class": "Classe", "Final mês": "Média Final Mês"}, inplace=True)

                                    df_por_classe = pd.concat([df_por_classe, media_por_classe], ignore_index=True)
                                else:
                                    st.warning(f"A coluna 'class' não existe na aba {mes}")
                            else:
                                st.warning(f"A coluna 'Final mês' não existe na aba {mes}")

                        except Exception as e:
                            st.warning(f"Erro ao processar {mes}: {e}")
                    
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

                    # Insights MÉDIAS GERAIS------------------------------------------------------------------------------------------------------------
                    df_geral["Média Final Mês (%)"] = df_geral["Média Final Mês"] * 100
                    df_por_classe["Média Final Mês (%)"] = df_por_classe["Média Final Mês"] * 100
                    
                    st.subheader("Média de Atingimento Geral", divider='blue')
                    chart_geral = alt.Chart(df_geral).mark_line(point=True,
                                                                color='#ff7f0e',
                                                                strokeWidth=2,
                                                                interpolate='monotone').encode(
                        x=alt.X("Mês", sort=todos_os_meses),
                        y=alt.Y("Média Final Mês (%)", title="Média (%)"),
                        tooltip=[alt.Tooltip("Mês"), alt.Tooltip("Média Final Mês (%)", format=".2f")]
                        ).properties(
                        title="Média Geral por Mês (%)",
                        width=700,
                        height=400
                        )
                    st.altair_chart(chart_geral)
                    
                    #--------------------------------------------------------------------------------------------------------------------------------------
                    st.subheader("Média de Atingimento por Classe", divider='blue')
                    import streamlit as st
                    import altair as alt   

                    chart_classe = (
                        alt.Chart(df_por_classe)
                        .mark_line(point=True, strokeWidth=1, interpolate='monotone')
                        .encode(
                            x=alt.X(
                                "Mês",
                                sort=todos_os_meses,
                                axis=alt.Axis(grid=False)
                            ),
                            y=alt.Y(
                                "Média Final Mês (%)",
                                title="Média (%)",
                                axis=alt.Axis(grid=False)
                            ),
                            color=alt.Color(  # Color configurado explicitamente aqui
                                "Classe:N",
                                legend=alt.Legend(
                                    title="Classe",
                                    orient="right",
                                    direction="vertical",
                                    labelLimit=400,  # controla o quanto ele pode escrever antes de cortar
                                    labelFontSize=12,
                                    titleFontSize=14
                                )
                            ),
                            tooltip=[
                                alt.Tooltip("Mês"),
                                alt.Tooltip("Classe"),
                                alt.Tooltip("Média Final Mês (%)", format=".2f")
                            ]
                        )
                        .properties(
                            title="Média por Classe e Mês (%)",
                            width=800,
                            height=400
                        )
                    )

                    st.altair_chart(chart_classe, use_container_width=True)

                    
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

        # ... (código anterior permanece igual até a linha onde começa "Franquias")
#---------------------------------------------------------------------------------------------------------------------------- EC ALTERANDO
        elif st.session_state.selected_study == "Franquias":
            # Criando abas para Franquias (agora com 4 abas)
            tab1, tab2, tab3, tab4 = st.tabs(["🏢 EC", "📞 EV", "🎯 SDR", "🔍 Mecânica"])

            with tab1:  # Aba EC
                st.header("🏢 EC - Análise Mensal")
                file_ec = st.file_uploader("Carregue o Excel da EC", type=["xlsx"], key="ec_upload")

                if file_ec:
                    # Dados
                    meses_pre = ["Agosto", "Setembro", "Outubro"]
                    meses_camp = ["Novembro", "Dezembro", "Janeiro"]
                    dados_key = ["dias","nmrr ec"]
                    dados_class = ["Cluster","Tempo de Casa"]
                    
                    # Seletores---------------------------------------------------------
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        mes_pre = st.selectbox("Mês pré-campanha", meses_pre, key="ec_mes_pre")
                    with col2:
                        mes_camp = st.selectbox("Mês de campanha", meses_camp, key="ec_mes_camp")
                    with col3:
                        var_x = st.selectbox("valor do eixo X", dados_key, key="chaves")
                    with col4:
                        var_class = st.selectbox("Classificação",dados_class, key="classificao" )
                    
                    # Processamento
                    df_pre = pd.read_excel(file_ec, sheet_name=mes_pre)
                    df_camp = pd.read_excel(file_ec, sheet_name=mes_camp)

                    def calc_metrics_ec(df):
                        meta = 3.0
                        return (
                            len(df),
                            (df['ating reunião'] >= meta).mean() * 100,
                            df['ating reunião'].mean() * 100,
                            meta * 100
                        )

                    tot_pre, perc_pre, media_pre, meta = calc_metrics_ec(df_pre)
                    tot_camp, perc_camp, media_camp, _ = calc_metrics_ec(df_camp)

                    media_nmrr_pre = df_pre['nmrr ec'].mean()
                    media_nmrr_camp = df_camp['nmrr ec'].mean()
                    
                    media_reu_util_pre = df_pre['reu_util'].mean()
                    media_reu_util_camp = df_camp['reu_util'].mean()
                    
                    # Classificação por tempo de casa
                    if 'dias' in df_pre.columns:
                        df_pre['class'] = df_pre['dias'].apply(classificar_dias)
                    if 'dias' in df_camp.columns:
                        df_camp['class'] = df_camp['dias'].apply(classificar_dias)
                        
                    # Definir variáveis de cor com base na seleção---------------------------------
                    color_var = 'cluster' if var_class == "Cluster" else 'class'
                    color_map = CLUSTER_COLORS if var_class == "Cluster" else CLUSTER_COLORS

                    # Métricas para análise mensal
                    # Dados de franquias direto do código
                    dados_canais = {
                        "Canais": ["Franquias"],
                        "Agosto": [0.79],
                        "Setembro": [0.80],
                        "Outubro": [0.68],
                        "Novembro": [0.73],
                        "Dezembro": [0.72],
                        "Janeiro": [0.82],
                    }

                    df_metas = pd.DataFrame(dados_canais).set_index("Canais").T
                    df_metas.index.name = 'mês'
                    df_metas.reset_index(inplace=True)
                    df_metas.columns = ['mês', 'franquias']

                    # Pega as metas da franquia para os meses selecionados
                    meta_franquia_pre = df_metas.loc[df_metas['mês'] == mes_pre, 'franquias'].values
                    meta_franquia_camp = df_metas.loc[df_metas['mês'] == mes_camp, 'franquias'].values

                    meta_franquia_pre = meta_franquia_pre[0] if len(meta_franquia_pre) > 0 else None
                    meta_franquia_camp = meta_franquia_camp[0] if len(meta_franquia_camp) > 0 else None

                    # Exibição
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total ECs", f"{tot_pre} → {tot_camp}")
                    col2.metric("Média NMRR ECs", f"R$ {media_nmrr_pre:,.0f}".replace(",", ".") + f" → R$ {media_nmrr_camp:,.0f}".replace(",", "."), f"R$ {(media_nmrr_camp - media_nmrr_pre):,.0f}".replace(",", "."))
                    col3.metric("Média Reu_Util", f"{media_reu_util_pre:.1f} → {media_reu_util_camp:.1f}", f"{(media_reu_util_camp - media_reu_util_pre):+.1f}")
                    col4.metric(
                            "Meta Franquia",
                            f"{meta_franquia_pre:.0%} → {meta_franquia_camp:.0%}",
                            f"{(meta_franquia_camp - meta_franquia_pre):.1%}"
                        )
                    
                    # Gráficos
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_pre = px.scatter(
                            df_pre, 
                            x= var_x, 
                            y='reu_util',
                            color= color_var,
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_pre} (Pré-Campanha)",
                            hover_data={
                                'dias': ':.0f',  # Sem casas decimais
                                'reu_util': ':.2f',  # 2 casas decimais
                                'nmrr ec': ':.2f',
                                'ating reunião': ':.2f',  # 2 casas decimais
                                'cluster': True,
                                'usuario_email': True,
                                'class': True
                            },
                            labels={'reu_util': 'Média reunião'}
                        )
                        fig_pre.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Meta: 3.0")
                        st.plotly_chart(fig_pre, use_container_width=True, key=f"ec_pre_{mes_pre}")
                    
                    with col2:
                        fig_camp = px.scatter(
                            df_camp, 
                            x= var_x, 
                            y='reu_util', 
                            color=color_var,
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_camp} (Campanha)",
                            hover_data={
                                'dias': ':.0f',  # Sem casas decimais
                                'reu_util': ':.2f',  # 2 casas decimais
                                'nmrr ec': ':.2f',
                                'ating reunião': ':.2f',  # 2 casas decimais
                                'cluster': True,
                                'usuario_email': True,
                                'class': True
                            },
                            labels={'reu_util': 'Média reunião'}
                        )
                        fig_camp.add_hline(y=3.0, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_camp, use_container_width=True, key=f"ec_camp_{mes_camp}")
                    #EDITADO ATÉ AQUI A PARTE DE CLUSTER E EIXOS ATUALIZADOS.
                    # Insights (removida a aba de correlação)
                    

                    # Gráficos de desempenho por cluster
                    st.subheader("📊 Desempenho por Cluster", divider="blue")
                    
                    dados_key_2 = ["dias","nmrr ec"]
                    col1 = st.columns(1)[0]
                    with col1:
                        var_x = st.selectbox("valor do eixo X", dados_key_2 + ["reu_util"], key="chaves_2")
                    
                    df_agrupado = df_pre.groupby('cluster')[dados_key_2 + ['reu_util']].mean().reset_index()
                    df_agrupado_camp = df_camp.groupby('cluster')[dados_key_2 + ['reu_util']].mean().reset_index()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_cluster_pre = px.bar(
                             df_agrupado.sort_values(var_x, ascending=False),
                            x='cluster',
                            y=var_x,
                            color='cluster',
                            color_discrete_map=CLUSTER_COLORS,
                            title=f'Média {var_x} por Cluster - {mes_pre}',
                            labels={var_x: f'Média {var_x}', 'cluster': 'Cluster'},
                            text=var_x
                        )
                        fig_cluster_pre.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        st.plotly_chart(fig_cluster_pre, use_container_width=True, key=f"ec_cluster_pre_{mes_pre}")
                    
                    with col2:
                        fig_cluster_camp = px.bar(
                            df_agrupado_camp.sort_values(var_x, ascending=False),
                            x='cluster',
                            y=var_x,
                            color='cluster',
                            color_discrete_map=CLUSTER_COLORS,
                            title=f'Média {var_x} por Cluster - {mes_camp}',
                            labels={var_x: f'Média {var_x}', 'cluster': 'Cluster'},
                            text=var_x
                        )
                        fig_cluster_camp.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        st.plotly_chart(fig_cluster_camp, use_container_width=True, key=f"ec_cluster_camp_{mes_camp}")
                        
                    st.subheader("📊 Analise Geral Campanha",divider="blue")
                    
                    import altair as alt
                    meses_analise = ["Agosto", "Setembro", "Outubro", "Novembro", "Dezembro", "Janeiro"]

                    # Coleta as médias
                    dados_grafico = []
                    for mes in meses_analise:
                        try:
                            df = pd.read_excel(file_ec, sheet_name=mes)
                            df.columns = df.columns.str.strip().str.lower()

                            dados_grafico.append({
                                "Mês": mes,
                                "NMRR EC": df['nmrr ec'].mean(),
                                "Reu_Util": df['reu_util'].mean()
                            })

                        except Exception as e:
                            st.warning(f"Erro ao processar mês {mes}: {e}")

                    df_plot = pd.DataFrame(dados_grafico)

                    # --- NOVO CÓDIGO PARA CALCULAR VARIAÇÕES ---
                    # Calcular variações mensais
                    df_plot['Variação NMRR'] = df_plot['NMRR EC'].diff().fillna(0)
                    df_plot['Variação Reu'] = df_plot['Reu_Util'].diff().fillna(0)

                    # Formatando os textos para incluir as variações
                    df_plot['Texto NMRR'] = df_plot.apply(
                        lambda x: f"{x['NMRR EC']:.1f}\n({x['Variação NMRR']:+.1f})", axis=1
                    )
                    df_plot['Texto Reu'] = df_plot.apply(
                        lambda x: f"{x['Reu_Util']:.1f}\n({x['Variação Reu']:+.1f})", axis=1
                    )
                    # --------------------------------------------

                    base = alt.Chart(df_plot).encode(
                        x=alt.X('Mês:N', sort=meses_analise, title='Mês')
                    )

                    # NMRR EC - Barras (eixo esquerdo)
                    left_axis = alt.Axis(title='NMRR EC (R$)', titleFontWeight='bold')
                    bars = base.mark_bar(color='#1f77b4',
                                         size=80,
                                         cornerRadiusTopRight=8,
                                         cornerRadiusTopLeft=8,
                                         opacity=0.5,
                                         ).encode(
                        y=alt.Y('NMRR EC:Q', axis=left_axis),
                        tooltip=[
                            alt.Tooltip('Mês:N'),
                            alt.Tooltip('NMRR EC:Q', format='$,.0f'),
                            alt.Tooltip('Variação NMRR:Q', format='$,.0f')
                        ]
                    )

                    # Reu_Util - Linha (eixo direito)
                    right_axis = alt.Axis(title='Reu_Util', titleColor='#ff7f0e', 
                                        orient='right', titleFontWeight='bold', 
                                        labelColor='#ff7f0e', titlePadding=50)
                    line = base.mark_line(point=True,
                                        color='#ff7f0e',
                                        strokeWidth=1.5,
                                        interpolate='monotone'
                                        ).encode(
                        y=alt.Y('Reu_Util:Q', axis=right_axis, scale=alt.Scale(domain=[1, 4])),
                        tooltip=[
                            alt.Tooltip('Mês'),
                            alt.Tooltip('Reu_Util', format='.2f'),
                            alt.Tooltip('Variação Reu', format='.2f')
                        ]
                    )

                    # Textos com variações (substitui os textos originais)
                    texto_barras = base.mark_text(
                        align='center',
                        baseline='bottom',
                        dy=-5,
                        color='white',
                        lineHeight=15,
                        fontSize=13,
                        fontWeight='bold'
                    ).encode(
                        text='Texto NMRR:N',
                        y='NMRR EC:Q'
                    )

                    texto_linha = base.mark_text(
                        align='left',
                        baseline='top',
                        strokeWidth=1.5, #expressura da linha
                        interpolate='monotone', #suaviza a linhas
                        dx=0,
                        dy=-18,
                        color='#ff7f0e',
                        lineHeight=20,
                        fontSize=13,
                        fontWeight='bold'
                    ).encode(
                        text='Texto Reu:N',
                        y='Reu_Util:Q',
                        
                    )

                    # Combinar os gráficos (versão modificada)
                    chart = alt.layer(
                        bars + texto_barras,  # já usa 'Texto NMRR'
                        line + texto_linha     # já usa 'Texto Reu'
                    ).resolve_scale(
                        y='independent'
                    ).properties(
                        width=700,
                        height=450,
                        title='Média de NMRR EC - Média Reunião dia Útil'
                    ).configure_view(
                        strokeOpacity=0
                    ).configure_axisY(
                        grid=False # retirar as linhas de fundo 
                    )

                    st.altair_chart(chart, use_container_width=True)
                    

            with tab2: #----------------------------------------------------- ajustes evs 
                st.header("📞 EV - Análise Mensal")
                file_ev = st.file_uploader("Carregue o Excel da EV", type=["xlsx"], key="ev_upload")

                if file_ev:
                    # Dados
                    meses_pre = ["Agosto", "Setembro", "Outubro"]
                    meses_camp = ["Novembro", "Dezembro", "Janeiro"]
                    dados_evs = ["dias","nmrr ev"]
                    dados_class_ev = ["Cluster", "Tempo de Casa"]
                    
                    # Seletores
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        mes_pre = st.selectbox("Mês pré-campanha", meses_pre, key="ev_mes_pre")
                    with col2:
                        mes_camp = st.selectbox("Mês de campanha", meses_camp, key="ev_mes_camp")
                    with col3:
                        var_xx = st.selectbox("Valor do eixo X", dados_evs, key="evs_chaves")
                    with col4:
                        dados_class_ev_ = st.selectbox("Classificação", dados_class_ev, key="classificação ev")
                    # definindo as classificações dos EVs. 
                    
                    # Processamento
                    df_pre = pd.read_excel(file_ev, sheet_name=mes_pre)
                    df_camp = pd.read_excel(file_ev, sheet_name=mes_camp)
                    
                    # # Padroniza colunas
                    df_pre.columns = df_pre.columns.str.strip().str.lower()
                    df_camp.columns = df_camp.columns.str.strip().str.lower()
                    
                    # Classificação por tempo de casa
                    if 'dias' in df_pre.columns:
                        df_pre['class'] = df_pre['dias'].apply(classificar_dias)
                    if 'dias' in df_camp.columns:
                        df_camp['class'] = df_camp['dias'].apply(classificar_dias)
                        
                    # Definir variáveis de cor com base na seleção---------------------------------
                    color_var = 'cluster' if dados_class_ev_ == "Cluster" else 'class'
                    color_map = CLUSTER_COLORS if dados_class_ev_ == "Cluster" else CLUSTER_COLORS

                    # Métricas para análise mensal
                    # Versão simplificada (sem unidade)
                    def calc_metrics_ev(df):
                            meta_ev = df['meta nmrr ev'].mean()
                            return (
                                len(df),
                                (df['nmrr ev'] >= df['meta nmrr ev']).mean() * 100,
                                df['nmrr ev'].sum(),
                                meta_ev * len(df)
                            )

                        # Chamada com 4 valores
                    tot_pre, perc_ating_ev_pre, total_ev_pre, meta_total_ev_pre = calc_metrics_ev(df_pre)
                    tot_camp, perc_ating_ev_camp, total_ev_camp, meta_total_ev_camp = calc_metrics_ev(df_camp)
                        
                    media_nmrr_ev_pre = df_pre['nmrr ev'].mean()
                    media_nmrr_ev_camp = df_camp['nmrr ev'].mean()
                        
                    # Dados de franquias direto do código - dados gerais das franquias --------------------------------------------------
                    dados_canais = {
                        "Canais": ["Franquias"],
                        "Agosto": [0.79],
                        "Setembro": [0.80],
                        "Outubro": [0.68],
                        "Novembro": [0.73],
                        "Dezembro": [0.72],
                        "Janeiro": [0.82],
                    }

                    df_metas = pd.DataFrame(dados_canais).set_index("Canais").T
                    df_metas.index.name = 'mês'
                    df_metas.reset_index(inplace=True)
                    df_metas.columns = ['mês', 'franquias']

                    # Pega as metas da franquia para os meses selecionados
                    meta_franquia_pre = df_metas.loc[df_metas['mês'] == mes_pre, 'franquias'].values
                    meta_franquia_camp = df_metas.loc[df_metas['mês'] == mes_camp, 'franquias'].values

                    meta_franquia_pre = meta_franquia_pre[0] if len(meta_franquia_pre) > 0 else None
                    meta_franquia_camp = meta_franquia_camp[0] if len(meta_franquia_camp) > 0 else None   

                        # Exibição permanece a mesma

                    # Exibição
                    delta_ev = media_nmrr_ev_camp - media_nmrr_ev_pre
                                        
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total EVs", f"{tot_pre} → {tot_camp}")
                    col2.metric("Média NMRR EV", 
                                f"R$ {media_nmrr_ev_pre:,.0f}".replace(",", ".") + f" → R$ {media_nmrr_ev_camp:,.0f}".replace(",", "."),
                                delta_ev,
                                delta_color="normal")
                    col3.metric(
                            "Meta Franquia",
                            f"{meta_franquia_pre:.0%} → {meta_franquia_camp:.0%}",
                            f"{(meta_franquia_camp - meta_franquia_pre):.1%}"
                        )
                    
                    # Gráficos com classificação somente por cluster
                                        
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_pre = px.scatter(
                            df_pre, 
                            x=var_xx, 
                            y='ating ev',
                            color= color_var,  # 
                            color_discrete_map= COLOR_MAP,
                            title=f"{mes_pre} (Pré-Campanha)",
                            hover_data={
                                'dias': ':.0f',
                                'ating ev': ':.2f',
                                'nmrr ev': ':,.0f',
                                'meta nmrr ev': ':,.0f',
                                'cluster': True,
                                'vendedor_nome': True
                            },
                            labels={'ating ev': 'Atingimento EV'}
                        )
                        fig_pre.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Meta: 100%")
                        st.plotly_chart(fig_pre, use_container_width=True, key=f"ev_pre_{mes_pre}")
                    
                    with col2:
                        fig_camp = px.scatter(
                            df_camp, 
                            x=var_xx, 
                            y='ating ev', 
                            color=color_var,
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_camp} (Campanha)",
                            hover_data={
                                'dias': ':.0f',  # Sem casas decimais
                                'ating ev': ':.2f',  # 2 casas decimais
                                'nmrr ev': ':,.0f',  # Formato numérico exato
                                'meta nmrr ev': ':,.0f',
                                'nmrr unidade': True,
                                'meta nmrr unidade': True,
                                'cluster': True,
                                'vendedor_nome': True,
                                'class': True
                            }
                        )
                        fig_camp.add_hline(y=1.0, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_camp, use_container_width=True, key=f"ev_camp_{mes_camp}")


                    # Gráficos de desempenho por cluster
                    st.subheader("📊 Desempenho por Cluster", divider='blue')
                    
                    dados_evs_2= ["nmrr ev", "ating ev"]
                    col1 = st.columns(1)[0]
                    with col1:
                            mes_dados = st.selectbox("Kpis ev", dados_evs_2, key="ev_mes_predfsdf")
                            
                    df_pre_grouped = df_pre.groupby('cluster', as_index=False)[mes_dados].mean()
                    df_camp_grouped = df_camp.groupby('cluster', as_index=False)[mes_dados].mean()

                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_cluster_pre = px.bar(
                            df_pre_grouped.sort_values(mes_dados, ascending=False),
                            x='cluster',
                            y= mes_dados,
                            color='cluster',
                            color_discrete_map=CLUSTER_COLORS,
                            title=f'Média Atingimento EV por Cluster - {mes_pre}',
                            labels={mes_dados: f'Média {mes_dados}', 'cluster': 'Cluster'},
                            text= mes_dados
                        )
                        fig_cluster_pre.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        st.plotly_chart(fig_cluster_pre, use_container_width=True, key=f"ev_cluster_pre_{mes_pre}")
                    
                    with col2:
                        fig_cluster_camp = px.bar(
                            df_camp_grouped.sort_values(mes_dados, ascending=False),
                            x='cluster',
                            y= mes_dados,
                            color='cluster',
                            color_discrete_map=CLUSTER_COLORS,
                            title=f'Média Atingimento EV por Cluster - {mes_camp}',
                            labels={mes_dados: f'Média {mes_dados}', 'cluster': 'Cluster'},
                            text= mes_dados
                        )
                        fig_cluster_camp.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        st.plotly_chart(fig_cluster_camp, use_container_width=True, key=f"ev_cluster_camp_{mes_camp}")
                        
                    st.subheader("🎈Analise Geral da campanhas EVs",divider='blue')#analise com grafico e linhas.........
                    import altair as alt
                    #dados metas
                    dados_canais = {
                    "Canais": ["Franquias"],
                    "Agosto": [0.79],
                    "Setembro": [0.80], 
                    "Outubro": [0.68],
                    "Novembro": [0.73],
                    "Dezembro": [0.72],
                    "Janeiro": [0.82],
                    }

                    df_metas = pd.DataFrame(dados_canais).set_index("Canais").T
                    df_metas.index.name = 'mês'
                    df_metas.reset_index(inplace=True)
                    df_metas.columns = ['mês', 'franquias']

                    meta_franquia_pre = df_metas.loc[df_metas['mês'] == mes_pre, 'franquias'].values[0]
                    meta_franquia_camp = df_metas.loc[df_metas['mês'] == mes_camp, 'franquias'].values[0]
                    
                    meses_analise = ["Agosto", "Setembro", "Outubro", "Novembro", "Dezembro", "Janeiro"]
                    
                    dados_grafico = []
                    for mes in meses_analise:
                        try:
                            df = pd.read_excel(file_ev, sheet_name=mes)
                            df.columns = df.columns.str.strip().str.lower()
                            
                            franquia_valor = df_metas.loc[df_metas['mês'] == mes, 'franquias'].values[0]
                            
                            dados_grafico.append({
                            "Mês": mes,
                            "nmrr ev": df['nmrr ev'].mean(),
                            "Franquias": franquia_valor * 100  # Convertendo para porcentagem (1.0 = 100%)
                        })
                        except Exception as e:
                            st.warning(f"Erro ao processar mês {mes}: {e}")
                    df_plot = pd.DataFrame(dados_grafico)

                    # Calcular variações mensais
                    df_plot['Variação NMRR'] = df_plot['nmrr ev'].diff().fillna(0)
                    df_plot['Variação Franquias'] = df_plot['Franquias'].diff().fillna(0)

                    # Formatando os textos
                    df_plot['Texto NMRR'] = df_plot.apply(lambda x: f"{x['nmrr ev']:.0f} ({x['Variação NMRR']:+.0f})", axis=1)
                    df_plot['Texto Franquias'] = df_plot.apply(lambda x: f"{x['Franquias']/100:.0%} ({x['Variação Franquias']/100:+.0%})", axis=1)
                    
                    base = alt.Chart(df_plot).encode(
                    x=alt.X('Mês:N', sort=meses_analise, title='Mês', axis=alt.Axis(labelAngle=0))
                    )

                    # NMRR ev - Barras (eixo esquerdo)
                    left_axis = alt.Axis(title='nmrr ev (R$)', titleColor='#1f77b4', titleFontWeight='bold')
                    bars = base.mark_bar(color='#1f77b4',
                                         size=80,
                                         cornerRadiusTopRight=8,
                                         cornerRadiusTopLeft=8,
                                         opacity=0.5,).encode(
                        y=alt.Y('nmrr ev:Q', axis=left_axis),
                        tooltip=['Mês', alt.Tooltip('nmrr ev:Q', title='nmrr ev (R$)'), 
                                alt.Tooltip('Variação nmrr ev:Q', title='Variação NMRR (R$)')]
                    )

                    # Franquias atingimento - Linha tracejada (eixo direito)
                    right_axis = alt.Axis(title='Meta Franquias (%)', titleColor='#ff7f0e', 
                                        orient='right', titleFontWeight='bold', 
                                        titlePadding=50)
                    
                    line_franquias = base.mark_line(point=True,
                                                    color='#ff7f0e',
                                                    strokeWidth=2,
                                                    interpolate='monotone',
                                                    strokeDash=[3,3]).encode(
                        y=alt.Y('Franquias:Q', axis=right_axis),
                        tooltip=['Mês', alt.Tooltip('Franquias:Q', title='Franquias', format='.0%'),
                                alt.Tooltip('Variação Franquias:Q', title='Variação Franquias', format='+.0%')]
                    )

                    # Textos com valores
                    texto_barras = base.mark_text(
                        align='center',
                        baseline='bottom',
                        dy=-5,
                        color='white',
                        lineHeight=15,
                        fontSize=13,
                        fontWeight='bold'
                        ).encode(
                        text='Texto NMRR:N',
                        y='nmrr ev:Q'
                    )
                    
                    texto_franquias = base.mark_text(align='left', 
                        baseline='top',
                        interpolate='monotone',
                        dx=0, 
                        dy=-18,
                        color='#ff7f0e',
                        lineHeight=20,
                        fontSize=13,
                        fontWeight='bold').encode(
                        text='Texto Franquias:N',
                        y='Franquias:Q'
                    )   
                    
                    # Combinar os gráficos (apenas NMRR e Franquias)
                    chart = alt.layer(
                        bars + texto_barras,
                        line_franquias + texto_franquias
                    ).resolve_scale(
                        y='independent'
                    ).properties(
                        width=700,
                        height=450,
                        title='Desempenho Ev: NMRR vs Meta Franquias'
                    ).configure_axis(
                        grid=False
                    ).configure_view(
                        strokeOpacity=0
                    ).configure_axisY(
                        grid=False
                    )

                    st.altair_chart(chart, use_container_width=True)

            with tab3:#---------------------------------------------------------------------------------------------
                st.header("🎯 SDR - Análise Mensal")
                file_sdr = st.file_uploader("Carregue o Excel do SDR", type=["xlsx"], key="sdr_upload")

                if file_sdr:
                    # Dados
                    meses_pre = ["Agosto", "Setembro", "Outubro"]
                    meses_camp = ["Novembro", "Dezembro", "Janeiro"]
                    dados_key_sdr = ["dias","tarefas sdr"]
                    dados_class_sdr = ["Cluster","Tempo de Casa"]
                    
                    # Seletores
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        mes_pre = st.selectbox("Mês pré-campanha", meses_pre, key="sdr_mes_pre")
                    with col2:
                        mes_camp = st.selectbox("Mês de campanha", meses_camp, key="sdr_mes_camp")
                    with col3:
                        keys_sdrs = st.selectbox("Valor eixo X", dados_key_sdr, key="sdreixos")
                    with col4:
                        class_sdr = st.selectbox("Classificação", dados_class_sdr, key="sdr_classes")
                    
                    
                    # Processamento
                    df_pre = pd.read_excel(file_sdr, sheet_name=mes_pre)
                    df_camp = pd.read_excel(file_sdr, sheet_name=mes_camp)
                    
                    # Padroniza colunas
                    df_pre.columns = df_pre.columns.str.strip().str.lower()
                    df_camp.columns = df_camp.columns.str.strip().str.lower()
                    
                    # Classificação por tempo de casa
                    if 'dias' in df_pre.columns:
                        df_pre['class'] = df_pre['dias'].apply(classificar_dias)
                    if 'dias' in df_camp.columns:
                        df_camp['class'] = df_camp['dias'].apply(classificar_dias)

                    def calc_metrics_sdr(df):
                        meta = 1.0
                        return (
                            len(df),
                            (df['atig sdr'] >= meta).mean() * 100,
                            df['atig sdr'].mean() * 100,
                            meta * 100
                        )

                    tot_pre, perc_pre, media_pre, meta = calc_metrics_sdr(df_pre)
                    tot_camp, perc_camp, media_camp, _ = calc_metrics_sdr(df_camp)

                    media_ating_pre = df_pre['atig sdr'].mean()
                    media_ating_camp = df_camp['atig sdr'].mean()
                    
                    media_tarefas_sdr_pre = df_pre['tarefas sdr'].mean()
                    media_tarefas_sdr_camp = df_camp['tarefas sdr'].mean()
                    
                    # Definir variáveis de cor com base na seleção---------------------------------
                    color_var = 'cluster' if class_sdr == "Cluster" else 'class'
                    color_map = CLUSTER_COLORS if class_sdr == "Cluster" else CLUSTER_COLORS

                    # Métricas para análise mensal
                    # Dados de franquias direto do código
                    dados_canais = {
                        "Canais": ["Franquias"],
                        "Agosto": [0.79],
                        "Setembro": [0.80],
                        "Outubro": [0.68],
                        "Novembro": [0.73],
                        "Dezembro": [0.72],
                        "Janeiro": [0.82],
                    }

                    df_metas = pd.DataFrame(dados_canais).set_index("Canais").T
                    df_metas.index.name = 'mês'
                    df_metas.reset_index(inplace=True)
                    df_metas.columns = ['mês', 'franquias']

                    # Pega as metas da franquia para os meses selecionados
                    meta_franquia_pre = df_metas.loc[df_metas['mês'] == mes_pre, 'franquias'].values
                    meta_franquia_camp = df_metas.loc[df_metas['mês'] == mes_camp, 'franquias'].values

                    meta_franquia_pre = meta_franquia_pre[0] if len(meta_franquia_pre) > 0 else None
                    meta_franquia_camp = meta_franquia_camp[0] if len(meta_franquia_camp) > 0 else None
                    
                    #Exibição dos KPIS PRINCIPAIS 
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total SDR", f"{tot_pre} → {tot_camp}")
                    col2.metric("Média ating SDR", f"{media_ating_pre:.2f} % → {media_ating_camp:.2f} %", f"{(media_ating_camp - media_ating_pre):.2f} %")
                    col3.metric("Média Tarefa Reunião", f"{media_tarefas_sdr_pre:.1f} →  {media_tarefas_sdr_camp:.1f}", f"{(media_tarefas_sdr_camp - media_tarefas_sdr_pre):.1f}")
                    col4.metric(
                            "Meta Franquia",
                            f"{meta_franquia_pre:.0%} → {meta_franquia_camp:.0%}",
                            f"{(meta_franquia_camp - meta_franquia_pre):.1%}"
                        )
                    
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_pre = px.scatter(
                            df_pre, 
                            x=keys_sdrs, 
                            y='atig sdr',
                            color=color_var,  # Somente cluster
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_pre} (Pré-Campanha)",
                            hover_data={
                                'dias': ':.0f',  # Sem casas decimais
                                'atig sdr': ':.2f',  # 2 casas decimais
                                'tarefas sdr': True,
                                'meta sdr': True,
                                'nmrr unidade': ':,.0f',  # Formato exato
                                'meta unidade nmrr': ':,.0f',
                                'cluster': True,
                                'usuario_nome': True
                            },
                            labels={'atig sdr': 'Atingimento SDR'}
                        )
                        fig_pre.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Meta: 100%")
                        st.plotly_chart(fig_pre, use_container_width=True, key=f"sdr_pre_{mes_pre}")
                    
                    with col2:
                        fig_camp = px.scatter(
                            df_camp, 
                            x=keys_sdrs, 
                            y='atig sdr', 
                            color=color_var,  # Somente cluster
                            color_discrete_map=COLOR_MAP,
                            title=f"{mes_camp} (Campanha)",
                            hover_data={
                                'dias': ':.0f',  # Sem casas decimais
                                'atig sdr': ':.2f',  # 2 casas decimais
                                'tarefas sdr': True,
                                'meta sdr': True,
                                'nmrr unidade': ':,.0f',  # Formato numérico exato
                                'meta unidade nmrr': ':,.0f',
                                'cluster': True,
                                'usuario_nome': True,
                                'class': True
                            }
                        )
                        fig_camp.add_hline(y=1.0, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_camp, use_container_width=True, key=f"sdr_camp_{mes_camp}")

                    # Gráficos de desempenho por cluster
                    st.subheader("📊 Desempenho por Cluster", divider='blue')
                    
                    dados_sdr_2= ["atig sdr", "tarefas sdr"]
                    col1 = st.columns(1)[0]
                    with col1:
                            mes_dados_sdr = st.selectbox("Kpis sdrs", dados_sdr_2, key="sdr_mes_predfsdf")
                            
                    df_pre_grouped_sdr = df_pre.groupby('cluster', as_index=False)[mes_dados_sdr].mean()
                    df_camp_grouped_sdr = df_camp.groupby('cluster', as_index=False)[mes_dados_sdr].mean()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_cluster_pre = px.bar(
                            df_pre_grouped_sdr.sort_values(mes_dados_sdr, ascending=False),
                            x='cluster',
                            y=mes_dados_sdr,
                            color='cluster',
                            color_discrete_map=CLUSTER_COLORS,
                            title=f'Média Atingimento SDR por Cluster - {mes_pre}',
                            labels={mes_dados_sdr: f'Média {mes_dados_sdr}', 'cluster': 'Cluster'},
                            text= mes_dados_sdr
                        )
                        fig_cluster_pre.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        st.plotly_chart(fig_cluster_pre, use_container_width=True, key=f"sdr_cluster_pre_{mes_pre}")
                    
                    with col2:
                        fig_cluster_camp = px.bar(
                            df_camp_grouped_sdr.sort_values(mes_dados_sdr, ascending=False),
                            x='cluster',
                            y=mes_dados_sdr,
                            color='cluster',
                            color_discrete_map=CLUSTER_COLORS,
                            title=f'Média Atingimento SDR por Cluster - {mes_camp}',
                            labels={mes_dados_sdr: f'Média {mes_dados_sdr}', 'cluster': 'Cluster'},
                            text= mes_dados_sdr
                        )
                        fig_cluster_camp.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        st.plotly_chart(fig_cluster_camp, use_container_width=True, key=f"sdr_cluster_camp_{mes_camp}")
                        
                    st.subheader("🎈Analise Geral da campanhas SDR", divider='blue')#analise com grafico e linhas.........
                    import altair as alt
                    #dados metas
                    dados_canais = {
                    "Canais": ["Franquias"],
                    "Agosto": [0.79],
                    "Setembro": [0.80], 
                    "Outubro": [0.68],
                    "Novembro": [0.73],
                    "Dezembro": [0.72],
                    "Janeiro": [0.82],
                    }
                    
                    df_metas = pd.DataFrame(dados_canais).set_index("Canais").T
                    df_metas.index.name = 'mês'
                    df_metas.reset_index(inplace=True)
                    df_metas.columns = ['mês', 'franquias']

                    meta_franquia_pre = df_metas.loc[df_metas['mês'] == mes_pre, 'franquias'].values[0]
                    meta_franquia_camp = df_metas.loc[df_metas['mês'] == mes_camp, 'franquias'].values[0]
                    
                    meses_analise = ["Agosto", "Setembro", "Outubro", "Novembro", "Dezembro", "Janeiro"]
                    
                    dados_grafico = []
                    for mes in meses_analise:
                        try:
                            df = pd.read_excel(file_sdr, sheet_name=mes)
                            df.columns = df.columns.str.strip().str.lower()
                            
                            franquia_valor = df_metas.loc[df_metas['mês'] == mes, 'franquias'].values[0]
                            
                            dados_grafico.append({
                            "Mês": mes,
                            "Tarefas SDRs": df['tarefas sdr'].mean(),
                            "Franquias": franquia_valor * 100  # Convertendo para porcentagem (1.0 = 100%)
                        })
                        except Exception as e:
                            st.warning(f"Erro ao processar mês {mes}: {e}")
                        df_plot = pd.DataFrame(dados_grafico)
                    
                        # Calcular variações mensais
                        df_plot['Variação Tarefas'] = df_plot['Tarefas SDRs'].diff().fillna(0)
                        df_plot['Variação Franquias'] = df_plot['Franquias'].diff().fillna(0)

                        # Formatando os textos
                        df_plot['Texto tarefas sdr'] = df_plot.apply(
                        lambda x: f"{x['Tarefas SDRs']:.0f} ({x['Variação Tarefas']:+.0f})", axis=1
                        )

                        df_plot['Texto Franquias'] = df_plot.apply(
                        lambda x: f"{x['Franquias']/100:.0%} ({x['Variação Franquias']/100:+.0%})", axis=1
                        )

                    
                    base = alt.Chart(df_plot).encode(
                    x=alt.X('Mês:N', sort=meses_analise, title='Mês', axis=alt.Axis(labelAngle=0))
                    )

                    # TAREFAS SDR - Barras (eixo esquerdo)
                    left_axis = alt.Axis(title='Tarefas SDR', titleColor='#1f77b4', titleFontWeight='bold')
                    bars = base.mark_bar(color='#1f77b4',
                                         size=80,
                                         cornerRadiusTopRight=8,
                                         cornerRadiusTopLeft=8,
                                         opacity=0.5).encode(
                        y=alt.Y('Tarefas SDRs:Q', axis=left_axis),
                        tooltip=['Mês', alt.Tooltip('Tarefas SDRs:Q', title='Tarefas SDRs'), 
                                alt.Tooltip('Tarefas SDRs:Q', title='Variação NMRR (R$)')]
                    )
                    
                    # Franquias - Linha tracejada (eixo direito)
                    right_axis = alt.Axis(title='Meta Franquias (%)', titleColor='#ff7f0e', 
                                        orient='right', titleFontWeight='bold', 
                                        titlePadding=50)
                    
                    line_franquias = base.mark_line(point=True,
                                                    color='#ff7f0e',
                                                    strokeWidth=2,
                                                    interpolate='monotone',
                                                    strokeDash=[3,3]).encode(
                        y=alt.Y('Franquias:Q', axis=right_axis),
                        tooltip=['Mês', alt.Tooltip('Franquias:Q', title='Franquias', format='.0%'),
                                alt.Tooltip('Variação Franquias:Q', title='Variação Franquias', format='+.0%')]
                    )
                    
                    # Textos com valores
                    texto_barras = base.mark_text(
                        align='center',
                        baseline='bottom',
                        dy=-5,
                        color='white',
                        lineHeight=15,
                        fontSize=13,
                        fontWeight='bold').encode(
                        text=alt.Text('Tarefas SDRs:Q', format=',.2f'),
                        y='Tarefas SDRs:Q'
                    )
                
                    texto_franquias = base.mark_text(
                        align='center',
                        baseline='bottom',
                        dy=-5,
                        color='#ff7f0e',
                        lineHeight=15,
                        fontSize=13,
                        fontWeight='bold',
                        ).encode(
                        text='Texto Franquias:N',
                        y='Franquias:Q'
                    ) 
                
                # Combinar os gráficos (apenas NMRR e Franquias)
                    chart = alt.layer(
                    bars + texto_barras,
                    line_franquias + texto_franquias
                    ).resolve_scale(
                    y='independent'
                    ).properties(
                    width=700,
                    height=450,
                    title='Desempenho SDR: Tarefas vs Meta Franquias'
                    ).configure_axis(
                    grid=False
                    ).configure_view(
                    strokeOpacity=0
                    )

                    st.altair_chart(chart, use_container_width=True)  
                        
            with tab4:  # Aba de Mecânica da Análise
                st.title("🔍 Mecânica da Análise")
    
                metodologia_tab, interpretacao_tab, guia_por_funcao, glossario_tab = st.tabs(
                    ["📋 Metodologia", "📊 Guia de Gráficos", "👥 Por Função", "📚 Glossário"]
                )
                
                with metodologia_tab:
                    st.header("Fluxo da Análise", divider="blue")
                    
                    with st.expander("🔎 Coleta de Dados", expanded=True):
                        cols = st.columns(1)
                        
                    with cols[0]:
                            st.markdown("""
                            **Períodos analisados:**
                            - Pré-campanha: Agosto a Outubro
                            - Campanha: Novembro a Janeiro
                            """)
                    
                    with st.expander("⚙️ Processamento", expanded=True):
                                                
                        # Tabela de classificação
                        st.markdown("**Classificação por Tempo de Casa:**")
                        classif_df = pd.DataFrame([
                            {
                                "Classificação": k, 
                                "Faixa (dias)": f"{v['range'][0]}-{v['range'][1]}", 
                                "Cor": f"<span style='color:{v['color']}'>■</span>"
                            } for k, v in CLASSIFICACAO.items()
                        ])
                        st.write(classif_df.to_html(escape=False), unsafe_allow_html=True)
                
                with interpretacao_tab:
                    st.header("Como Interpretar os Gráficos", divider="green")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **📊 Elementos Comuns:**
                        - **Eixo X:** Tempo de casa (dias)
                        - **Eixo Y:** Métrica específica da função
                        - **Cores:** Cluster/Experiência
                        - **Linha vermelha:** Meta esperada
                        
                        **Cores dos Clusters:**
                        - Ultra: Azul
                        - Diamante: Laranja
                        - Platina: Verde
                        - Ouro: Vermelho
                        """)
                    
                    with col2:
                        st.markdown("""
                        **🔍 O Que Procurar:**
                        1. Agrupamentos por tempo de casa
                        2. Outliers (alto/baixo desempenho)
                        3. Diferenças pré vs durante campanha
                        4. Consistência por cluster
                        """)
                
                with guia_por_funcao:
                    st.header("Guia por Função", divider="violet")
                    
                    with st.expander("🏢 EC - Executivo Comercial", expanded=True):
                        st.markdown("""
                        **Métricas Principais:**
                        - Reuniões úteis/dia (meta: 3.0)
                        - NMRR gerado
                        
                        **Análise Recomendada:**
                        1. Verificar se veteranos (>2 anos) mantêm performance
                        2. Identificar novatos com rápido crescimento
                        3. Comparar clusters de performance similar
                        """)
                    
                    with st.expander("📞 EV - Executivo de Vendas", expanded=True):
                        st.markdown("""
                        **Métricas Principais:**
                        - Atingimento % da meta individual
                        - NMRR absoluto gerado
                        
                        **Análise Recomendada:**
                        1. Relacionar tempo de casa com consistência
                        2. Identificar "top performers" por cluster
                        3. Analisar sazonalidade por mês
                        """)
                    
                    with st.expander("🎯 SDR - Sales Development", expanded=True):
                        st.markdown("""
                        **Métricas Principais:**
                        - Tarefas concluídas/semana
                        
                        **Análise Recomendada:**
                        1. Verificar curva de aprendizado (primeiros 3 meses)
                        2. Comparar desempenho por tipo de lead
                        3. Identificar melhores práticas por cluster
                        """)
                
                with glossario_tab:
                    st.header("Dicionário de Termos", divider="orange")
                    
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown("""
                        **Termos Gerais:**
                        - **NMRR:** New Monthly Recurring Revenue
                        - **Cluster:** Grupo de performance
                        - **Dias:** Tempo na empresa
                        
                        **Métricas de EC:**
                        - **Reu_util:** Reuniões úteis/dia
                        - **Ating_Reunião:** % da meta diária
                        """)
                    
                    with cols[1]:
                        st.markdown("""
                        **Métricas de EV:**
                        - **Ating_EV:** % meta individual
                        - **NMRR_EV:** Valor absoluto
                        
                        **Métricas de SDR:**
                        - **Atig_SDR:** % de tarefas concluídas
                        - **Tarefas SDR:** Tarefas de reunião. 
                        """)
                            #-verificar com pablito isso. kkkk
                            
                        
