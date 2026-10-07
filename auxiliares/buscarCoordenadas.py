import csv
import os

import osmnx as ox
from shapely.geometry import Point

ox.settings.http_user_agent = "TP1 Algoritmos2 UFMG (raissalgns@ufmg.br)"
ox.settings.use_cache = True

arquivo_entrada = "../data/bares.csv"
arquivo_saida = "../data/bares_com_coordenadas.csv"
cidade = "Belo Horizonte, Minas Gerais, Brasil"
dicionario = {
    "AVE": "Avenida", 
    "ALA": "Alameda", 
    "BEC": "Beco", 
    "EST": "Estrada", 
    "PCA": "Praça", 
    "LGO": "Largo", 
    "ROD": "Rodovia", 
    "PRC": "Praça",
    "TRV": "Travessa",
    "VIA": "Via",
}

# Cria as diferentes consultas possíveis para cada linha do arquivo de entrada
def formar_consulta(linha):
    descricao_abreviada = linha["DESC_LOGRADOURO"].strip()
    descricao = dicionario.get(descricao_abreviada, descricao_abreviada.title())
    rua = linha["NOME_LOGRADOURO"].strip().title()
    numero = linha["NUMERO_IMOVEL"].strip()
    bairro = linha["NOME_BAIRRO"].strip().title()
    lista = []
    if numero and numero not in ("0", "S/N", "SN"):
        lista.append(f"{descricao} {rua}, {numero}, {bairro}, {cidade}")
        lista.append(f"{descricao} {rua}, {numero}, {cidade}")
    lista.append(f"{descricao} {rua}, {bairro}, {cidade}")
    return lista

# Tenta gerar a latitude e longitude para cada linha do arquivo de entrada
def tentar_consultas(linha, delimitacao_bh):
    for consulta in formar_consulta(linha):
        try:
            latitude, longitude = ox.geocode(consulta)
        except Exception:
            continue
        if delimitacao_bh.contains(Point(longitude, latitude)):
            return latitude, longitude
    return None, None


if __name__ == "__main__":
    with open(arquivo_entrada, newline="", encoding="utf-8") as f:
        leitor_arquivo = csv.DictReader(f)
        colunas = leitor_arquivo.fieldnames
        linhas = list(leitor_arquivo)

    if os.path.exists(arquivo_saida):
        with open(arquivo_saida, newline="", encoding="utf-8") as f:
            feitos = {l["_id"] for l in csv.DictReader(f)}

    feitos = set() 
    delimitacao_bh = ox.geocode_to_gdf(cidade).geometry.iloc[0]

    with open(arquivo_saida, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas + ["latitude", "longitude"])
        if not os.path.exists(arquivo_saida):
            escritor.writeheader()
        for linha in linhas:
            if linha["_id"] in feitos:
                continue
            latitude, longitude = tentar_consultas(linha, delimitacao_bh)
            linha["latitude"] = latitude
            linha["longitude"] = longitude
            print(f"Processado: {linha['_id']} - Latitude: {latitude}, Longitude: {longitude}")
            escritor.writerow(linha)
            f.flush()