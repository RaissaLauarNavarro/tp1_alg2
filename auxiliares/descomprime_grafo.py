import gzip
import shutil

arquivo_comprimido = "data/grafo_bh.graphml.gz"
arquivo_descomprimido = "data/grafo_bh.graphml"
def descomprime_grafo():
    with gzip.open(arquivo_comprimido, "rb") as origem:
        with open(arquivo_descomprimido, "wb") as destino:
            shutil.copyfileobj(origem, destino)