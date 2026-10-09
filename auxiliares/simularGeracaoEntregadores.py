from scipy.stats import qmc

import osmnx as ox
from shapely.geometry import Point
from shapely.geometry import LineString
ox.settings.http_user_agent = "TP1 Algoritmos2 UFMG (raissalgns@ufmg.br)"
ox.settings.use_cache = True
def simulaGeracaoEntregadores(numero_entregadores,restaurante):
    return geraLatitudeLongitudeEntregadores(numero_entregadores,restaurante)
# restaurante tem que ter os campos ["latitude"] e ["longitude"]
def geraLatitudeLongitudeEntregadores(numero_entregadores, restaurante):
    # Gera uma normal 2 variada com média na latitude e longitude do restaurante. A matriz de covariancia a principio vai ser a identidade.
    normal = qmc.MultivariateNormalQMC(mean=[restaurante["longitude"], restaurante["latitude"]], cov=[[0.0001, 0], [0, 0.0001]])
    # X é a longitude e Y a latitude
    # Amostramos dessa normal
    entregadores = normal.random(numero_entregadores)
    return ajustaPosicaoEntregadores(entregadores, restaurante)
def ajustaPosicaoEntregadores(entregadores, restaurante):
    # Vamos usar o grafo que o osmnx nos fornece, vamos carregar o mapa em volta do restaurante num raio de 3km e queremos representações das ruas por isso "drive"
    grafo_mapa = ox.graph_from_xml("data/mapa.osm")
    # Passamos o grafo, e os vetores da latitude e longitude
    # Vamos encontrar a rua(edge) mais proxima e ajustar a posição para lá. (calcular os nearest_vertices(cruzamentos) seria computacionalmente mais barato, se isso demorar podemos mudar)
    arestas_mais_proximas = ox.distance.nearest_edges(grafo_mapa, X=entregadores[:,0], Y=entregadores[:,1])
    entregadores_ajustados = []
    # O metodo nearest_edges nos dá a rua (edge) mas não necessariamente o ponto mais proximo então temos que calcular isso
    for i, (u, v, key) in enumerate(arestas_mais_proximas):
        # Recupera os dados da rua
        dados_da_rua = grafo_mapa.edges[(u, v, key)]
        
        # Cria um Point para cada entregador
        ponto_original = Point(entregadores[i,0], entregadores[i,1])
        
        # Recupera a forma da rua, se for curva é o geometry se não criamos a reta
        if 'geometry' in dados_da_rua:
            linha_da_rua = dados_da_rua['geometry']
        else:
            # Criamos a reta
            ponto_u = Point(grafo_mapa.nodes[u]['x'], grafo_mapa.nodes[u]['y'])
            ponto_v = Point(grafo_mapa.nodes[v]['x'], grafo_mapa.nodes[v]['y'])
            linha_da_rua = LineString([ponto_u, ponto_v])
        
        # Projetamos a posição do entregador na rua. Assim encontrando a sua posição na rua mais proxima
        ponto_projetado = linha_da_rua.interpolate(linha_da_rua.project(ponto_original))
        
        entregadores_ajustados.append({
            "longitude": ponto_projetado.x,
            "latitude": ponto_projetado.y
        })
    return entregadores_ajustados
