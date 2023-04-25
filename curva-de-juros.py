import pandas as pd
from bs4 import BeautifulSoup

# Caso apareça ao rodar que o SSL não é confiável.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from urllib.request import urlopen
url = urlopen('https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-ajustes-do-pregao-ptBR.asp')
soup = BeautifulSoup(url.read(), 'html.parser')

# pego a tabela de preços de ajuste da página
tabela = soup.find('table', id="tblDadosAjustes")

tr = soup.tbody.find_all('tr')

dados = []

for t in tr: 
    dados.append(t.text.split('\n'))
    
# converter em dataframe
df = pd.DataFrame(dados)

# Apagar as colunas desnecessárias
df.drop([0, 5, 6, 7], axis=1, inplace=True)
cabecalho = ('Contrato', 'Vencimento', 'AjusteAnterior', 'AjusteAtual')
df.columns = cabecalho
df.reset_index()

# Pega localização dos contratos no dataframe
inicioDDI = df[df['Contrato'].str.contains('DDI')].index[0]
inicioDI1 = df[df['Contrato'].str.contains('DI1')].index[0]
inicioDOL = df[df['Contrato'].str.contains('DOL')].index[0]

# Cria 2 dataframes: um DDI (Cupom Cambial) e um DI1 (DI Diário)
dfDDI = df.iloc[inicioDDI:inicioDI1].copy()
dfDDI.rename(
    columns = {
        'AjusteAnterior': 'AjAntDDI',
        'AjusteAtual': 'AjAtualDDI', 
    }, 
    inplace = True
)

dfDI1 = df.iloc[inicioDI1:inicioDOL].copy()
dfDI1.rename(
    columns = {
        'AjusteAnterior': 'AjAntDI1',
        'AjusteAtual': 'AjAtualDI1', 
    }, 
    inplace = True
)

# Cria novo dataframe que juntará os dois
dfDDIDI1 = dfDDI.merge(
    dfDI1[['Vencimento', 'AjAntDI1', 'AjAtualDI1']], 
    on='Vencimento', 
    how='right'
)

# Apaga nome da coluna Contrato no DDIDI1
dfDDIDI1.drop('Contrato', axis = 1, inplace = True)

# Transformar as strings em números para o Excel (. => ,)
dfDDIDI1 = dfDDIDI1.replace('\.', '', regex = True)
dfDDIDI1 = dfDDIDI1.replace(',', '.', regex = True)
dfDDIDI1[['AjAntDDI', 'AjAtualDDI', 'AjAntDI1', 'AjAtualDI1']] = dfDDIDI1[['AjAntDDI', 'AjAtualDDI', 'AjAntDI1', 'AjAtualDI1']].apply(pd.to_numeric)

# Grava o dataframe como Planilha Excel
dfDDIDI1.to_excel('', sheet_name = 'dados')

