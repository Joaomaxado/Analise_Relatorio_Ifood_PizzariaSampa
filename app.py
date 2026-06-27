import streamlit as st
import pandas as pd
import plotly.express as px
from src.analise_dados import analise
import datetime

# 1. Configuração da página DEVE ser o primeiro comando Streamlit
st.set_page_config('Dashboard Pizzaria', layout="wide")

st.title('Dashboard Financeiro Sampa')

# Executa o pipeline de dados
df, faturamento_bruto, faturamento_liquido, taxas, analise_tempo_por_motivos = analise()

# Garante que a coluna de data é datetime no app
df['DATA E HORA DO PEDIDO'] = pd.to_datetime(df['DATA E HORA DO PEDIDO'], errors='coerce')

# --- SIDEBAR COM FILTROS ---
st.sidebar.subheader('Filtrar por período')
data_inicial = datetime.date(2026, 4, 25)
data_final = datetime.date(2026, 5, 24)

periodo = st.sidebar.date_input(
    'Selecione o intervalo de datas:',
    value=(data_inicial, data_final),
    min_value=data_inicial,
    max_value=data_final          
)

st.sidebar.markdown('---')
st.sidebar.subheader('Navegação')
aba_selecionada = st.sidebar.radio(
    'Ir para aba:',
    ["📊 Métricas", "⏱️ Análise de Cancelamentos", "💡 Soluções Estratégicas"]
)

# --- APLICAÇÃO DO FILTRO CORRIGIDA (Preste atenção nas variáveis) ---
if isinstance(periodo, tuple) and len(periodo) == 2:
    data_inicio, data_fim = periodo  # Correção da digitação (de inico para inicio)
    df_filtrado = df[
        (df['DATA E HORA DO PEDIDO'].dt.date >= data_inicio) &  # Correção aqui: trocado data_inicial por data_inicio
        (df['DATA E HORA DO PEDIDO'].dt.date <= data_fim)
    ]
else:
    df_filtrado = df

# Recalcula os agregados com base no df_filtrado
fat_bruto_filtrado = df_filtrado['TOTAL PAGO PELO CLIENTE (R$)'].sum()
fat_liquido_filtrado = df_filtrado['VALOR LIQUIDO (R$)'].sum()
taxas_filtradas = df_filtrado['TAXAS E COMISSOES (R$)'].sum()
df_cancelados_filtrado = df_filtrado[df_filtrado['STATUS FINAL DO PEDIDO'].str.upper().str.contains('CANCELADO', na=False)]

# --- RENDERIZAÇÃO DAS ABAS ---

# ================= ABA 1: MÉTRICAS =================
if aba_selecionada == "📊 Métricas":    
    st.markdown("---")
    
    # Criando as colunas de métricas dentro da aba para melhor visualização
    col1, col2, col3 = st.columns(3)
    
    with col1: 
        # Correção aqui: Trocado faturamento_bruto por fat_bruto_filtrado
        st.metric(label='Faturamento Bruto', value=f'R$ {fat_bruto_filtrado:,.2f}')
    with col2: 
        # Correção aqui: Trocado faturamento_liquido por fat_liquido_filtrado
        st.metric(label='Líquido', value=f'R$ {fat_liquido_filtrado:,.2f}')
    with col3:
        # Correção aqui: Trocado taxas por taxas_filtradas
        st.metric(label='Taxas totais', value=f'R$ {taxas_filtradas:,.2f}')
    
    st.markdown("---")
    
    # Mostra a forma de pagamento mais comum baseada no período filtrado
    pagamento_filtrado = df_filtrado['FORMA DE PAGAMENTO'].value_counts() if 'FORMA DE PAGAMENTO' in df_filtrado.columns else []
    if len(pagamento_filtrado) > 0:
        forma_comum = pagamento_filtrado.index[0]
        st.metric(label="Principal Forma de Pagamento no Período", value=str(forma_comum))

    st.subheader("💳 Top 5 Formas de Pagamento (Faturamento)")
        
        # 1. Agrupa o faturamento por forma de pagamento
    df_pagamento = df_filtrado.groupby('FORMA DE PAGAMENTO')['TOTAL PAGO PELO CLIENTE (R$)'].sum().reset_index()
    df_pagamento.columns = ['FORMA DE PAGAMENTO', 'TOTAL PAGO PELO CLIENTE (R$)']
        
        # 2. FILTRO TOP 5: Mantém apenas as 5 maiores em valor financeiro
    df_pagamento_top5 = df_pagamento.nlargest(5, 'TOTAL PAGO PELO CLIENTE (R$)')

        # 3. Plota o gráfico limpo
    fig_pagamento = px.bar(
        df_pagamento_top5, 
        x='FORMA DE PAGAMENTO',
        y='TOTAL PAGO PELO CLIENTE (R$)',
        color='TOTAL PAGO PELO CLIENTE (R$)',
        color_continuous_scale='Blues',
        text_auto='R$ .2s',
        use_container_width=True  # Adiciona o prefixo de Real antes do valor resumido (ex: R$ 52k)
        )
    fig_pagamento.update_layout(template='plotly_dark', showlegend=False)
    st.plotly_chart(fig_pagamento, use_container_width=True)
        
    # Gráfico de Linha de Tendência 
    df_filtrado['Data_Dia'] = df_filtrado['DATA E HORA DO PEDIDO'].dt.date
    df_linha = df_filtrado.groupby('Data_Dia')['TOTAL PAGO PELO CLIENTE (R$)'].sum().reset_index()
    df_linha.columns = ['Dia', 'Faturamento Bruto (R$)']
    df_linha = df_linha.sort_values('Dia')


    st.subheader('Volume de Vendas')
    fig_linha = px.line(
        df_linha,
        x='Dia',
        y='Faturamento Bruto (R$)',
        markers=True,
        use_container_width=True
        )
    fig_linha.update_traces(line=dict(color='#FF4B4B', width=3), line_shape='spline')
    fig_linha.update_layout(template='plotly_dark')
    st.plotly_chart(fig_linha, use_container_width=True)

