import pandas as pd
def busca_coordenadas_bar(id_bar):
    bares = pd.read_csv("data/bares_com_coordenadas.csv", dtype=str, keep_default_na=False)
    bar = bares[bares["_id"] == id_bar]
    if bar.empty:
        print("Não encontramos o bar com esse id")
    else:
        latitude = bar.iloc[0]['latitude']
        longitude = bar.iloc[0]['longitude']
        return latitude, longitude
