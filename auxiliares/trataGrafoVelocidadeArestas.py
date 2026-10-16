import osmnx as ox
from descomprime_grafo import descomprime_grafo
descomprime_grafo()
grafo = ox.load_graphml("data/grafo_bh.graphml")
ox.routing.add_edge_speeds(grafo)

soma_velocidades = 0
i = 0
for _,_,_, dados in grafo.edges(keys=True, data=True):
    valor = dados.get("maxspeed")
    if valor is not None:
        velocidade = 0
        # As vezes max_speed pode ser uma lista (acho que e tipo caminhao e carro, entao vou pegar a media aqui)
        if isinstance(valor, list):
            for v in valor:
                velocidade += float(v)
            velocidade = velocidade/len(valor)
            soma_velocidades += float(velocidade)
        else:
            soma_velocidades += float(valor)
        i= i+1
velocidade_media = soma_velocidades / i

for _,_,_, dados in grafo.edges(keys=True, data=True):
    valor = dados.get("maxspeed")
    if valor is None:
        dados["maxspeed"] = velocidade_media
ox.routing.add_edge_speeds(grafo)
ox.routing.add_edge_travel_times(grafo)
ox.io.save_graphml(grafo, "data/grafo_bh.graphml")