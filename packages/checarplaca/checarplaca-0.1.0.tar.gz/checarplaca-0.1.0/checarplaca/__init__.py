import requests
from bs4 import BeautifulSoup
import re

def checar_placa(placa: str) -> None:

    """
    Consulta e exibe os dados do veículo pela placa.

    Parâmetros:
    - placa (str): Placa do veículo (ex: 'AAA1A11' ou 'AAA1234')
    """

    placa = placa.strip().upper()

    # Validação de formato de placa (padrão antigo e Mercosul)
    if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", placa):
        print("[ERRO] Formato inválido. Use o formato 'AAA1234' ou 'AAA1A11'.")
        return

    url = f"https://www.ipvabr.com.br/placa/{placa}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        print("[ERRO] Não foi possível se conectar ao servidor.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    linhas = soup.select('table.tableIPVA tr')

    if not linhas:
        print("[ERRO] Placa não encontrada ou sem informações disponíveis.")
        return

    # Coleta e exibe os dados formatados
    dados = {}
    for linha in linhas:
        colunas = linha.find_all('td')
        if len(colunas) == 2:
            chave = colunas[0].get_text(strip=True).rstrip(':')
            valor = colunas[1].get_text(strip=True)
            dados[chave] = valor

    # Exibição formatada
    print("\n+============================================+")
    print(f"|   Dados encontrados para a placa {placa}   |")
    print("+============================================+")
    for chave, valor in dados.items():
        print(f"| {chave:<20}: {valor:<20} |")
    print("+============================================+\n")