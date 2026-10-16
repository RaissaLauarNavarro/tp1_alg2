import osmnx as ox

def tempoEntrega(entregador, restaurante, grafo):
    vertice_entregador, vertice_restaurante = ox.distance.nearest_nodes(grafo, X=[entregador.longitude, restaurante.longitude], Y=[entregador.latitude, restaurante.latitude])
    caminho = ox.routing.shortest_path(grafo, vertice_entregador, vertice_restaurante, weight="travel_time")

    if caminho is None:
        return None

    arestas_do_caminho = ox.routing.route_to_gdf(grafo, caminho, weight="travel_time")
    tempo_total_segundos = arestas_do_caminho["travel_time"].sum()
    
    return tempo_total_segundos