# ================= ABA 2: ANÁLISE DE CANCELAMENTOS =================
elif aba_selecionada == "⏱️ Análise de Cancelamentos":
    st.subheader('Motivos dos Cancelamentos')
    if len(df_cancelados_filtrado) > 0:
        df_motivos = df_cancelados_filtrado['MOTIVO DO CANCELAMENTO'].value_counts().reset_index()
        df_motivos.columns = ['Motivo', 'Quantidade']
        
        fig_cancelamento = px.bar(
            df_motivos, x='Quantidade', y='Motivo', orientation='h',
            color='Quantidade', color_continuous_scale='Reds'
        )
        fig_cancelamento.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
        st.plotly_chart(fig_cancelamento, use_container_width=True)
    else:
        st.info("Nenhum cancelamento registrado neste intervalo de tempo.")

    st.markdown("---")
    st.title("⏱️ Monitoramento Logístico")
    st.subheader("Métricas de Tempo e Gargalos de Entrega")
    
    col_atraso, col_tempo = st.columns(2)
    with col_atraso:
        col_atraso_nome = 'CLIENTE SOLICITOU NOVA PREVISÃO DE ENTREGA DEVIDO ATRASO (LOGÍSTICA PRÓPRIA)'
        if col_atraso_nome in df_filtrado.columns:
            alertas_atraso = df_filtrado[df_filtrado[col_atraso_nome].astype(str).str.upper().str.contains('SIM', na=False)]
            st.metric(label="Alertas de Atraso Acionados", value=len(alertas_atraso))
        else:
            st.metric(label="Alertas de Atraso Acionados", value=0)
    
    with col_tempo:
        col_espera = 'TEMPO DO ENTREGADOR ESPERANDO NO CLIENTE (MIN)'
        if col_espera in df_filtrado.columns:
            mediana_tempo = df_filtrado[df_filtrado[col_espera] > 0][col_espera].median()
            st.metric(label="Mediana de Espera na Calçada", value=f"{mediana_tempo:.1f} min" if not pd.isna(mediana_tempo) else "0.0 min")

    st.markdown("---")
    st.markdown("**Distribuição Estatística do Tempo por Motivo de Cancelamento:**")
    st.dataframe(analise_tempo_por_motivos, use_container_width=True)

# ================= ABA 3: SOLUÇÕES =================
elif aba_selecionada == "💡 Soluções Estratégicas":
    st.title("💡 Plano de Ação & Soluções")
    st.markdown("Análise baseada nos gargalos detectados no relatório atual.")
    
    st.info("### 🛑 Gargalo 1: Cliente Não Localizado")
    st.markdown("""
    * **Impacto:** É o principal motivo de cancelamento detectado no gráfico.
    * **Solução Proposta:** Implementar uma mensagem automatizada de WhatsApp via API assim que o motoboy sair para a entrega, forçando a confirmação do cliente de que há alguém para receber.
    """)
    
    st.warning("### ⏱️ Gargalo 2: Retenção de Motoboy na Calçada")
    st.markdown("""
    * **Impacto:** Motoboys perdendo tempo excessivo esperando o cliente descer.
    * **Solução Proposta:** Criar uma regra de velocidade e tolerância máxima de 5 minutos no cliente. Após esse tempo, o entregador fica autorizado a retornar com o pedido para a central para não quebrar a rota logística das próximas entregas.
    """)
    
st.markdown("---")