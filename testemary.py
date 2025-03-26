import pandas as pd
import streamlit as st

# Criando o DataFrame com os dados originais + novos dados
data = {
    "Label": [
        "Acessar portal : / login - 18",
        "Login usuario : Realizar Pedido",
        "Navegar pelo showroom : Realizar Pedido",
        "Realizar Pedido",  # Novo dado (antigo "Controlador de Transação")
        "TOTAL"
    ],
    "# Samples": [213, 213, 213, 213, 852],
    "Average (ms)": [6570, 51608, 95108, 128690, 71094],
    "Median (ms)": [6224, 60033, 92673, 131328, 72641],
    "90% Line (ms)": [7133, 64030, 118463, 140443, 104018],
    "95% Line (ms)": [7467, 65067, 145705, 141203, 112334],
    "99% Line (ms)": [22325, 70983, 189298, 142945, 156201],
    "Min (ms)": [4581, 15835, 45422, 93415, 4581],
    "Maximum (ms)": [22478, 192229, 189977, 142987, 192229],
    "Error %": [0.0, 100.0, 100.0, 100.0, 80.0],
    "Throughput (/sec)": [9.3, 1.1, 1.1, 1.5, 3.25],
    "Received KB/sec": [127.18, 23.58, 2677.59, 835.54, 915.72],
    "Sent KB/sec": [6.72, 37.35, 139.18, 243.28, 106.63]
}

df = pd.DataFrame(data)

# Configuração do Streamlit
st.title("Análise de Performance - Teste de Carga")
st.markdown("### Métricas de Tempo de Resposta e Erros")

# Exibindo o DataFrame
st.dataframe(df.style.format({
    "Average (ms)": "{:,.0f}",
    "Median (ms)": "{:,.0f}",
    "90% Line (ms)": "{:,.0f}",
    "Error %": "{:.2f}%"
}), height=250)

# Análise
st.header("Principais Insights")
st.subheader("🔴 Problemas Críticos:")
st.markdown("""
1. **Taxa de Erro Alarmante**:  
   - Login, Navegação e Realizar Pedido têm **100% de falhas**.
   - Sistema completamente inoperante para funções críticas sob carga.

2. **Lentidão Extrema**:  
   - Operação de Realizar Pedido leva **128s em média** (pico de 142s).  
   - 90% das transações totais demoram mais de **104 segundos**.
""")

st.subheader("📊 Métricas Chave:")
col1, col2, col3 = st.columns(3)
col1.metric("Throughput Total", "3.25 req/seg", delta="-72% vs esperado")
col2.metric("Erro Total", "80%", delta_color="inverse")
col3.metric("Pior Tempo", "192.2s", delta="+620% do aceitável")

st.subheader("🛠 Recomendações:")
st.markdown("""
- **Priorizar Correção de Erros**:  
  Foco imediato em "Realizar Pedido" (função crítica para negócio).  
- **Otimização de Banco de Dados**:  
  Todos os tempos acima de 100s sugerem problemas graves de queries/índices.  
""")
# [...] (código anterior mantido igual até a seção de legenda)

# Seção de Legenda KPIs (completa e explicativa)
st.header("📖 Legenda Detalhada dos Indicadores")
st.markdown("""
###  Explicação Técnica de Cada Métrica:

| Coluna/Métrica       | O Que Mede?                                                                 | Exemplo Prático                          | Valores Ideais            |
|----------------------|----------------------------------------------------------------------------|-----------------------------------------|---------------------------|
| **Label**           | Nome da transação/teste realizado                                         | "Realizar Pedido"                       | -                         |
| **# Samples**       | Quantidade total de requisições executadas                                | 213 = 213 tentativas de login           | Quanto maior, mais significativo |
| **Average (ms)**    | Tempo médio de resposta da transação                                      | 128690ms = ~2 minutos por pedido        | < 2000ms (2 segundos)     |
| **Median (ms)**     | Valor que divide os tempos em duas partes iguais (50% acima/abaixo)       | 131328ms = Metade dos pedidos foi mais lento que isso | < 2000ms |
| **90% Line (ms)**   | 90% das requisições foram mais rápidas que este tempo                     | 140443ms = Apenas 10% foram piores      | < 4000ms (4 segundos)     |
| **Error %**         | Porcentagem de requisições que falharam                                   | 100% = Todas as tentativas de pedido falharam | < 1% (0.1% em sistemas críticos) |
| **Throughput (/sec)** | Capacidade do sistema em processar requisições por segundo               | 1.5/sec = 1.5 pedidos processados a cada segundo | > 10 req/s (depende do sistema) |
| **Received KB/sec** | Dados recebidos pelo servidor (ex: uploads de formulários) por segundo    | 835.54 KB/s = ~0.8 MB de dados recebidos a cada segundo | Monitorar picos anormais |
| **Sent KB/sec**     | Dados enviados pelo servidor (ex: imagens do catálogo) por segundo        | 243.28 KB/s = ~0.24 MB enviados por segundo | Monitorar picos anormais |

""")
# Seção: Referências Técnicas e Benchmarks
st.header("Por que esses números são ruins?")
st.markdown("""
### 🔍 **Critérios de Avaliação (Benchmarks)**  
Os parâmetros abaixo são baseados em padrões de mercado e melhores práticas de performance web:

| Métrica               | Aceitável (SaaS/Web) | Crítico               | Fonte                          |
|-----------------------|----------------------|-----------------------|--------------------------------|
| Tempo Médio (ms)      | < 2,000 ms          | > 5,000 ms           | [Google RAIL Model](https://web.dev/rail/) |
| Taxa de Erro          | < 1%                | > 5%                 | [SRE Book (Google)](https://sre.google/sre-book/service-level-objectives/) |
| Throughput (req/s)    | > 10 req/s          | < 2 req/s            | [JMeter Best Practices](https://jmeter.apache.org/usermanual/best-practices.html) |
| 90% Line (ms)         | < 4,000 ms          | > 10,000 ms          | [New Relic APM](https://newrelic.com/blog/how-to-relic/application-response-time) |
""")

st.subheader("**Problemas Identificados vs Benchmarks**")
st.markdown("""
1. **Tempo de Resposta (Showroom)**:
   - **95,108 ms (Médio)** vs **< 2,000 ms esperado**  
   → **47x mais lento** que o aceitável para operações críticas.

2. **Taxa de Erro (Login/Navegação)**:
   - **100% de falhas** vs **< 1% tolerado**  
   → Sistema **totalmente indisponível** sob carga.

3. **Throughput**:
   - **1.1 req/s** vs **> 10 req/s esperado**  
   → Capacidade **insuficiente** para uso real (ex: 50 usuários concorrentes exigiriam ~50 req/s).
""")

# [...] (restante do código mantido igual)