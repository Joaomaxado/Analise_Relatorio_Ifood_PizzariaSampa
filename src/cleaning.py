import pandas as pd
from .extration import extration

def tratamento_dados():
    df = extration()
    df = df.drop(columns=['ID COMPLETO DO PEDIDO', 'ID DA LOJA', 'ID CURTO DO PEDIDO', 'ORIGEM DA NEGOCIAÇÃO NO PREPARO'
    , 'TIPO DE NEGOCIAÇÃO NO PREPARO', 'DATA DE AGENDAMENTO'])
    df = df.loc[:, (df != '').any(axis=0)]
    df = df.fillna(0)
    df['DATA E HORA DO PEDIDO'] = pd.to_datetime(df['DATA E HORA DO PEDIDO'], dayfirst=True, errors='coerce')
    df['DATA DO CANCELAMENTO'] = pd.to_datetime(df['DATA DO CANCELAMENTO'], dayfirst=True, errors='coerce')

    colunas_texto = df.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        df[col] = df[col].fillna('Não informado')
    df.fillna(0)
    return df