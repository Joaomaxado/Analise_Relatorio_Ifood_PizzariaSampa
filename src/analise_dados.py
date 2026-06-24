import pandas as pd
from .cleaning import tratamento_dados

def analise():
    df = tratamento_dados()
    df_cancelados = df[df['STATUS FINAL DO PEDIDO'].str.upper().str.contains('CANCELADO', na=False)]
    motivo_cancelamento = df_cancelados['MOTIVO DO CANCELAMENTO'].value_counts()
    solicitacao_atraso = df[df['CLIENTE SOLICITOU NOVA PREVISÃO DE ENTREGA DEVIDO ATRASO (LOGÍSTICA PRÓPRIA)'].str.upper().str.contains('SIM', na=False)]
    media_espera_cliente = df['TEMPO DO ENTREGADOR ESPERANDO NO CLIENTE (MIN)'].mean()
    mediana_espera_cliente = df['TEMPO DO ENTREGADOR ESPERANDO NO CLIENTE (MIN)'].median()
    analise_tempo_por_motivos = df_cancelados.groupby('MOTIVO DO CANCELAMENTO')['TEMPO DO ENTREGADOR ESPERANDO NO CLIENTE (MIN)'].describe()

    # Cliente não localizado                              4
    # O pedido veio com todos os itens errados            3
    # Pedido cancelado por atraso com alerta para loja    3
    # O pedido não foi entregue                           2
    # O pedido está atrasado                              1
    # Faltou inserir informações no pedido                1
    # Pedido impróprio para consumo/uso                   1

    # Faturamento Bruto
    df['TOTAL PAGO PELO CLIENTE (R$)'] = pd.to_numeric(df['TOTAL PAGO PELO CLIENTE (R$)'])
    faturamento_bruto = df['TOTAL PAGO PELO CLIENTE (R$)'].sum()

    # Faturamento líquido
    df['VALOR LIQUIDO (R$)'] = pd.to_numeric(df['VALOR LIQUIDO (R$)'])
    faturamento_liquido = df['VALOR LIQUIDO (R$)'].sum()

    # Valor pago em taxas
    df['TAXAS E COMISSOES (R$)'] = pd.to_numeric(df['TAXAS E COMISSOES (R$)'])
    taxas = df['TAXAS E COMISSOES (R$)'].sum()

    # Formas de pagamento 
    pagamento = df['FORMA DE PAGAMENTO'].value_counts()
    return df, faturamento_bruto, faturamento_liquido, taxas, pagamento, df_cancelados, motivo_cancelamento, analise_tempo_por_motivos, solicitacao_atraso