import osmnx as ox

def tempoEntrega(entregador, restaurante, grafo):
    vertice_entregador, vertice_restaurante = ox.distance.nearest_nodes(grafo, X=[entregador[1], restaurante["longitude"]], Y=[entregador[0], restaurante["latitude"]])
    caminho = ox.routing.shortest_path(grafo, vertice_entregador, vertice_restaurante, weight="travel_time")
    print(vertice_entregador)
    if caminho is None:
        return None

    arestas_do_caminho = ox.routing.route_to_gdf(grafo, caminho, weight="travel_time")
    tempo_total_segundos = arestas_do_caminho["travel_time"].sum()
    
    return tempo_total_segundos
def tempoEntregas(entregadores, restaurante, grafo):
    X = [entregador[1] for entregador in entregadores] + [restaurante["longitude"]]
    Y = [entregador[0] for entregador in entregadores] + [restaurante["latitude"]]
    vertices = ox.distance.nearest_nodes(grafo, X=X, Y=Y)
    num_entregadores = len(entregadores)
    restaurantes = [vertices[num_entregadores] for i in range(num_entregadores)]
    caminhos = ox.routing.shortest_path(grafo, vertices[:num_entregadores], restaurantes, weight="travel_time")
    tempo_total_segundos = []
    if caminhos is None:
        return None
    for caminho in caminhos:
        arestas_do_caminho = ox.routing.route_to_gdf(grafo, caminho, weight="travel_time")
        tempo_total_segundos.append(arestas_do_caminho["travel_time"].sum())
    
    return tempo_total_segundos