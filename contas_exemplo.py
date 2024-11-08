import requests
import os
from pymongo import MongoClient

# Função para consultar contas da Enel usando a API da Infosimples
def consultar_contas_enel(login_email, login_senha, instalacao, token, timeout=300):
    """
    Realiza a consulta das contas de energia da Enel via API da Infosimples.
    """
    url = 'https://api.infosimples.com/api/v2/consultas/contas/enel/sp/download'
    args = {
        "login_email": login_email,
        "login_senha": login_senha,
        "instalacao": instalacao,
        "token": token,
        "timeout": timeout
    }
    
    try:
        response = requests.post(url, data=args, verify=False)
        response_json = response.json()
        response.close()
        return response_json
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
        return None

# Função para exibir o resultado da consulta de forma organizada
def exibir_resultado(response_json):
    """
    Exibe o resultado da consulta de forma estruturada e amigável.
    """
    if response_json is None:
        print("Nenhuma resposta recebida.")
        return
    
    if response_json.get('code') == 200:
        print("Retorno com sucesso:")
        for conta in response_json['data'][0]['contas']:
            print("\nConta:")
            print(f" - Valor: {conta['valor']}")
            print(f" - Status: {conta['status']}")
            print(f" - Mês de Referência: {conta['mes_referencia']}")
            print(f" - Vencimento: {conta['vencimento']}")
            print(f" - Código de Barras: {conta['codigo_barras']}")
            print(f" - PDF da Conta: {conta['conta_pdf_url']}")
    elif response_json['code'] in range(600, 799):
        print("Resultado sem sucesso:")
        print(f"Código: {response_json['code']} ({response_json['code_message']})")
        print("Erros:", "; ".join(response_json['errors']))
    
    print("\nCabeçalho da consulta:")
    for key, value in response_json['header'].items():
        print(f" - {key}: {value}")
    
    print("\nURLs com arquivos de visualização (HTML/PDF):")
    for url in response_json['site_receipts']:
        print(f" - {url}")

# Configurar o cliente do MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["contas"]
collection = db["contas_energia"]

# Função para inserir o JSON no MongoDB
def inserir_dados_mongo(response_json):
    """
    Insere dados relevantes no MongoDB.
    """
    try:
        collection.insert_one(response_json)
        print("Dados inseridos com sucesso no MongoDB!")
    except Exception as e:
        print("Erro ao inserir no MongoDB:", e)

# Configurações e execução
if __name__ == "__main__":
    # Configurações dos parâmetros, use variáveis de ambiente para segurança
    login_email = os.getenv("ENEL_LOGIN_EMAIL", "ronaldooliveira82@hotmail.com")
    login_senha = os.getenv("ENEL_LOGIN_SENHA", "Le140724@")
    instalacao = "0126175314"
    token = os.getenv("INFOSIMPLES_TOKEN", "FPv41P4tUPjwcy4Lm7awfOLwL70TEY7e_wRXLm-4")

    # Executando a consulta e exibindo o resultado
    response_json = consultar_contas_enel(login_email, login_senha, instalacao, token)
    exibir_resultado(response_json)

    # Inserindo os dados no MongoDB
    if response_json and response_json.get('code') == 200:
        inserir_dados_mongo(response_json)