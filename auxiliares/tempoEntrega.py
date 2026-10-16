import osmnx as ox
from auxiliares.minHeap import MinHeap

def dijkstra(grafo, origem, destino, peso):
    fila_prioridade = MinHeap()
    fila_prioridade.push((0, origem))
    
    # predecessores é so pra conseguir reconstruir o caminho
    distancias = {origem: 0}
    predecessores = {origem: None}

    while not fila_prioridade.vazio():
        distancia_atual, vertice_atual = fila_prioridade.pop()

        if vertice_atual == destino:
            break

        if distancia_atual > distancias.get(vertice_atual, float('inf')):
            continue

        for vizinho in grafo.successors(vertice_atual):
            # Osmnx usa um multidigraph, então não tem necessariamente apenas uma aresta 
            # ligando dois vertices, então temos que escolher a melhor delas
            menor_peso = float('inf')
            
            for _, dados_aresta in grafo[vertice_atual][vizinho].items():
                peso_aresta = dados_aresta.get(peso, float('inf'))
                if peso_aresta < menor_peso:
                    menor_peso = peso_aresta

            if menor_peso == float('inf'):
                continue

            nova_distancia = distancia_atual + menor_peso

            if nova_distancia < distancias.get(vizinho, float('inf')):
                distancias[vizinho] = nova_distancia
                predecessores[vizinho] = vertice_atual
                fila_prioridade.push((nova_distancia, vizinho))

    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = predecessores.get(atual)

    return caminho[::-1]

def calculaTempoDistanciaCaminho(grafo, caminho):
    if not caminho or len(caminho) < 2:
        return 0, 0
        
    tempo_total = 0
    distancia_total = 0

    for i in range(len(caminho) - 1):
        u = caminho[i]
        v = caminho[i + 1]

        menor_peso = float('inf')
        comprimento_escolhido = 0

        for _, dados_aresta in grafo[u][v].items():
            peso_atual = dados_aresta.get("travel_time", float('inf'))
            if peso_atual < menor_peso:
                menor_peso = peso_atual
                comprimento_escolhido = dados_aresta.get("length", 0)

        if menor_peso != float('inf'):
            tempo_total += menor_peso
            distancia_total += comprimento_escolhido

    return tempo_total, distancia_total


def tempoEntregas(entregadores, restaurante, grafo):
    X = [entregador[1] for entregador in entregadores] + [restaurante["longitude"]]
    Y = [entregador[0] for entregador in entregadores] + [restaurante["latitude"]]
    
    vertices = ox.distance.nearest_nodes(grafo, X=X, Y=Y)
    num_entregadores = len(entregadores)
    vertice_restaurante = vertices[-1]
    vertices_entregadores = vertices[:num_entregadores]
    tempo_total_segundos = []
    distancias = []
    
    for vertice_entregador in vertices_entregadores:
        caminho = dijkstra(grafo, vertice_entregador, vertice_restaurante, "travel_time")
        
        if caminho is None:
            return None, None
        else:
            tempo, distancia = calculaTempoDistanciaCaminho(grafo, caminho)
            tempo_total_segundos.append(tempo)
            distancias.append(distancia)

    return tempo_total_segundos, distancias