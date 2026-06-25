import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

#Importação das bibliotecas necessárias. Importamos pandas para manusearmos os CSV's, Streamlit para termos uma interface interatica (sem ser terminal)
#O requests é pra operarmos com a IA local. A comunicação é na própria máquina, a IA local é para mantermos os dados dentro da empresa, não enviando pra modelos da Internet
#A biblioteca gspread e google.oauth2 são para a integração com o Google Sheets, onde vamos salvar o histórico de análises. 
#Gspread acessa a planilha e google.oauth2.service_account é a parte de autenticação

escopos = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
#Escopos das API's dp Google.

def consultar_ia(prompt, dados):
    #Criamos essa função de consulta de I.A. Os parâmetros são o prompt do usuário e os dados
    r = requests.post("http://localhost:11434/api/chat", json={
        #json com as descrições
        "model": "llama3.2:3b",
        #Definição do modelo. Este modelo com 3B de parâmetros é eficiente para o nosso caso
        "stream": False,
        "options": {"temperature": 0.1},
        #A temperatura significa exatidão. Quanto menor, mais exato. Quanto maior, mais criativo, mas abre margem pra alucinação. 
        #Para mexer com números, 0.1 é bom.
        "messages": [
            {"role": "system", "content":
                "Você é analista de growth."
                "Métrica principal: receita_liquida = comissão - cashback. "
                "Seja direto: diga o grupo vencedor e justifique em um texto analítico de até 5 linhas. "
                f"Dados:\n{dados}"},
            #Dados fornecidos
            {"role": "user", "content": prompt}
            #Prompt do usuário
        ]
    })
    return r.json()["message"]["content"]
    #Retorno no json

def salvar_sheets(linha_dict):
    #Função para salvar o resultado no Google Sheets. Requer credentials.json e ID da planilha configurados
    creds = Credentials.from_service_account_file(os.getenv("json_config"), scopes=escopos)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(os.getenv("chave_sheets")).sheet1
    #ID da planilha é a parte da URL entre /d/ e /edit
    sheet.append_row(list(linha_dict.values()))
    #Appenda uma nova linha com os valores do dicionário

st.title("Análise de Testes A/B")
#Título da interface Streamlit

def limpar(valor):
    return float(str(valor).replace("R$","").replace(".","").replace(",",".").strip())
#Função de limpeza do valor. A gente pega e trata o valor como string, tiramos os caracteres especiais, pontos e espaços (Fundamental termos o tratamento do valor como string antes)
#Após isso, temos uma string com o valor tratado. Transformamos em float. Volta a ser um número

arquivo = st.file_uploader("Forneça o CSV do teste", type="csv")
#Aqui a gente coloca na interface visual do Streamlit a opção de subir o CSV de teste. Definimos o tipo como "csv"

if arquivo:
    #Caso haja arquivo fornecido
    df_csv = pd.read_csv(arquivo)
    #Usamos a biblioteca Pandas para ler o csv e tratar como dataframe
    for col in ["comissão", "cashback", "vendas totais"]:
        #Repetição para aplicarmos a função de limpeza somente nas colunas de números
        df_csv[col] = df_csv[col].apply(limpar)
        #Aplicação da função de limpeza
    df_csv["receita_liquida"] = df_csv["comissão"] - df_csv["cashback"]
    #A coluna do dataframe "receita líquida" vai receber o valor da diferença da comissão e cashback

    resumo = df_csv.groupby("Grupos de usuários").agg(
        #Definimos o resumo como o que será retornado ao usuário
        #Usamos esses recursos da biblioteca pandas para voltarmos os dados para cada grupo de usuário. agg pra fazermos essas operações de somar compradores, comissão e cashback
        compradores=("compradores","sum"),
        #Soma de int compradores do grupo
        comissao=("comissão","sum"),
        #Soma do float comissão
        cashback=("cashback","sum"),
        #Soma do float cashback
        receita_liquida=("receita_liquida","sum")
        #Soma do float da receita
    ).reset_index()
    #Por padrão, a primeira coluna se torna o índice. Resetamos pra ser considerada como coluna novamente e podermos manusear o csv resultante

    st.subheader("Resumo por Grupo")
    #Subtítulo da interface Streamlit
    st.dataframe(resumo, use_container_width=True)
    #Joga a tabela csv numa interface visual no streamlit
    st.bar_chart(resumo.set_index("Grupos de usuários")["receita_liquida"])
    #Aqui temos um gráfico. Receita líquida por grupo de usuário. Outro recurso Streamlit

    pergunta = st.text_input("Pergunta para a IA:", "Qual grupo escalar para 100%? Por quê?")
    #Aqui definimos a instrução do que escrever no input visual

    if st.button("Analisar"):
        #Caso o botão de analisar, criado pelo Streamlit, seja acionado
        with st.spinner("Analisando..."):
            #Spinner é aquela roda de carregamento. Vai dar essa mensagem
            resposta = consultar_ia(pergunta, resumo.to_string(index=False))
            #Chamamos a função consultar_ia passando a pergunta e o resumo dos dados em texto
        st.write("Conclusão", resposta)

        parceiro = df_csv["Parceiro"].iloc[0]
        #Como numa consulta teremos um parceiro, pegamos a localização do primeiro para não precisar percorrer toda a coluna
        vencedor = resumo.loc[resumo["receita_liquida"].idxmax(), "Grupos de usuários"]
        #O vencedor é aquele onde a receita líquida seja a maior. Recurso da biblioteca pandas

        linha = {
            #Cada linha abaixo é uma coluna no Sheets
            #Estrutura exigida pelo case: nome do teste, descrição, resultado e decisão tomada
            "data": datetime.now().strftime("%d-%m-%Y %H:%M"),
            #Isso aqui funciona como um Log pra registrar data e hora
            "teste": parceiro,
            #Aqui a linha com o teste, o parceiro
            "resultado": f"{vencedor}: R$ {resumo['receita_liquida'].max():,.2f}",
            #Aqui o resultado com o vencedor e a receita líquida
            "decisao": resposta
            #Resposta da IA
        }
        salvar_sheets(linha)
        #Salva a linha no Google Sheets via gspread
        st.success("Salvo no Google Sheets.")
