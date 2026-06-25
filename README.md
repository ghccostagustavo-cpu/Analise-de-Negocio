# Análise de Testes A/B
Ferramenta para análise automatizada de testes A/B de cashback, com interface Streamlit e IA local via Ollama.

## Pré-requisitos

- Python 3.9+
- [Ollama](https://ollama.com) instalado e rodando

## Instalação

```bash
pip install streamlit pandas requests gspread google-auth
ollama pull llama3.2:8b
```

## Como rodar

```bash
streamlit run app.py
```

Acesse `http://localhost:8501`, suba um dos CSVs e faça sua pergunta.

## Lógica de negócio

**Receita Líquida = Comissão − Cashback**

O grupo vencedor é o que maximiza a receita líquida total acumulada no período do teste.

## Google Sheets

A função `salvar_sheets()` já está estruturada no código. Para ativar:

1. Criar projeto no [Google Cloud Console](https://console.cloud.google.com)
2. Ativar a API do Google Sheets
3. Criar uma Service Account e baixar o as credenciais em json na raiz do projeto
4. Compartilhar a planilha com o email da Service Account
5. Substituir `"ID_DA_SUA_PLANILHA"` no código pelo ID real

Sem essa configuração, basta trocar `salvar_sheets(linha)` pelo trecho comentado no código que grava em `historico.csv` localmente.

## Por que IA local?

Os dados dos parceiros (comissões, vendas) são confidenciais. O Ollama roda offline e nenhum dado é enviado para servidores externos.