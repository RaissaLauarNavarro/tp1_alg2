import gzip
import shutil

with open("../data/grafo_bh.graphml", "rb") as origem:
    with gzip.open(
        "grafo_bh.graphml.gz",
        "wb",
        compresslevel=9,
    ) as destino:
        shutil.copyfileobj(origem, destino)
