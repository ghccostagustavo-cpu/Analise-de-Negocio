# Análise de Testes de Mercado

Ferramenta para análise automatizada de testes A/B de cashback, com interface Streamlit e IA local via Ollama.

## Pré-requisitos

- Python 3.9+
- [Ollama](https://ollama.com) instalado e rodando

## Instalação

```bash
pip install streamlit pandas requests gspread google-auth
ollama pull llama3.2:3b
#Caso opte por maior capacidade, 8 bilhões de parametros exige uma máquina um pouco melhor (um notebook atual com 8GB de RAM já basta):
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

A função `salvar_sheets()` usa API's da Google para acessar uma planilha do Google Sheets e armazenar os dados conforme cada execução do programa.

Sem essa configuração, basta tirar `salvar_sheets(linha)` e substituir para gravar em algum diretório do computador.  

## Por que IA local?

Os dados dos parceiros (comissões, vendas) são confidenciais. O Ollama roda offline e nenhum dado é enviado para servidores externos, por isso optei pelo uso dele. Uso diariamente o ollama no meu projeto de Analista de Dados por I.A (tudo também no meu GitHub) exatamente pela segurança da informação. O único gargalo de uma I.A local é o uso de hardware (RAM e VRAM), no entanto, ao usar uma I.A de 3B de parâmetros, o programa consegue rodar bem. Caso opte por capacidade de armazenamento, basta baixar a mesma I.A, porém com 8 bilhões ou mais de parâmetros.
